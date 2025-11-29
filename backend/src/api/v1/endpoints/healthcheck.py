from fastapi import APIRouter, HTTPException
from datetime import datetime


router = APIRouter(tags=["Health Check"])


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    try:
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
