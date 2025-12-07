from fastapi import APIRouter, Depends
from agent.schemas.health import HealthResponse
from agent.api.services.agent_service import AgentService, get_agent_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and agent service"
)
async def health_check(
    service: AgentService = Depends(get_agent_service)
) -> HealthResponse:
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthResponse with current service status
    """
    health_data = await service.health_check()
    return HealthResponse(**health_data)


@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Readiness Check",
    description="Check if the agent is initialized and ready to handle requests"
)
async def readiness_check(
    service: AgentService = Depends(get_agent_service)
) -> HealthResponse:
    """
    Readiness check to verify agent is fully initialized.
    
    Returns:
        HealthResponse indicating readiness status
    """
    health_data = await service.health_check()
    status = "ready" if health_data["agent_initialized"] else "not_ready"
    return HealthResponse(
        status=status,
        agent_initialized=health_data["agent_initialized"],
        version=health_data["version"]
    )
