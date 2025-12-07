from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    agent_initialized: bool = Field(..., description="Whether the agent is initialized")
    version: str = Field(default="1.0.0", description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "agent_initialized": True,
                "version": "1.0.0"
            }
        }