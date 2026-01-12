from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import shutil
from backend.core.config import UPLOAD_DIR, MAX_FILE_SIZE
from backend.services.csv_service import read_csv_safe

router = APIRouter()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Validation
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        size = 0
        with open(file_location, "wb") as buffer:
            while content := await file.read(1024 * 1024): # Read in 1MB chunks
                size += len(content)
                if size > MAX_FILE_SIZE:
                    os.remove(file_location) # Cleanup
                    raise HTTPException(status_code=413, detail=f"File too large. Maximum size is 50MB.")
                buffer.write(content)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    


    try:
        df = read_csv_safe(file_location)
        if df.empty:
             raise HTTPException(status_code=400, detail="CSV file is empty.")
             
        columns = df.columns.tolist()
        preview = df.head().fillna("").to_dict(orient="records")
        
        return {"filename": file.filename, "columns": columns, "preview": preview}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
