from fastapi import APIRouter
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chatbot_router = APIRouter()

class Query(BaseModel):
    question: str
    language: str = "en"  # Default to English

@chatbot_router.post("/ask")
async def ask(query: Query):
    try:
        # Validate language code
        valid_languages = ["en", "hi", "or", "bn", "ta", "te", "kn", "mr"]
        language = query.language.lower() if query.language else "en"
        
        if language not in valid_languages:
            logger.warning("Invalid language code: %s, defaulting to English", query.language)
            language = "en"
        
        logger.info("Received query: %s in language: %s", query.question, language)
        # Import here to avoid circular imports
        from chatbot.ai_logic import get_faq_or_ai_response
        result = get_faq_or_ai_response(query.question, language)
        logger.info("Successfully processed query: %s, response: %s", query.question, result.get('reply', '')[:100])
        return result
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error processing query: %s", query.question, exc_info=True)
        # Return a proper JSON response with error details instead of raising HTTPException
        error_msg = "I'm sorry, but I encountered an error while processing your request. Please try again later."
        logger.debug("Exception details: %s", str(e))
        return {"reply": error_msg}