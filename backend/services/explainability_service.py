import shap
import matplotlib.pyplot as plt
import os
import io
import base64
from backend.services.ml_service import ml_service
import numpy as np

# Configure matplotlib for non-interactive backend
plt.switch_backend('Agg')

class ExplainabilityService:
    @staticmethod
    def generate_global_importance(filename_prefix: str = "shap"):
        """
        Generates a global feature importance plot using SHAP.
        Returns: Base64 string of the image.
        """
        model = ml_service.get_model()
        features = ml_service.get_features()
        
        if not model or not features:
             return None

        try:
            # We need a background dataset. Since we don't store X_train raw,
            # we can't do deep SHAP easily without data. 
            # TreeExplainer works with Tree models.
            explainer = shap.TreeExplainer(model)
            
            # Since we don't have X, we can't plot global importance dynamically 
            # without input data.
            # Workaround: Use Feature Importance from Tree (fallback)
            # or require X input for this method.
            
            # BETTER APPROACH: Plot summary for a given dataset input.
            return None
        except Exception as e:
            print(f"SHAP Init Error: {e}")
            return None

    @staticmethod
    def explain_prediction(df_row, features_list):
        """
        Generates a force plot or waterfall plot for a single prediction.
        Returns base64 image.
        """
        model = ml_service.get_model()
        if not model:
            return None

        try:
            # Ensure input matches feature list
            X_input = df_row[features_list]
            
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_input)
            
            # For binary classification, shap_values is a list [class0, class1]
            if isinstance(shap_values, list):
                shap_val = shap_values[1][0] # Positive class, single sample
            else:
                shap_val = shap_values[0]

            expected_value = explainer.expected_value
            if isinstance(expected_value, np.ndarray) or isinstance(expected_value, list):
                 expected_value = expected_value[1] # Positive class

            # Generate Plot
            plt.figure()
            shap.waterfall_plot(shap.Explanation(values=shap_val, 
                                                 base_values=expected_value, 
                                                 data=X_input.iloc[0], 
                                                 feature_names=features_list),
                                show=False)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"SHAP Explainer Error: {e}")
            import traceback
            traceback.print_exc()
            return None
