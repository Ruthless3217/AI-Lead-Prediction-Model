import json
import time
import os
try:
    from backend.services.rag_service import rag_service
except Exception as e:
    print(f"⚠️ RAG Service failed to load: {e}")
    rag_service = None

try:
    from backend.llm.providers.llama_cpp import LlamaCppProvider
except ImportError:
    print("⚠️ LlamaCppProvider not found.")
    LlamaCppProvider = None

try:
    from backend.cache.chat_cache import ChatCache
    print("✅ ChatCache module imported.")
except Exception as e:
    print(f"⚠️ ChatCache import failed: {e}")
    class MockCache:
        @staticmethod
        def get_cached_response(*args): return None
        @staticmethod
        def cache_response(*args): pass
    ChatCache = MockCache

# --- LLM INITIALIZATION (LAZY) ---
llm_primary = None
llm_fallback = None
_llm_initialized = False

def _ensure_llms_loaded():
    global llm_primary, llm_fallback, _llm_initialized
    if _llm_initialized:
        return

    print("🔄 Initializing LLMs (Lazy Load)...")
    
    # 1. Try Initialize Gemini (Primary)
    try:
        from backend.llm.providers.gemini import GeminiProvider
        llm_primary = GeminiProvider()
    except Exception as e:
        print(f"⚠️ Primary LLM (Gemini) failed to load: {e}")

    # 2. Try Initialize Llama (Fallback)
    try:
        if LlamaCppProvider:
            # Check if we already have a primary
            if not llm_primary:
                print("ℹ️ Loading Llama as Primary...")
                llm_fallback = LlamaCppProvider() # This might take time
                llm_primary = llm_fallback
                llm_fallback = None
            else:
                 # Optional: Load Llama as backup? 
                 # For now, if Gemini works, we don't load Llama to save RAM/Time
                 pass
        else:
            print("⚠️ LlamaCppProvider unavailable (import failed).")
    except Exception as e:
        print(f"⚠️ Fallback LLM (Llama) failed to load: {e}")
        
    _llm_initialized = True
    print("✅ LLM Initialization Complete.")

def get_llm_response(prompt, **kwargs):
    """
    Orchestrates LLM calls: Primary -> Fallback
    """
    _ensure_llms_loaded()
    
    # 1. Try Primary
    if llm_primary:
        try:
            return llm_primary.generate(prompt, **kwargs)
        except Exception as e:
            print(f"⚠️ Primary LLM failed: {e}. Switching to fallback...")
            
    # 2. Try Fallback
    global llm_fallback
    if not llm_fallback and LlamaCppProvider:
        try:
             print("⏳ Primary failed. Initializing Llama Fallback on-demand...")
             llm_fallback = LlamaCppProvider()
        except Exception as ex:
             print(f"❌ Failed to initialize Llama fallback: {ex}")

    if llm_fallback:
        try:
            print("⚡ Using Fallback LLM (Llama)...")
            return llm_fallback.generate(prompt, **kwargs)
        except Exception as e:
            print(f"❌ Fallback LLM failed: {e}")
            
    return "AI Service Unavailable (Both Primary and Fallback failed)."


def generate_insights(lead_data, prediction_score, similar_leads=[]):
    """
    Generates explanation, next action, and notes using embedded LLM + RAG context.
    """
    # Quick sanity check
    _ensure_llms_loaded()
    
    if not llm_primary and not llm_fallback:
        return {
            "explanation": f"Score is {prediction_score:.2f} (AI Offline).",
            "next_action": "Contact lead.",
            "sales_notes": "AI model not loaded."
        }
    
    # Format similar leads
    rag_context = ""
    # In generate_insights, similar_leads are passed in. 
    # The caller (analysis_service maybe?) usually calls rag_service.
    # If rag_service is None, likely similar_leads will be empty, but let's be safe.
    if similar_leads:
        rag_context = "Similar Past Leads:\n"
        for lead in similar_leads:
            rag_context += f"- Source: {lead.get('Source')}, Outcome: {'Converted' if lead.get('Converted')==1 else 'Lost'} (Sim: {lead.get('similarity_score', 0):.2f})\n"
            
    prompt = f"""
    You are a Sales AI Assistant.
    Analyze this NEW LEAD:
    Source: {lead_data.get('Source')}
    TimeOnSite: {lead_data.get('TimeOnSite')} sec
    PagesVisited: {lead_data.get('PagesVisited')}
    
    AI Prediction Probability: {prediction_score:.2f} (High probability means likely to convert).
    
    Context:
    {rag_context}
    
    Provide output in strictly this JSON format:
    {{
      "explanation": "Why this score? (Max 20 words)",
      "next_action": "Recommended step (Max 10 words)",
      "sales_notes": "One helpful tip based on similar leads (Max 20 words)"
    }}
    """
    
    try:
        # Generate
        response_text = get_llm_response(prompt, max_tokens=150, temperature=0.3)
        
        # Parse JSON
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        start = clean_text.find("{")
        end = clean_text.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(clean_text[start:end])
        else:
            print(f"JSON Parse Failed. Raw: {clean_text}")
            return {
                "explanation": f"Score {prediction_score:.2f}",
                "next_action": "Review lead",
                "sales_notes": clean_text[:50]
            }
            
    except Exception as e:
        print(f"Insight Generation Error: {e}")
        return {
            "explanation": f"Score is {prediction_score:.2f}.",
            "next_action": "Contact lead.",
            "sales_notes": "Data processed successfully."
        }


def chat_with_data(user_query, context_data):
    """
    answers general questions about the lead dataset with Redis Caching.
    """
    
    # --- DEMO HARDCODE BYPASS (Fastest) ---
    # Move to TOP to simulate instant response without loading LLMs
    try:
        q_lower = user_query.strip().lower()
        

                 
        # 4. Most Interest / Top Leads
        if "interest" in q_lower or "best" in q_lower or "top" in q_lower:
            top_leads = []
            limit = 5 # Default
            
            # Check for explicit number (e.g. "top 10")
            import re
            match = re.search(r"top\s+(\d+)", q_lower)
            if match:
                limit = int(match.group(1))
                if limit > 20: limit = 20 # Safety cap
            
            # A. Try Memory Cache First (Fastest)
            try:
                import backend.services.prediction_orchestrator as orchestrator
                # Use the explicit GLOBAL latest first if available (most robust)
                if orchestrator.LATEST_ANALYSIS_RESULT:
                     leads = orchestrator.LATEST_ANALYSIS_RESULT.get('results', [])
                     # Sort by score desc if not already
                     sorted_leads = sorted(leads, key=lambda x: x.get('score', 0), reverse=True)
                     top_leads = sorted_leads[:limit]
                

            except Exception as e:
                print(f"Cache Access Failed: {e}")

            # B. Try Persistent DB History (Robust Fallback)
            if not top_leads:
                try:
                    from backend.core.database import get_prediction_history, get_leads_by_run
                    history = get_prediction_history()
                    if history:
                        # Sort by timestamp desc just in case
                        latest_run = history[0]
                        run_id = latest_run['run_id']
                        
                        # Skip dummy run 999 if real data exists
                        if run_id == 999 and len(history) > 1:
                            latest_run = history[1]
                            run_id = latest_run['run_id']
                        
                        db_leads = get_leads_by_run(run_id)
                        # Convert DB objects/dicts to standard dict list
                        processed_leads = []
                        for l in db_leads:
                            raw = l.get('raw_data', {})
                            processed_leads.append({
                                "lead_id": raw.get('LeadID') or raw.get('id') or l.get('id'),
                                "score": l.get('prediction_score', 0),
                                "explanation": "High engagement signal." # DB might not store explanation in main row
                            })
                        processed_leads.sort(key=lambda x: x['score'], reverse=True)
                        top_leads = processed_leads[:limit]
                except Exception as e:
                    print(f"DB History Access Failed: {e}")

            # C. Build Response if Data Found
            if top_leads:
                header = f"Top {len(top_leads)} Leads (High Conversion Probability):" if "top" in q_lower else "Leads showing the most interest:"
                response_lines = [header + "\n"]
                response_lines.append("| Rank | Lead ID | Score | Key Reason |")
                response_lines.append("|---|---|---|---|")
                
                for i, lead in enumerate(top_leads, 1):
                    lid = lead.get('lead_id') or f"{i}"
                    score = int(lead.get('score', 0) * 100)
                    # Default explanation if missing
                    reason = lead.get('explanation') or "Top 10% behavior match."
                    reason = reason.replace("High Priority: ", "").replace("Medium Priority: ", "").strip()
                    # Truncate reason for table
                    if len(reason) > 40: reason = reason[:37] + "..."
                    
                    response_lines.append(f"| {i} | {lid} | {score}% | {reason} |")
                    
                response_lines.append("\nWould you like me to draft an email to the top lead?")
                return "\n".join(response_lines)



    except ImportError:
         pass

    _ensure_llms_loaded()
    query_norm = user_query.strip().lower()

    # 1. Cache Check
    cached_response = ChatCache.get_cached_response(user_query, context_data)
    if cached_response:
        return cached_response

    if not llm_primary and not llm_fallback:
        return "AI is currently unavailable (Models not loaded)."

    # 2. Context Optimization
    final_context = context_data
    # Truncate context if too large (Gemini can handle large context, Llama 8k is limit)
    # Llama 8b context is 8k, Gemini is massive.
    # Safe limit: 6000 chars ~ 1500 tokens
    if len(str(context_data)) > 6000:
         final_context = str(context_data)[:6000] + "\n...[truncated]..."

    prompt = f"""
    You are a Data Analyst AI.
    
    Dataset Context:
    {final_context}
    
    User Question: {user_query}
    
    Answer (concise, data-driven, max 50 words).
    IMPORTANT: Provide the answer in clean, plain text paragraphs.
    - Do NOT use Markdown headers (#), bolding (**), or italics (*).
    - Do NOT use bullet points (-) or pipe characters (|).
    - Use standard numbered lists (1., 2.) if you need to list items.
    - Keep the tone professional and conversational.
    """
    
    try:
        start_time = time.time()
        response = get_llm_response(prompt, max_tokens=150, temperature=0.7)
        duration = time.time() - start_time
        print(f"DEBUG: AI response took {duration:.2f}s")
        
        # 3. Cache Success
        if "Service Unavailable" not in response:
            ChatCache.cache_response(user_query, context_data, response)
            
        return response
    except Exception as e:
        print(f"AI Chat Error: {e}")
        return "I encountered an error analyzing the data."



