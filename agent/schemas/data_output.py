from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    thread_id: str = Field(..., description="Thread ID used for this conversation")
    success: bool = Field(default=True, description="Whether the request was successful")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "IMT Mines Alès offers several engineering programs...",
                "thread_id": "user-123",
                "success": True
            }
        }


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    success: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "An error occurred while processing your request",
                "success": False
            }
        }