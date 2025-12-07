from agent.agent_client import Agent_Client
from agent.utils.logger import get_logger
from agent.utils.custom_exception import CustomException
from langchain_core.messages import HumanMessage
from typing import Optional
from langchain_core.messages import AnyMessage

logger = get_logger(__name__)


class AgentService:
    """Service layer for managing the AI agent."""
    
    _instance: Optional["AgentService"] = None
    
    def __new__(cls) -> "AgentService":
        """Singleton pattern to ensure single agent instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        self.agent_client = Agent_Client()
        self._initialized = True
        logger.info("AgentService initialized")
    
    async def initialize_agent(self) -> None:
        """Initialize the agent client with MCP tools."""
        try:
            if not self.agent_client.is_initialized:
                logger.info("Initializing agent client...")
                await self.agent_client.initialize()
                logger.info("Agent client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise CustomException("Failed to initialize agent", e)
    
    async def chat(self, message: str, thread_id: Optional[str] = None) -> str:
        """
        Process a chat message and return the agent's response.
        
        Args:
            message: User's input message
            thread_id: Conversation thread ID for memory persistence
            
        Returns:
            Agent's response string
        """
        try:
            if not self.agent_client.is_initialized:
                await self.initialize_agent()
            
            logger.info(f"Processing message for thread: {thread_id}")
            
            messages: list[AnyMessage] = [HumanMessage(content=message)]
            response = await self.agent_client.ask(messages, thread_id)
            
            logger.info(f"Response generated for thread: {thread_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            raise CustomException("Failed to process chat message", e)
    
    async def health_check(self) -> dict:
        """Check the health status of the agent service."""
        return {
            "status": "healthy",
            "agent_initialized": self.agent_client.is_initialized,
            "version": "1.0.0"
        }
    
    async def shutdown(self) -> None:
        """Cleanup resources on shutdown."""
        try:
            logger.info("Shutting down agent service...")
            await self.agent_client.close()
            logger.info("Agent service shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def get_agent_service() -> AgentService:
    """Dependency injection for AgentService."""
    return AgentService()
