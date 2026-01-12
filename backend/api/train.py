from fastapi import APIRouter, HTTPException
import os
from backend.core.schemas import TrainRequest
from backend.core.config import UPLOAD_DIR
from backend.services.csv_service import read_csv_safe
from backend.services.ml_service import ml_service
from backend.services.rag_service import rag_service

router = APIRouter()

@router.post("/train")
async def train_model_endpoint(request: TrainRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        df = read_csv_safe(file_path)
        # Train ML Model
        if ml_service:
            result = ml_service.train(df, request.target_col)
            if result.get('status') == 'error':
                 raise HTTPException(status_code=400, detail=result.get('message', 'Training failed'))
            accuracy = result.get('accuracy', 0)
        else:
            accuracy = 0
        
        # Index leads
        if rag_service:
            rag_service.index_leads(df)
        analysis_text = f"Model trained using Random Forest.\nAccuracy: {accuracy:.2f}\n\nTop features analyzed for lead scoring model."
        
        return {"status": "trained", "metrics": {"accuracy": accuracy, "analysis": analysis_text}}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Train Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
