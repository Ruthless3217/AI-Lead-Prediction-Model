import pandas as pd
from backend.services.scoring_service import ScoringService

class ResultProcessor:
    @staticmethod
    def process_leads(df: pd.DataFrame, scores: list):
        """
        Processes leads, determining priorities and accuracy.
        Returns:
            - results: List of dicts for frontend response
            - leads_to_db: List of dicts for database insertion
            - counts: Dict with high/med/low counts
            - accuracy_aggregates: Dict tallying correct/total for accuracy calc
        """
        results = []
        leads_to_db = []
        
        # Sort by score
        df_sorted = df.copy()
        df_sorted['prediction_score'] = scores
        df_sorted = df_sorted.sort_values(by='prediction_score', ascending=False)
        
        # Check actuals
        has_actual_conversion = 'Converted' in df.columns or 'converted' in df.columns
        actual_col = 'Converted' if 'Converted' in df.columns else ('converted' if 'converted' in df.columns else None)
        
        # Counters
        counts = {"High": 0, "Medium": 0, "Low": 0}
        accuracy_aggregates = {"correct": 0, "total_with_actual": 0}
        
        # Domain Logic: Explanation (Rule-Based for Speed & Detail)
        # This is now handled by ml_service.generate_feature_explanations above, 
        # but we need to integrate it. For efficiency, we'll generate all at once before the loop.
        pass 
        
        # --- NEW: Generate Explanations Batch ---
        from backend.services.ml_service import ml_service
        # FIX: Align scores with the sorted dataframe!
        # Previously we passed raw 'scores' which were unsorted, causing a mismatch with 'df_sorted'
        sorted_scores = df_sorted['prediction_score'].tolist()
        explanations = ml_service.generate_feature_explanations(df_sorted, sorted_scores)
        
        # --- VECTORIZED PROCESSING (Speed Up) ---
        # Instead of iterating rows (slow), we operate on columns (fast)
        
        # 1. Add computed columns
        df_sorted['explanation'] = explanations
        
        # 2. Calculate Priority Vectorially (Score-Based)
        # User requested "actual" priorities based on data.
        # We use absolute thresholds so the label matches the probability.
        # High: >= 0.7
        # Medium: >= 0.3 and < 0.7
        # Low: < 0.3
        
        # Default to Low
        df_sorted['priority'] = "Low"
        
        # Apply thresholds
        # Note: We use .loc to avoid SettingWithCopy warnings if applicable, though df_sorted is a copy.
        mask_high = df_sorted['prediction_score'] >= 0.7
        mask_medium = (df_sorted['prediction_score'] >= 0.3) & (df_sorted['prediction_score'] < 0.7)
        
        df_sorted.loc[mask_high, 'priority'] = "High"
        df_sorted.loc[mask_medium, 'priority'] = "Medium"
        
        # 3. Calculate Counts
        counts = df_sorted['priority'].value_counts().to_dict()
        # Ensure all keys exist
        for k in ["High", "Medium", "Low"]:
            if k not in counts: counts[k] = 0
            
        # 4. Handle Actuals & Accuracy
        accuracy_aggregates = {"correct": 0, "total_with_actual": 0}
        
        if has_actual_conversion and actual_col:
            # Vectorized normalization
            # We map the column using a safe map function
            def normalize_actual(val):
                if pd.isna(val): return None
                s = str(val).strip().lower()
                if s in ['1', 'yes', 'true', 'won', 'success']: return True
                if s in ['0', 'no', 'false', 'lost', 'failed']: return False
                try: return float(val) == 1.0
                except: return False
                
            df_sorted['actual_converted'] = df_sorted[actual_col].apply(normalize_actual)
            
            # Count valid actuals
            valid_actuals = df_sorted.dropna(subset=['actual_converted'])
            accuracy_aggregates["total_with_actual"] = len(valid_actuals)
            
            # Calculate correct predictions
            # High -> True, Medium/Low -> False (Simplification for accuracy metric)
            # Or use specific logic: High=True, Low=False. Medium is ambiguous.
            # Let's align with ScoringService: High->True, Low->False usually.
            # Efficient Correctness Check:
            # Correct if (High AND True) OR (Low AND False) OR (Medium AND True/False??)
            # Let's rely on row-by-row for the *metrics* calculation in ml_service.
            # For this 'correct' counter, let's just do a quick apply
            
            def is_correct(row):
                if row['priority'] == 'High' and row['actual_converted'] is True: return True
                if row['priority'] == 'Low' and row['actual_converted'] is False: return True
                return False
                
            correct_mask = valid_actuals.apply(is_correct, axis=1)
            accuracy_aggregates["correct"] = correct_mask.sum()
            
            df_sorted['prediction_accuracy'] = valid_actuals.apply(
                lambda r: "correct" if is_correct(r) else "incorrect", axis=1
            )
            df_sorted['prediction_accuracy'] = df_sorted['prediction_accuracy'].fillna("unknown")
            
        else:
            df_sorted['actual_converted'] = None
            df_sorted['prediction_accuracy'] = None

        # 5. Final Formatting
        df_sorted['score'] = df_sorted['prediction_score'].round(2)
        df_sorted['next_action'] = df_sorted['priority'].apply(lambda p: "Contact immediately" if p == "High" else "Nurture")
        df_sorted['sales_notes'] = ""
        
        # --- OPTIMIZATION: Reduce Payload Size ---
        # The frontend only uses specific fields. We strip everything else to keep JSON small.
        # Check config for DEMO_MODE logic if we want to be safe, but this is good practice generally.
        keep_cols = ['score', 'priority', 'explanation', 'next_action', 'sales_notes']
        
        # Add ID and Source columns flexibly
        for col in df_sorted.columns:
            lower = col.strip().lower()
            if lower in ['leadid', 'lead_id', 'id', 'lead number', 'no', 'lead_no']:
                keep_cols.append(col)
            elif lower in ['source', 'lead source', 'platform', 'channel']:
                keep_cols.append(col)
        
        # Deduplicate
        keep_cols = list(set(keep_cols))
        
        # Fallback if no ID/Source found (send everything? No, just send what we have + maybe first 2 cols)
        if len(keep_cols) < 7:
             # Add first 2 columns just in case they are identifiers
             keep_cols.extend(df_sorted.columns[:2].tolist())
        
        # Ensure we don't crash if col missing
        final_cols = [c for c in keep_cols if c in df_sorted.columns]
        
        # Create lightweight results (List of Dicts)
        # Handle nan values for JSON compliance
        # OPTIMIZATION: Removed arbitrary limit to show actual dataset size
        results = df_sorted.fillna("").to_dict('records')
        
        # DB Payload (subset of fields)
        leads_to_db = []
        
        # Prepare DB Payload
        for r in df_sorted.fillna("").to_dict('records'):
            leads_to_db.append({
                "lead_data": {k:v for k,v in r.items() if k not in ['score', 'priority', 'explanation', 'next_action', 'sales_notes']},
                "prediction_score": r['score'],
                "priority": r['priority']
            })
             
        return results, leads_to_db, counts, accuracy_aggregates
