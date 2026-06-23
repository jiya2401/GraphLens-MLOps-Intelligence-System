"""
Analytics Router — endpoint for aggregate dashboard analytics.
"""

from fastapi import APIRouter

from backend.models.analytics import AnalyticsResponse
from backend.services import analytics_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Get comprehensive analytics across all graphs.
    Includes failure distribution, resource utilization, temporal trends.
    """
    return analytics_service.compute_analytics()
