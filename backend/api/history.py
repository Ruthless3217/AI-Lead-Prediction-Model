from fastapi import APIRouter, HTTPException
from backend.core.database import get_prediction_history, get_leads_by_run

router = APIRouter()

@router.get("/prediction-history")
async def get_history():
    """Get all prediction runs"""
    try:
        history = get_prediction_history()
        


        return {"history": history}
    except Exception as e:
        print(f"History Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prediction-history/{run_id}")
async def get_prediction_by_run(run_id: int):
    """Get detailed results from a specific prediction run"""
    try:


        # Get run metadata first
        history = get_prediction_history()
        run_metadata = next((h for h in history if h['run_id'] == run_id), None)
        
        if not run_metadata:
            raise HTTPException(status_code=404, detail="Prediction run not found")
            
        # Get the leads for this run
        leads = get_leads_by_run(run_id)
        
        # Transform the data to match the expected format
        results = []
        for lead in leads:
            # Extract raw data if available
            raw_data = lead.get('raw_data', {})
            if isinstance(raw_data, dict):
                lead_item = {
                    **raw_data,
                    "score": round(lead.get('prediction_score', 0), 2),
                    "priority": lead.get('priority', 'Unknown'),
                    "actual_converted": raw_data.get('Converted') if 'Converted' in raw_data else (raw_data.get('converted') if 'converted' in raw_data else None),
                    "prediction_accuracy": None 
                }
                
                # Re-calculate accuracy if needed for UI
                if lead_item["actual_converted"] is not None:
                    actual = int(lead_item["actual_converted"]) == 1
                    prio = lead_item["priority"]
                    if prio == "High" and actual: lead_item["prediction_accuracy"] = "correct"
                    elif prio == "Low" and not actual: lead_item["prediction_accuracy"] = "correct"
                    elif prio == "High" and not actual: lead_item["prediction_accuracy"] = "false_positive"
                    elif prio == "Low" and actual: lead_item["prediction_accuracy"] = "missed"
                    else: lead_item["prediction_accuracy"] = "medium"
            else:
                lead_item = {
                    "score": round(lead.get('prediction_score', 0), 2),
                    "priority": lead.get('priority', 'Unknown'),
                    "Source": lead.get('source', 'Unknown')
                }
            results.append(lead_item)
        
        return {
            "run_id": run_id,
            "filename": run_metadata.get('filename', 'Unknown'),
            "timestamp": run_metadata.get('timestamp'),
            "results": results,
            "has_actual_data": run_metadata.get('has_actual_data', False),
            "accuracy_metrics": {
                "overall_accuracy": run_metadata.get('accuracy'),
                "total_predictions": run_metadata.get('total_leads', len(results)),
                "with_actual_data": run_metadata.get('total_leads', 0),
                "f1": run_metadata.get('f1_score'),
                "auprc": run_metadata.get('pr_auc'),
                "precision_k": run_metadata.get('precision_at_k'),
                "recall_k": run_metadata.get('recall_at_k')
            } if run_metadata.get('accuracy') is not None else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
