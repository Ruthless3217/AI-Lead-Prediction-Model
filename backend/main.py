from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.core.config import UPLOAD_DIR
from backend.api import upload, train, predict, history, search, chat, notifications

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Nutto Hybrid Engine v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(upload.router)
app.include_router(train.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(chat.router)
# app.include_router(search.router) # Removed
# app.include_router(notifications.router) # Removed

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Nutto Hybrid Engine v2"}
