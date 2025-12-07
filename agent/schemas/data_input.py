from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageInput(BaseModel):
    role: MessageRole = MessageRole.USER
    content: str = Field(..., min_length=1, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What programs does IMT Mines Alès offer?"
            }
        }


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message to the agent")
    thread_id: Optional[str] = Field(default="default", description="Conversation thread ID for memory")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Tell me about the engineering programs",
                "thread_id": "user-123"
            }
        }