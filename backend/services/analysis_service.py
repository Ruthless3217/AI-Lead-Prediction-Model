import pandas as pd
from backend.services.ml_service import ml_service

class AnalysisService:
    @staticmethod
    def perform_deep_analysis(df: pd.DataFrame, filename: str) -> str:
        """
        Generates a deep analysis context string from a DataFrame.
        Includes basic stats, correlations, categorical breakdowns, and lead scoring context.
        """
        try:
             # 1. Basic Stats
            desc = df.describe().to_string()
            
            # 2. Correlations (Numerical)
            numeric_df = df.select_dtypes(include=['number'])
            correlations = ""
            if not numeric_df.empty:
                 corr_matrix = numeric_df.corr()
                 # Find strong correlations (> 0.5)
                 strong_pairs = []
                 for i in range(len(corr_matrix.columns)):
                     for j in range(i):
                         if abs(corr_matrix.iloc[i, j]) > 0.5:
                             strong_pairs.append(f"{corr_matrix.columns[i]} vs {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.2f}")
                 if strong_pairs:
                     correlations = "Strong Correlations:\n" + "\n".join(strong_pairs)
            
            # 3. Categorical Counts (Top 5)
            cat_analysis = ""
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if col != 'filename': 
                     counts = df[col].value_counts().head(5).to_dict()
                     cat_analysis += f"\nTop 5 {col}: {counts}"

            # 4. Get Lead Data with Predictions (if available)
            lead_data_context = ""
            try:
                # Attempt to get predictions if they've been run
                if ml_service:
                    scores, _, _ = ml_service.predict_score(df)
                    df['prediction_score'] = scores
                    
                    # Sort by score and get top 20 for context
                    df_sorted = df.sort_values(by='prediction_score', ascending=False)
                    top_leads = df_sorted.head(20)
                    
                    # Format lead data as a table
                    lead_data_context = "\n\nTOP 20 LEADS (by prediction score):\n"
                    lead_data_context += "=" * 80 + "\n"
                    
                    for idx, (_, row) in enumerate(top_leads.iterrows(), 1):
                        lead_data_context += f"\nLead #{idx}:\n"
                        lead_data_context += f"  Score: {row.get('prediction_score', 0):.3f}\n"
                        
                        # Include key fields
                        key_fields = ['Source', 'Company', 'Lead Number', 'Lead Origin', 
                                     'TimeOnSite', 'PagesVisited', 'EmailOpened', 
                                     'MeetingBooked', 'EngagementScore', 'InteractionCount']
                        
                        for field in key_fields:
                            if field in row.index and pd.notna(row[field]):
                                lead_data_context += f"  {field}: {row[field]}\n"
                        
                        lead_data_context += "-" * 40 + "\n"
            except Exception as e:
                # print(f"Lead data extraction error: {e}")
                lead_data_context = "\n(Lead-level data not available - run predictions first)"

            # Assemble Deep Context
            context = f"""
            DEEP DATA ANALYSIS for '{filename}':
            
            Shape: {df.shape[0]} rows, {df.shape[1]} columns.
            
            Numeric Summary:
            {desc}
            
            {correlations}
            
            Categorical Breakdown:
            {cat_analysis}
            {lead_data_context}
            """
            return context
            
        except Exception as e:
            print(f"Deep Analysis Error: {e}")
            return f"Error performing analysis: {str(e)}"
