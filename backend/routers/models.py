"""
Models Router
API endpoints for AI model information
"""

from fastapi import APIRouter
from services.ai_providers import get_model_status

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def get_models():
    """Get available AI providers and their models."""
    return get_model_status()
