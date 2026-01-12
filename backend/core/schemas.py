from pydantic import BaseModel
from typing import Optional

class PredictRequest(BaseModel):
    filename: str
    explain: bool = False # Enable SHAP explanation for top lead

class TrainRequest(BaseModel):
    filename: str
    target_col: str

class ChatRequest(BaseModel):
    message: str
    context: str = ""
    filename: Optional[str] = None

class Metrics(BaseModel):
    accuracy: float
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    custom_metrics: dict = {}
