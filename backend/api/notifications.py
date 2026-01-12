from fastapi import APIRouter
from backend.core.database import get_notifications, mark_notification_read

router = APIRouter()

@router.get("/notifications")
async def get_notifications_endpoint():
    """Get recent notifications"""
    return get_notifications(limit=10)

@router.post("/notifications/{id}/read")
async def read_notification_endpoint(id: int):
    """Mark notification as read"""
    mark_notification_read(id)
    return {"status": "ok"}
