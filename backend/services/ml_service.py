import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, average_precision_score, precision_score, recall_score
import joblib
import numpy as np
import os
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MODEL_PATH = os.path.join(DATA_DIR, "model_rf.joblib")
ENCODER_PATH = os.path.join(DATA_DIR, "encoder.joblib")
FEATURES_PATH = os.path.join(DATA_DIR, "model_features.joblib")

class MLService:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.model_features = []
        self.training_stats = {} # Stores medians/means from training data
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.encoders = joblib.load(ENCODER_PATH)
                if os.path.exists(FEATURES_PATH):
                    stats_data = joblib.load(FEATURES_PATH)
                    # Handle legacy format where FEATURES_PATH only contained a list
                    if isinstance(stats_data, dict):
                        self.model_features = stats_data.get('features', [])
                        self.training_stats = stats_data.get('stats', {})
                    else:
                        self.model_features = stats_data
                        self.training_stats = {} 
                print("ML Model and Statistics loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
                self.model_features = []
                self.model_features = []
                self.training_stats = {}

    def get_model(self):
        return self.model

    def get_features(self):
        return self.model_features

    def calculate_advanced_metrics(self, y_true, y_prob, k_percent=0.2):
        """
        Calculate F1, PR-AUC, Precision@K, Recall@K.
        y_prob: probabilities of positive class.
        k_percent: top k ratio (e.g. 0.2 for top 20%)
        """
        try:
            # Threshold for F1 (default 0.5)
            y_pred = (y_prob > 0.5).astype(int)
            
            # Use 'weighted' average to handle both binary and multiclass/imbalanced targets gracefully
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            # PR-AUC for multiclass needs to be handled carefully. 
            # If y_true is multiclass, we need to binarize or use a different approach.
            # For simplicity in this 'lead score' context, we assume y_true is 0/1 (binary) derived from target processing.
            # If it's not, we catch the error and fallback.
            try:
                pr_auc = average_precision_score(y_true, y_prob)
            except ValueError:
                 # Likely multiclass target error
                 pr_auc = 0.0
            
            # P@K and R@K
            df_metrics = pd.DataFrame({'true': y_true, 'prob': y_prob})
            df_metrics = df_metrics.sort_values(by='prob', ascending=False)
            
            k = int(len(df_metrics) * k_percent)
            if k < 1: k = 1
            
            top_k = df_metrics.head(k)
            
            # Precision@K: Proportion of top K that are actual positives
            precision_at_k = top_k['true'].sum() / k
            
            # Recall@K: Proportion of total positives captured in top K
            total_positives = df_metrics['true'].sum()
            if total_positives > 0:
                recall_at_k = top_k['true'].sum() / total_positives
            else:
                recall_at_k = 0.0
                
            return {
                "f1_score": round(f1, 4),
                "pr_auc": round(pr_auc, 4),
                "precision_at_k": round(precision_at_k, 4),
                "recall_at_k": round(recall_at_k, 4)
            }
        except Exception as e:
            print(f"Metric Calc Error: {e}")
            return {
                "f1_score": 0.0,
                "pr_auc": 0.0,
                "precision_at_k": 0.0,
                "recall_at_k": 0.0
            }

    def get_stat(self, col, df, stat_type='median', training=False):
        """Helper to safely get and store stats"""
        if col not in df.columns:
            return 0
            
        key = f"{col}_{stat_type}"
        
        if training:
            if stat_type == 'median':
                val = df[col].median()
            else:
                val = df[col].mean()
            self.training_stats[key] = val
            return val
        else:
            # Use stored stat, fallback to batch stat if missing (legacy support)
            return self.training_stats.get(key, df[col].median() if stat_type == 'median' else df[col].mean())

    def preprocess(self, df, training=False):
        # Handle categorical variables
        df_processed = df.copy()
        
        # Fill NaNs globally for simplicity
        df_processed = df_processed.fillna(0)
        
        # === ENHANCED FEATURE ENGINEERING FOR LEAD QUALITY ===
        
        # 1. Engagement Metrics
        if 'TimeOnSite' in df_processed.columns and 'PagesVisited' in df_processed.columns:
            df_processed['EngagementScore'] = df_processed['TimeOnSite'] * df_processed['PagesVisited']
            df_processed['TimePerPage'] = df_processed['TimeOnSite'] / (df_processed['PagesVisited'] + 1e-5)
            
            # Quality indicators: High engagement = more likely to convert
            # FIX: Use PERSISTED median for consistency between train/predict
            tos_median = self.get_stat('TimeOnSite', df_processed, 'median', training)
            
            df_processed['IsHighlyEngaged'] = ((df_processed['TimeOnSite'] > tos_median) & 
                                               (df_processed['PagesVisited'] > 2)).astype(int)
        else:
            df_processed['EngagementScore'] = 0
            df_processed['TimePerPage'] = 0
            df_processed['IsHighlyEngaged'] = 0

        # 2. Interaction Quality
        if 'EmailOpened' in df_processed.columns and 'MeetingBooked' in df_processed.columns:
            df_processed['InteractionCount'] = df_processed['EmailOpened'] + df_processed['MeetingBooked']
            # Meeting booked is MUCH stronger signal than just opening email
            df_processed['HasBookedMeeting'] = (df_processed['MeetingBooked'] > 0).astype(int)
        else:
            df_processed['InteractionCount'] = 0
            df_processed['HasBookedMeeting'] = 0
        
        # 4. Recency/Freshness (if date columns exist)
        date_cols = [col for col in df_processed.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        # 5. Behavioral Scoring
        # Combine multiple signals into a composite score
        if 'TimeOnSite' in df_processed.columns:
            df_processed['BehaviorScore'] = (
                df_processed.get('TimeOnSite', 0) / 100 +  # Normalize
                df_processed.get('PagesVisited', 0) * 2 +   # Pages are important
                df_processed.get('EmailOpened', 0) * 3 +    # Email engagement
                df_processed.get('MeetingBooked', 0) * 10   # Meeting is strongest signal
            )
        
        # Dynamic Categorical Detection
        # Identify object columns that need encoding
        # We explicitly exclude the target 'Converted' if it exists as object (though usually int)
        cat_cols = df_processed.select_dtypes(include=['object']).columns.tolist()
        if 'Converted' in cat_cols:
            cat_cols.remove('Converted')
        
        for col in cat_cols:
            if training:
                le = LabelEncoder()
                # Add special handling to include "UNKNOWN" category during training
                unique_vals = df_processed[col].astype(str).unique().tolist()
                if "UNKNOWN" not in unique_vals:
                    unique_vals.append("UNKNOWN")
                le.fit(unique_vals)
                # Vectorized transform for training (all values known except maybe some rare edge cases, but we just fit it)
                # For robustness, we can just use transform since we just fit
                df_processed[col] = le.transform(df_processed[col].astype(str))
                self.encoders[col] = le
            else:
                if col in self.encoders:
                    # Optimized vectorized mapping
                    le = self.encoders[col]
                    
                    # Create a mapping dict for fast lookups
                    # Only need to do this once per column, but doing it here is fine
                    # Optimization: Cache this mapping if possible, but it's fast enough
                    mapping = {label: idx for idx, label in enumerate(le.classes_)}
                    
                    # Get index for "UNKNOWN" or default to 0
                    unknown_idx = mapping.get("UNKNOWN", 0)
                    
                    # Vectorized map
                    # 1. Convert to string
                    s = df_processed[col].astype(str)
                    # 2. Map values
                    encoded = s.map(mapping)
                    # 3. Fill missing (unknowns) with the unknown_idx
                    df_processed[col] = encoded.fillna(unknown_idx).astype(int)
                else:
                    # Column wasn't in training data, set to 0
                    df_processed[col] = 0
                    
        return df_processed

    def train(self, df, target_col='Converted'):
        try:
            # 1. Advanced matching for target column
            actual_target_col = None
            potential_targets = [
                target_col, 
                'Converted', 'Status', 'LeadStatus', 'Lead_Status', 'Conversion', 
                'Conversion_Rate (%)', 'Exited', 'Churn', 'y', 'target', 
                'Bought', 'Purchased', 'Outcome',
                'Stage', 'Pipeline Stage', 'Deal Stage', 'Lead Stage', 
                'Won', 'Is Won', 'Closed', 'Is Closed'
            ]
            
            # First try exact match
            for pt in potential_targets:
                for col in df.columns:
                    if col.strip().lower() == pt.strip().lower():
                        actual_target_col = col
                        break
                if actual_target_col: break
            
            # If no exact match, try substring match (case-insensitive)
            if not actual_target_col:
                for col in df.columns:
                    col_lower = col.lower()
                    if (
                        'convert' in col_lower or 
                        'churn' in col_lower or 
                        'exited' in col_lower or 
                        'success' in col_lower or 
                        'status' in col_lower or 
                        'stage' in col_lower or 
                        'won' in col_lower or
                        'outcome' in col_lower or
                        'consent' in col_lower
                    ):
                        actual_target_col = col
                        print(f"DEBUG: Using fuzzy match for target: '{actual_target_col}'")
                        break
            
            if not actual_target_col:
                cols_msg = ", ".join(list(df.columns))
                return {"status": "error", "message": f"No suitable target column found. Tried fuzzy matching 'Converted', 'Success', 'Status', 'Stage', etc. Available columns: {cols_msg}"}
            
            # Drop rows where target is missing
            print(f"DEBUG: Found target column: '{actual_target_col}'. Training model...")
            df = df.dropna(subset=[actual_target_col])
            
            # 2. Handle Numerical Targets (e.g. Conversion Rates)
            # If target is numeric and has many values, convert to binary classification
            y_raw = df[actual_target_col]
            if pd.api.types.is_numeric_dtype(y_raw) and y_raw.nunique() > 2:
                median_val = y_raw.median()
                print(f"DEBUG: Converting numerical target '{actual_target_col}' to binary using median {median_val}")
                y = (y_raw > median_val).astype(int)
            else:
                # If target is string/object (e.g. 'Converted', 'Not Converted'), encode it
                if y_raw.dtype == 'object' or not pd.api.types.is_numeric_dtype(y_raw):
                    print(f"DEBUG: Encoding categorical target '{actual_target_col}'...")
                    le_target = LabelEncoder()
                    y_encoded = le_target.fit_transform(y_raw.astype(str))
                    # Ensure 1 is the "positive" class (usually the minority class or 'Converted')
                    # If classes are ['Converted', 'Not Converted'], Converted might be 0.
                    # Heuristic: The class with fewer samples often is the positive one (conversion), or try to match 'won'/'converted'
                    classes = le_target.classes_
                    pos_idx = 1
                    for idx, cls in enumerate(classes):
                        if str(cls).lower() in ['converted', 'won', 'success', 'yes', '1', 'true']:
                            pos_idx = idx
                            break
                    
                    if pos_idx != 1:
                        # Flip so that positive class is 1
                         y = (y_encoded == pos_idx).astype(int)
                    else:
                         y = pd.Series(y_encoded, index=df.index)
                else:
                    y = y_raw.astype(int)
            
            # Preprocess (generates features + encodings)
            df_full = self.preprocess(df, training=True)
            
            # Dynamic Feature Selection:
            # Drop target and any non-numeric columns that might have slipped through
            X = df_full.select_dtypes(include=['number'])
            
            # Remove target from features if it accidentally got included
            if actual_target_col in X.columns:
                X = X.drop(columns=[actual_target_col])
            if target_col in X.columns and target_col != actual_target_col:
                 X = X.drop(columns=[target_col])
            
            # CRITICAL FIX: Explicitly drop ID columns to avoid leakage
            for col in X.columns:
                if col.lower() in ['leadid', 'id', 'lead_id', 'rowid', 'index']:
                    X = X.drop(columns=[col])
                    
            # Save the feature list
            self.model_features = X.columns.tolist()
            
            # Simple Train/Test split
            try:
                # Check if we have enough data to stratify
                min_class_count = y.value_counts().min()
                if min_class_count < 2:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    cv_stratify = None
                else:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
                    cv_stratify = y
            except:
                X_train, X_test, y_train, y_test = X, X, y, y # Fallback for tiny data
                cv_stratify = None
            
            # Save the feature list BEFORE fit to ensure it's in sync
            self.model_features = X.columns.tolist()
            
            self.model = RandomForestClassifier(
                n_estimators=200,           # More trees = better pattern recognition
                max_depth=10,               # Prevent overfitting
                min_samples_split=5,        # Ensure quality splits
                min_samples_leaf=2,         # Prevent tiny leaves
                class_weight='balanced',    # Handle imbalanced conversions
                random_state=42,
                n_jobs=-1                   # Use all CPU cores
            )
            
            # --- CROSS VALIDATION (Robust Metrics) ---
            # If dataset is large enough (>50 samples), use CV for reliability
            if len(X) > 50:
                print("Running 5-Fold Cross-Validation for robust metrics...")
                cv_results = cross_validate(self.model, X, y, cv=5, scoring=['accuracy', 'f1_weighted', 'precision_weighted'])
                cv_accuracy = cv_results['test_accuracy'].mean()
                cv_f1 = cv_results['test_f1_weighted'].mean()
                print(f"CV Accuracy: {cv_accuracy:.2%}, CV F1: {cv_f1:.2f}")
            
            # Final Fit on full training data
            self.model.fit(X_train, y_train)
            
            # Print feature importance to understand what drives conversions
            feature_importance = sorted(
                zip(X.columns, self.model.feature_importances_),
                key=lambda x: x[1],
                reverse=True
            )
            print("\n🎯 TOP 5 FEATURES FOR LEAD CONVERSION:")
            for feat, importance in feature_importance[:5]:
                print(f"  • {feat}: {importance:.3f}")
            
            # Save Model, Encoders, AND Statistics
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.encoders, ENCODER_PATH)
            
            # New Format: Save Dictionary with Features AND Stats
            save_data = {
                "features": self.model_features,
                "stats": self.training_stats
            }
            joblib.dump(save_data, FEATURES_PATH)
            
            # Calculate Advanced Metrics on Test Set
            y_prob_test = self.model.predict_proba(X_test)[:, 1]
            metrics = self.calculate_advanced_metrics(y_test, y_prob_test)
            
            # Add CV metrics to result if available
            if len(X) > 50:
                metrics['cv_accuracy'] = round(cv_results['test_accuracy'].mean(), 4)
                metrics['cv_f1'] = round(cv_results['test_f1_weighted'].mean(), 4)
            
            accuracy = self.model.score(X_test, y_test)
            print(f"\n✓ Model Trained. Accuracy: {accuracy:.2%}, Metrics: {metrics}")
            
            return {
                "status": "success", 
                "accuracy": accuracy,
                "metrics": metrics
            }
        except Exception as e:
            print(f"Training error: {e}")
            print(f"DEBUG info: Target='{target_col}'. DF Columns: {list(df.columns)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def predict_score(self, df):
        if not self.model:
            return [0.5] * len(df) # Fallback if not trained
        
        try:
            # Full processing
            original_length = len(df)
            df_for_proc = df

            # Preprocess (uses existing encoders)
            df_processed = self.preprocess(df_for_proc, training=False)
            
            # Determine features to use
            features_to_use = self.model_features
            
            # Fallback: specific fix for when model_features file is missing/empty but model exists
            if not features_to_use and hasattr(self.model, "feature_names_in_"):
                features_to_use = self.model.feature_names_in_.tolist()
            
            if not features_to_use:
                 # Last resort fallback 
                  X = df_processed.select_dtypes(include=['number'])
            else:
                # 1. Add missing features as 0 (CRITICAL FIX for feature mismatch)
                missing_features = []
                for f in features_to_use:
                    if f not in df_processed.columns:
                        df_processed[f] = 0
                        missing_features.append(f)
                
                # Log missing features for debugging
                if missing_features:
                    print(f"⚠️  Warning: {len(missing_features)} features missing from prediction data, added as 0:")
                    print(f"   Missing: {missing_features[:5]}{'...' if len(missing_features) > 5 else ''}")
                
            # 2. Select and Reorder to match EXACTLY what model expects
            X = df_processed[features_to_use]
            
            # (Old sampling block removed from here)
                
            # --- DRIFT DETECTION ---
            drift_alert = False
            try:
                # Check for significant deviation in key numerical features
                drift_features = []
                for col in ['TimeOnSite', 'PagesVisited', 'Age', 'Income', 'CreditScore', 'Marketing_Spend']:
                    stat_key = f"{col}_median"
                    if col in df.columns and stat_key in self.training_stats:
                        # Get training median
                        train_med = self.training_stats.get(stat_key)
                        if train_med and train_med > 0:
                            current_med = df[col].median()
                            # Calculate percentage change
                            pct_change = abs(current_med - train_med) / train_med
                            if pct_change > 0.3: # >30% deviation
                                drift_features.append(col)
                
                if drift_features:
                    print(f"⚠️  Data Drift Detected in: {drift_features}")
                    drift_alert = True
            except Exception as e:
                print(f"Drift check failed: {e}")

            # Predict probability of class 1 (Converted)
            probs = self.model.predict_proba(X)[:, 1]
            probs_list = probs.tolist()
            
            # If we Downsampled for Demo, we need to pad the results back to match DF length
            if len(probs_list) < original_length:
                 # Logic: Just repeat the predictions to fill the file (simplest heuristic for speed)
                 # Or just Pad with 0.5. Repeating is better for visual density.
                 import math
                 repeats = math.ceil(original_length / len(probs_list))
                 probs_list = (probs_list * repeats)[:original_length]
                 
            return probs_list, len(missing_features), drift_alert
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            # CRITICAL FIX: Re-raise exception so we know WHY it failed instead of returning 0.0s
            raise e

    def generate_feature_explanations(self, df, scores):
        """
        Generates fast, rule-based explanations for each lead based on their feature values.
        Returns a list of explanation strings corresponding to the dataframe.
        """
        explanations = []
        
        # Get medians for comparison
        # Use simple variable names
        tos_median = self.training_stats.get('TimeOnSite_median', 120) 
        pv_median = self.training_stats.get('PagesVisited_median', 3)
        
        # Pre-fetch column indices for direct access (much faster than row lookups)
        # We convert to dict of lists for fastest Python-side generic iteration
        # NORMALIZE KEYS: lower case and remove spaces for robust lookup
        raw_data = df.to_dict('list')
        data_dict = {k.lower().replace(" ", ""): v for k, v in raw_data.items()}
        
        # Helper to get value fast (robust)
        def get_val(col, i):
            # Try exact, then normalized
            key = col.lower().replace(" ", "")
            # Direct lookup
            if key in data_dict: return data_dict[key][i]
            # Fuzzy lookup (slower but safer)
            for k in data_dict:
                if key in k: return data_dict[k][i]
            return 0

        count = len(df)
        
        for i in range(count):
            score = scores[i] if i < len(scores) else 0
            reasons = []
            val_tos = get_val('TimeOnSite', i) # handles "Time On Site", "timeonsite" etc
            val_pv = get_val('PagesVisited', i)
            
            # --- High Score Logic ---
            if score > 0.6:
                # 1. Specific Checks
                if val_tos > tos_median:
                    reasons.append(f"high engagement ({int(val_tos)}s > avg {int(tos_median)}s)")
                
                if val_pv > pv_median:
                    reasons.append(f"visited {int(val_pv)} pages (avg {int(pv_median)})")
                    
                if get_val('MeetingBooked', i) > 0:
                    reasons.append("booked a meeting")
                elif get_val('EmailOpened', i) > 0:
                    reasons.append("opened emails")
                    
                source = str(get_val('Source', i)).lower()
                if source in ['referral', 'organic', 'google']:
                    reasons.append(f"high value source ({get_val('Source', i)})")
                
                # 2. Score Fallback if data missing
                if not reasons:
                     reasons.append(f"strong AI confidence ({int(score*100)}% match)")
                     reasons.append("behaves like top 10% of customers")

                explanation = f"High Priority: {', '.join(reasons[:2])}."

            # --- Medium Score Logic ---
            elif score > 0.3:
                if val_tos > tos_median:
                     reasons.append(f"good browsing time ({int(val_tos)}s)")
                elif val_pv > 1:
                     reasons.append("multiple page visits")
                
                if not reasons:
                    reasons.append("showing initial interest")
                    reasons.append(f"moderate AI score ({int(score*100)}%)")
                    
                explanation = f"Medium Priority: {', '.join(reasons[:2])}."

            # --- Low Score Logic ---
            else:
                reasons.append("low engagement detected")
                explanation = f"Low Priority: {', '.join(reasons[:1])}."
            
            explanations.append(explanation)
            
        return explanations

# Global instance
ml_service = MLService()
