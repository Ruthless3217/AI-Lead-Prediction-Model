from fastapi import APIRouter, HTTPException
import os
from backend.core.schemas import PredictRequest
from backend.core.config import UPLOAD_DIR
from backend.services.csv_service import read_csv_safe
from backend.services.prediction_orchestrator import orchestrate_prediction
from backend.services.ml_service import ml_service
from backend.services.explainability_service import ExplainabilityService

router = APIRouter()

@router.post("/predict")
async def predict_leads(request: PredictRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:


        df = read_csv_safe(file_path)
        df = df.fillna(0)
        
        if not ml_service:
             raise HTTPException(status_code=503, detail="ML Service unavailable")

        result = orchestrate_prediction(df, request.filename)
        
        # 3. Explainability (Optional)
        if request.explain and ml_service.get_model():
            # Explain the top lead (highest score)
            if result.get("results"):
                 # Assuming results are sorted by score desc in orchestrator
                 top_lead = result["results"][0]
                 # Reconstruct DataFrame row for this lead
                 # Note: We need the processed features corresponding to this lead.
                 # Since preprocessing happens inside MLS, we might need a workaround.
                 # For now, we reuse the input DF logic, but strictly this requires
                 # exactly the same features.
                 
                 # Simplification: pass full DF and pick top row
                 try:
                    df_sorted = df.copy()
                    # We need the scores to sort same way
                    scores = list(df_sorted['prediction_score']) if 'prediction_score' in df_sorted else ml_service.predict_score(df_sorted)[0]
                    df_sorted['__temp_score'] = scores
                    df_sorted = df_sorted.sort_values(by='__temp_score', ascending=False).drop(columns=['__temp_score'])
                    
                    # Preprocess just this row to match model features
                    features = ml_service.get_features()
                    processed_row = ml_service.preprocess(df_sorted.head(1), training=False)
                    # Ensure columns match
                    for f in features:
                        if f not in processed_row.columns: processed_row[f] = 0
                    processed_row = processed_row[features]
                    
                    explanation_image = ExplainabilityService.explain_prediction(processed_row, features)
                    result["explanation_image"] = explanation_image
                 except Exception as e:
                     print(f"Explain failed: {e}")

        return result
        
    except Exception as e:
        print(f"Orchestration Error: {e}")
        import traceback
        traceback.print_exc()
        # Return more detailed error message to frontend
        error_detail = str(e)
        if "feature names" in error_detail.lower():
            error_detail = "The uploaded file has different columns than the training data. Please retrain the model with this file first."
        raise HTTPException(status_code=500, detail=error_detail)
 
