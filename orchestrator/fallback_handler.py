# orchestrator/fallback_handler.py
"""
Fallback Handler for the Finance Assistant Orchestrator.
Provides graceful error handling and default responses when agents fail.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FallbackHandler")


class FallbackHandler:
    """
    Handles fallback responses when primary agents fail or return no results.
    """
    
    # Default responses for common scenarios
    DEFAULT_RESPONSES = {
        "no_context": "I couldn't find specific information about that topic in my knowledge base. "
                      "Please try rephrasing your question or ask about a different topic.",
        
        "api_error": "I'm having trouble connecting to the data source right now. "
                     "Please try again in a few moments.",
        
        "llm_error": "I encountered an issue while generating a response. "
                     "Please try again or simplify your question.",
        
        "voice_error": "I had trouble processing the audio. "
                       "Please make sure the recording is clear and try again.",
        
        "timeout": "The request took too long to process. "
                   "Please try a simpler query or try again later.",
        
        "invalid_input": "I couldn't understand your request. "
                         "Please provide a clear financial question.",
        
        "no_data": "No market data is available for that symbol or time period. "
                   "Please check the ticker symbol and try again.",
        
        "general": "Something went wrong while processing your request. "
                   "Please try again later or contact support."
    }
    
    # Helpful suggestions for users
    SUGGESTIONS = [
        "Try asking about specific stock tickers like AAPL, TSMC, or MSFT",
        "Ask about earnings reports, price trends, or market analysis",
        "You can ask questions like 'What is the RSI for Apple?' or 'Did TSMC beat earnings?'",
        "For voice queries, speak clearly and avoid background noise"
    ]
    
    def __init__(self):
        self.error_count = 0
        self.last_error_time: Optional[datetime] = None
    
    def get_fallback_response(
        self, 
        error_type: str = "general",
        original_query: Optional[str] = None,
        error_details: Optional[str] = None,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a fallback response based on the error type.
        
        Args:
            error_type: Type of error that occurred
            original_query: The user's original query
            error_details: Technical error details for logging
            include_suggestions: Whether to include helpful suggestions
        
        Returns:
            Dict containing the fallback response and metadata
        """
        # Log the error
        self._log_error(error_type, original_query, error_details)
        
        # Get the appropriate response
        response_text = self.DEFAULT_RESPONSES.get(error_type, self.DEFAULT_RESPONSES["general"])
        
        # Build response object
        response = {
            "success": False,
            "error_type": error_type,
            "message": response_text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add original query if available
        if original_query:
            response["original_query"] = original_query
        
        # Add suggestions if requested
        if include_suggestions:
            response["suggestions"] = self._get_relevant_suggestions(error_type)
        
        return response
    
    def _log_error(
        self, 
        error_type: str, 
        query: Optional[str], 
        details: Optional[str]
    ) -> None:
        """Log error details for debugging."""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        log_message = f"Fallback triggered - Type: {error_type}"
        if query:
            log_message += f" | Query: {query[:100]}"  # Truncate long queries
        if details:
            log_message += f" | Details: {details[:200]}"
        
        logger.warning(log_message)
    
    def _get_relevant_suggestions(self, error_type: str) -> list:
        """Get suggestions relevant to the error type."""
        if error_type == "voice_error":
            return [self.SUGGESTIONS[3]]  # Voice-specific suggestion
        elif error_type in ["no_context", "no_data"]:
            return self.SUGGESTIONS[:3]  # Query help suggestions
        else:
            return [self.SUGGESTIONS[0], self.SUGGESTIONS[1]]
    
    def handle_agent_failure(
        self,
        agent_name: str,
        query: str,
        exception: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Handle failure from a specific agent.
        
        Args:
            agent_name: Name of the failed agent
            query: The query that failed
            exception: The exception that was raised
        
        Returns:
            Fallback response dict
        """
        error_type_map = {
            "api_agent": "api_error",
            "scraper_agent": "api_error",
            "language_agent": "llm_error",
            "retriever_agent": "no_context",
            "voice_agent": "voice_error",
            "analytics_agent": "no_data"
        }
        
        error_type = error_type_map.get(agent_name, "general")
        error_details = str(exception) if exception else None
        
        return self.get_fallback_response(
            error_type=error_type,
            original_query=query,
            error_details=error_details
        )
    
    def is_rate_limited(self, max_errors: int = 10, window_seconds: int = 60) -> bool:
        """
        Check if we should rate limit responses due to too many errors.
        
        Args:
            max_errors: Maximum errors allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        if self.last_error_time is None:
            return False
        
        time_since_last = (datetime.now() - self.last_error_time).total_seconds()
        
        if time_since_last > window_seconds:
            # Reset counter if window has passed
            self.error_count = 0
            return False
        
        return self.error_count >= max_errors
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get the health status of the fallback handler."""
        return {
            "error_count": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "is_healthy": self.error_count < 5,
            "rate_limited": self.is_rate_limited()
        }


# Create a global instance for use across the application
fallback_handler = FallbackHandler()


def get_fallback(error_type: str = "general", query: Optional[str] = None) -> str:
    """
    Convenience function to get a simple fallback message.
    
    Args:
        error_type: Type of error
        query: Original query
    
    Returns:
        Fallback message string
    """
    response = fallback_handler.get_fallback_response(
        error_type=error_type,
        original_query=query,
        include_suggestions=False
    )
    return response["message"]


def handle_exception(agent_name: str, query: str, exception: Exception) -> Dict[str, Any]:
    """
    Convenience function to handle an agent exception.
    
    Args:
        agent_name: Name of the failed agent
        query: The query that failed
        exception: The exception that was raised
    
    Returns:
        Fallback response dict
    """
    return fallback_handler.handle_agent_failure(agent_name, query, exception)


# Test routine
if __name__ == "__main__":
    print("Testing Fallback Handler...")
    
    handler = FallbackHandler()
    
    # Test basic fallback
    print("\n=== No Context Fallback ===")
    response = handler.get_fallback_response("no_context", "What is the price of XYZ stock?")
    print(f"Message: {response['message']}")
    print(f"Suggestions: {response.get('suggestions', [])}")
    
    # Test agent failure
    print("\n=== Agent Failure ===")
    response = handler.handle_agent_failure(
        "api_agent",
        "Get AAPL data",
        Exception("Connection timeout")
    )
    print(f"Error Type: {response['error_type']}")
    print(f"Message: {response['message']}")
    
    # Test health status
    print("\n=== Health Status ===")
    status = handler.get_health_status()
    print(f"Error Count: {status['error_count']}")
    print(f"Is Healthy: {status['is_healthy']}")
