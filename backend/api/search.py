from fastapi import APIRouter, HTTPException
from backend.core.database import search_leads

router = APIRouter()

@router.get("/search")
async def search_endpoint(q: str):
    """Search leads"""
    try:
        results = search_leads(q)
        formatted_results = []
        for lead in results:
             raw_data = lead.get('raw_data', {})
             formatted = {
                 "id": lead.get('id'),
                 "lead_id": lead.get('lead_id'),
                 "source": lead.get('source'),
                 "priority": lead.get('priority'),
                 "score": lead.get('prediction_score'),
                 "company": raw_data.get('Company') or raw_data.get('company') or 'Unknown'
             }
             formatted_results.append(formatted)
        return {"results": formatted_results}
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
