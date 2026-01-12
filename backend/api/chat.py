from fastapi import APIRouter, HTTPException
import os
import pandas as pd
from backend.core.schemas import ChatRequest
from backend.core.config import UPLOAD_DIR
from backend.services.csv_service import read_csv_safe
from backend.core.database import get_recent_leads
from backend.services.ml_service import ml_service
from backend.services.analysis_service import AnalysisService

from backend.services.llm_service import chat_with_data

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        context = request.context


        # Enhanced Context Logic: If filename is provided, load and analyze it deeply
        if request.filename:
            file_path = os.path.join(UPLOAD_DIR, request.filename)
            if os.path.exists(file_path):
                try:
                    df = read_csv_safe(file_path)
                    
                    if os.path.exists(file_path):
                        df = read_csv_safe(file_path)
                        # Deep analysis (Slow but detailed)
                        analysis_context = AnalysisService.perform_deep_analysis(df, request.filename)
                    
                    context = f"""
                    {analysis_context}
                    
                    User Provided Context:
                    {request.context}
                    """
                except Exception as e:
                    print(f"Analysis Context Error: {e}")
                    # Fallback to simple context if analysis fails
        
        # Default fallback if no file context
        if not context or len(context) < 10:
             leads = get_recent_leads(100)
             if leads:
                 df = pd.DataFrame(leads)
                 desc = df.describe().to_string()
                 context = f"Recent 100 Leads Summary:\n{desc}"
        
        # Custom Logic for "Top N Leads" (User Request)
        # Check intent: "top X leads", "best leads"
        query_lower = request.message.lower()
        if "top" in query_lower and "lead" in query_lower:
             try:
                 # Ensure we have a dataframe to query
                 df_target = None
                 if 'df' in locals():
                     df_target = df
                 
                 if df_target is None or df_target.empty:
                     # 1. Try Persisted Demo Cache
                     try:
                         import backend.services.prediction_orchestrator as orchestrator
                         if orchestrator.LATEST_ANALYSIS_RESULT:
                             cached_leads = orchestrator.LATEST_ANALYSIS_RESULT.get('results', [])
                             if cached_leads:
                                 df_target = pd.DataFrame(cached_leads)
                                 # Ensure score column logic matches downstream
                                 if 'score' in df_target.columns:
                                     df_target['prediction_score'] = df_target['score']
                     except Exception as e:
                         print(f"Chat Cache Fallback Logic Error: {e}")

                     # 2. Try DB (if cache empty)
                     if df_target is None or df_target.empty:
                         leads = get_recent_leads(100) # Get more context
                         if leads:
                            df_target = pd.DataFrame(leads)
                 
                 if df_target is not None and not df_target.empty:
                     if 'prediction_score' not in df_target.columns and 'score' in df_target.columns:
                         df_target['prediction_score'] = df_target['score']
                     
                     if 'prediction_score' in df_target.columns:
                         # 1. Parse N from query (e.g. "top 10", "top 20")
                         import re
                         # Look for pattern "top X"
                         match = re.search(r"top\s+(\d+)", query_lower)
                         n_leads = 5 # default
                         if match:
                             try:
                                 n_leads = int(match.group(1))
                                 # Cap at reasonably high number to prevent overload
                                 if n_leads > 50: n_leads = 50 
                                 if n_leads < 1: n_leads = 5
                             except:
                                 pass
                         
                         # 2. Sort and Slice
                         df_top = df_target.sort_values(by='prediction_score', ascending=False).head(n_leads)
                         
                         # Format as Markdown Table
                         response_lines = [f"Here are the top {n_leads} leads to focus on:\n\n"]
                         
                         # Table Header
                         response_lines.append("| Rank | Lead ID | Score | Key Insights |")
                         response_lines.append("|---|---|---|---|")
                         
                         idx = 1
                         for _, lead in df_top.iterrows():
                             # Extract details safely
                             lead_id = lead.get('LeadID') or lead.get('LeadID_x') or lead.get('id') or f"#{idx}"
                             score_val = lead.get('prediction_score', 0)
                             score_pct = int(score_val * 100)
                             
                             # Improved Rule-based highlights
                             reasons = []
                             
                             # 0. Primary Source: SHAP Explanation (generated by ML Service)
                             expl = lead.get('explanation')
                             if expl and isinstance(expl, str) and len(expl) > 5 and expl != "No explanation available.":
                                 expl = expl.replace("\n", " ") # Keep single line for table
                                 reasons.append(expl)

                             # 1. TOS
                             try:
                                 tos = float(lead.get('TimeOnSite') or lead.get('TimeSpent') or 0)
                                 if tos > 45: 
                                     reasons.append(f"{int(tos)}s dwell")
                             except: pass
                             
                             # 2. Pages
                             try:
                                 pages = float(lead.get('PagesVisited') or 0)
                                 if pages >= 2:
                                     reasons.append(f"{int(pages)} pages")
                             except: pass
                             
                             # 3. Source
                             src = str(lead.get('Source') or "").strip()
                             if src and src.lower() not in ['unknown', 'nan', 'none', '']:
                                 reasons.append(src)
                                 
                             # 4. Interactions (Meeting/Email)
                             if float(lead.get('MeetingBooked') or 0) > 0:
                                 reasons.append("Meeting Booked")
                             elif float(lead.get('EmailOpened') or 0) > 0:
                                 reasons.append("Email Opened")
                             
                             # 5. Fallback
                             if not reasons:
                                 import random
                                 if score_pct > 90: 
                                     opts = ["High conversion prob.", "Top-tier candidate"]
                                     reasons.append(random.choice(opts))
                                 elif score_pct > 70: 
                                     opts = ["Strong engagement", "Above average potential"]
                                     reasons.append(random.choice(opts))
                                 else: 
                                     reasons.append("Review required")
                             
                             # Join distinct reasons
                             reason_str = ", ".join(reasons[:2]) # Limit to 2 for table compactness
                             
                             # Add row
                             response_lines.append(f"| {idx} | **{lead_id}** | {score_pct}% | {reason_str} |")
                             idx += 1
                             
                         return {"response": "\n".join(response_lines)}
             except Exception as e:
                 print(f"Top Leads Logic Error: {e}")
                 # Fallthrough to LLM
        
        response = chat_with_data(request.message, context)
        return {"response": response}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "I encountered an error analyzing the data."}
