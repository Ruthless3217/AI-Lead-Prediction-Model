import pandas as pd
from fastapi import HTTPException

def read_csv_safe(file_path):
    """Fallback logic for different CSV encodings."""
    kwargs = {'low_memory': False}
    
    try:
        return pd.read_csv(file_path, encoding='utf-8', **kwargs)
    except UnicodeDecodeError:
        try:
            return pd.read_csv(file_path, encoding='ISO-8859-1', **kwargs)
        except UnicodeDecodeError:
            try:
                return pd.read_csv(file_path, encoding='latin1', **kwargs)
            except Exception as e:
                 raise HTTPException(status_code=400, detail=f"Could not decode CSV file: {str(e)}")
