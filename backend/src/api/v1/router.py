from fastapi import APIRouter

from src.api.v1.endpoints.healthcheck import router as health_router
from src.api.v1.endpoints.project_router import router as project_router
from src.api.v1.endpoints.websocket_handler import websocket_endpoint


routers = APIRouter()
router_list = [
    health_router,
    project_router  # Keep REST endpoints for backwards compatibility
]

# Register all routers in a single place for maintainability
for router in router_list:
    routers.include_router(router)
