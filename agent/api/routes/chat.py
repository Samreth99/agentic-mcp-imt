from fastapi import APIRouter, Depends, HTTPException, status
from agent.schemas.data_output import  ChatResponse, ErrorResponse
from agent.schemas.data_input import ChatRequest
from agent.api.services.agent_service import AgentService, get_agent_service
from agent.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"model": ChatResponse, "description": "Successful response"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Chat with AI Agent",
    description="Send a message to the AI agent and receive a response"
)
async def chat(
    request: ChatRequest,
    service: AgentService = Depends(get_agent_service)
) -> ChatResponse:
    """
    Chat endpoint for interacting with the AI agent.
    
    Args:
        request: ChatRequest containing the user message and optional thread_id
        service: Injected AgentService instance
        
    Returns:
        ChatResponse with the agent's reply
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info(f"Received chat request for thread: {request.thread_id}")
        
        response = await service.chat(
            message=request.message,
            thread_id=request.thread_id
        )
        
        return ChatResponse(
            response=response,
            thread_id=request.thread_id,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ask",
    response_model=ChatResponse,
    responses={
        200: {"model": ChatResponse, "description": "Successful response"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Quick Ask",
    description="Simple endpoint to ask a question without thread management"
)
async def ask(
    message: str,
    service: AgentService = Depends(get_agent_service)
) -> ChatResponse:
    """
    Simplified ask endpoint for quick queries.
    
    Args:
        message: The question or message to send to the agent
        service: Injected AgentService instance
        
    Returns:
        ChatResponse with the agent's reply
    """
    try:
        response = await service.chat(message=message)
        return ChatResponse(
            response=response,
            thread_id="default",
            success=True
        )
    except Exception as e:
        logger.error(f"Ask endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
