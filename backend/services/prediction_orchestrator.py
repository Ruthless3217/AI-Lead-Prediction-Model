import pandas as pd
from backend.services.ml_service import ml_service
from backend.services.result_processor import ResultProcessor
from backend.core.database import save_leads_batch, save_prediction_run, create_notification
from backend.services.cache_service import cache_service, compute_file_hash
from backend.core.config import UPLOAD_DIR
import os




# Global to hold latest result for immediate chat access
LATEST_ANALYSIS_RESULT = None

def orchestrate_prediction(df: pd.DataFrame, filename: str):
    """
    Orchestrates the prediction flow:
    """
    global LATEST_ANALYSIS_RESULT

    # 0. Check Robust Cache first (Redis/Memory)
    try:
        full_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(full_path):
            file_hash = compute_file_hash(full_path)
            cache_key = f"prediction:{file_hash}"
            
            cached_result = cache_service.get(cache_key)
            if cached_result:
                print(f"✅ CACHE HIT: Returning cached analysis for {filename}")
                LATEST_ANALYSIS_RESULT = cached_result
                return cached_result
        else:
             file_hash = f"missing_{filename}"
             cache_key = f"prediction:{file_hash}"
    except Exception as e:
        print(f"Cache lookup failed: {e}")
        cache_key = None



    if not ml_service:
        raise Exception("ML Service unavailable")

    # 1. Get ML Scores (Vectorized - Fast)
    scores, missing_feature_count, drift_alert = ml_service.predict_score(df)
    
    # 2. Process Results (Vectorized - Instant)
    results, leads_to_db, counts, accuracy_agg = ResultProcessor.process_leads(df, scores)

    # 3. Advanced Metrics Calculation
    overall_accuracy = 0.0
    if accuracy_agg["total_with_actual"] > 0:
        overall_accuracy = round(accuracy_agg["correct"] / accuracy_agg["total_with_actual"], 4)
        
    calculated_accuracy = None
    advanced_metrics = {}
    
    # --- ORIGINAL HEAVY PATH ---
    # Check for target column (case-insensitive) for advanced metrics
    target_col_for_metrics = None
    for col in df.columns:
        if col.lower() in ['converted', 'status', 'lead_status', 'outcome', 'target']:
            target_col_for_metrics = col
            break
            
    if target_col_for_metrics:
        try:
            y_true = df[target_col_for_metrics]
            if y_true.dtype == 'object':
                 y_true = (y_true.astype(str).str.lower() == 'converted').astype(int) 
            
            # Reconstruct scores series aligned with df
            y_prob = pd.Series(scores, index=df.index)
            
            advanced_metrics = ml_service.calculate_advanced_metrics(y_true, y_prob)
            calculated_accuracy = advanced_metrics.get('f1_score', 0)
        except Exception as e:
            print(f"Error calculating advanced metrics: {e}")

    # 4. Persistence
    # Save the RUN metadata (lightweight) so it appears in history
    # Save the RUN metadata (lightweight) so it appears in history
    # Use actual dataframe length for total, not the truncated results length
    total_count = len(df)
    run_id = save_prediction_run(
        filename=filename,
        total_leads=total_count,
        high_count=counts["High"],
        medium_count=counts["Medium"],
        low_count=counts["Low"],
        accuracy=calculated_accuracy if calculated_accuracy is not None else overall_accuracy,
        has_actual_data=accuracy_agg["total_with_actual"] > 0,
        metrics=advanced_metrics
    )
    
    if run_id:
        # HEAVY WRITE: Save every single lead to DB
        for item in leads_to_db:
            item['run_id'] = run_id
        save_leads_batch(leads_to_db)
        
    # 5. Notification
    create_notification(
        "success", 
        f"Analysis complete for {filename}. {counts['High']} high priority leads found."
    )
    
    final_result = {
        "run_id": run_id,
        "filename": filename,
        "results": results,
        "has_actual_data": accuracy_agg["total_with_actual"] > 0,
        "missing_feature_count": missing_feature_count,
        "drift_alert": drift_alert,
        "distribution": counts,
        "accuracy_metrics": {
            "overall_accuracy": overall_accuracy,
            "total_predictions": total_count,
            "with_actual_data": accuracy_agg["total_with_actual"],
            "f1": advanced_metrics.get("f1_score"),
            "auprc": advanced_metrics.get("pr_auc"),
            "precision_k": advanced_metrics.get("precision_at_k"),
            "recall_k": advanced_metrics.get("recall_at_k")
        } if accuracy_agg["total_with_actual"] > 0 else None
    }
    
    # Update global latest for LLM access
    
    # Update global latest for LLM access
    LATEST_ANALYSIS_RESULT = final_result
    
    # Save to Cache
    if cache_key:
        cache_service.set(cache_key, final_result, ttl=3600)
    
    return final_result
