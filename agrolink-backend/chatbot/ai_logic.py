import logging
import google.generativeai as genai
import os
import csv
from dotenv import load_dotenv
from chatbot.translator import translate_text
import google.api_core.exceptions

# Set up logging
logger = logging.getLogger(__name__)

# load variables from .env file
load_dotenv()

# Load Gemini API key from env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up the model configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Try different models in order of preference
MODEL_OPTIONS = [
    "models/gemini-flash-latest",  # Flash models typically have higher quotas
    "models/gemini-2.0-flash", 
    "models/gemini-2.0-flash-001",
    "models/gemini-pro-latest",
    "models/gemini-1.5-flash"
]

# Load FAQ dataset
faq_data = []

def load_faq_data():
    """Load FAQ data from CSV file"""
    faq_list = []
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        faq_file_path = os.path.join(current_dir, 'data', 'faq_dataset.csv')
        
        with open(faq_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            faq_list = list(reader)
    except FileNotFoundError:  # pylint: disable=broad-except
        logger.error("Error loading FAQ data: File not found")
        faq_list = []
    except Exception:  # pylint: disable=broad-except
        logger.error("Error loading FAQ data", exc_info=True)
        faq_list = []
    return faq_list

# Load FAQ data on startup
faq_data = load_faq_data()
logger.info("Loaded %s FAQ entries", len(faq_data))

def find_faq_match(question):
    """Find a matching FAQ entry for the question"""
    question_lower = question.lower().strip()
    # Split question into words for better matching
    question_words = set(question_lower.split())
    
    best_match = None
    best_score = 0
    
    for entry in faq_data:
        # Check for exact or partial matches
        entry_question_lower = entry['question'].lower().strip()
        entry_words = set(entry_question_lower.split())
        
        # Calculate similarity score based on word overlap
        common_words = question_words.intersection(entry_words)
        score = len(common_words) / max(len(question_words), len(entry_words), 1)
        
        # Exact match gets highest priority
        if entry_question_lower == question_lower:
            return entry['answer']
            
        # Update best match if score is better
        # Increased threshold for similarity to make matching less aggressive
        if score > best_score and score > 0.6:  # Increased threshold from 0.5 to 0.6
            best_score = score
            best_match = entry['answer']
    
    return best_match  # Return best match or None

def get_working_model():
    """Try to get a working model from the available options"""
    for model_name in MODEL_OPTIONS:
        try:
            model = genai.GenerativeModel(model_name)
            # Test the model with a simple prompt
            test_response = model.generate_content("Hello", generation_config={"max_output_tokens": 10})
            if test_response.text:
                logger.info("Successfully initialized model: %s", model_name)
                return model
        except (google.api_core.exceptions.GoogleAPIError, google.api_core.exceptions.ResourceExhausted) as e:
            logger.warning("Failed to initialize model %s: %s", model_name, str(e))
            continue
        except Exception:  # pylint: disable=broad-except
            logger.warning("Failed to initialize model %s due to unexpected error", model_name, exc_info=True)
            continue
    # If no model works, try a fallback approach
    try:
        # Try with a simpler model name
        fallback_model = genai.GenerativeModel("gemini-pro")
        test_response = fallback_model.generate_content("Hello", generation_config={"max_output_tokens": 10})
        if test_response.text:
            logger.info("Successfully initialized fallback model: gemini-pro")
            return fallback_model
    except (google.api_core.exceptions.GoogleAPIError, google.api_core.exceptions.ResourceExhausted) as e:
        logger.error("Failed to initialize fallback model: %s", str(e))
    except Exception:  # pylint: disable=broad-except
        logger.error("Failed to initialize fallback model due to unexpected error", exc_info=True)
    return None

# Get working model at startup
working_model = get_working_model()
if working_model is None:
    logger.warning("No working AI model found! Check your GEMINI_API_KEY and network connectivity. Will use fallback responses only.")
else:
    logger.info("AI model successfully initialized: %s", working_model.model_name)

def get_faq_or_ai_response(question, language="en"):
    try:
        # Validate language parameter
        if not language or not isinstance(language, str):
            logger.warning("Invalid language parameter, defaulting to English")
            language = "en"
        
        logger.info("Processing query: '%s' in language: '%s'", question, language)
        
        # Map language codes to language names for the prompt
        language_map = {
            "en": "English",
            "hi": "Hindi", 
            "or": "Odia",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "kn": "Kannada",
            "mr": "Marathi"
        }
        
        language_name = language_map.get(language.lower(), "English")
        
        # First check if there's an FAQ match
        faq_answer = find_faq_match(question)
        logger.info("FAQ match found: %s", faq_answer is not None)
        
        # If we have a direct FAQ match, return it in the target language
        if faq_answer:
            english_response = faq_answer
            logger.info("Using FAQ response")
            
            # If not English, translate FAQ response to target language
            if language.lower() != "en":
                logger.info("Translating FAQ response to %s", language)
                translated_response = translate_text(english_response, "en", language)
                logger.info("Translated FAQ response: %s...", translated_response[:100])
                return {"reply": translated_response}
            
            return {"reply": english_response}
        else:
            # No FAQ match - use AI to generate response in target language
            ai_response = None
            if working_model:
                try:
                    logger.info("Using AI model to generate response in %s", language_name)
                    # Prepare context with FAQ data
                    faq_context = "\n".join([f"Q: {entry['question']}\nA: {entry['answer']}" for entry in faq_data[:10]])
                    
                    # Generate response directly in the target language
                    prompt = f"""
You are an expert agricultural assistant for Indian farmers. Your goal is to provide accurate, helpful, and practical farming advice.

IMPORTANT: You MUST respond ONLY in {language_name}. Do not mix languages or use English. 
Every word of your response must be in {language_name}.

Here are some frequently asked questions and answers that might be relevant:
{faq_context}

The farmer has asked: "{question}"

Please provide a comprehensive response in {language_name} that:
1. Directly answers the farmer's question
2. Is practical and actionable
3. Considers Indian farming conditions and practices
4. Uses the FAQ information if relevant
5. Is written in clear, simple {language_name}

If you're not certain about specific details, acknowledge that and provide the best general advice.
Do not make up information that you're not confident about.

Remember: Your entire response must be in {language_name} only.
                    """
                    
                    response = working_model.generate_content(prompt, generation_config=generation_config)
                    # Check if response has valid content before accessing .text
                    if response and response.parts and len(response.parts) > 0:
                        ai_response = response.text.strip()
                        logger.info("AI response generated successfully in %s: %s...", language_name, ai_response[:100])
                    else:
                        logger.warning("AI response is empty or invalid")
                        ai_response = None
                    
                except (google.api_core.exceptions.GoogleAPIError, google.api_core.exceptions.ResourceExhausted) as ai_error:
                    logger.error("AI Error: %s", str(ai_error))
                    ai_response = None
                except ValueError as ve:
                    logger.warning("AI response validation error: %s", str(ve))
                    ai_response = None
                except Exception:  # pylint: disable=broad-except
                    logger.error("Unexpected error in AI response generation", exc_info=True)
                    ai_response = None
            else:
                logger.info("No AI model available, skipping AI response generation")
            
            # Determine final response
            if ai_response:
                # AI generated response in target language
                logger.info("Returning AI-generated response in %s", language_name)
                return {"reply": ai_response}
            else:
                # No AI response, provide fallback
                logger.info("No AI response, using fallback")
                fallback_responses = {
                    "en": "I'm currently unable to generate a detailed response for your question. Here are some general farming tips that might help:\n\n1. For crop selection, consider your local soil type and climate conditions\n2. Regular soil testing helps determine the right fertilizers for your crops\n3. Proper irrigation scheduling is crucial for healthy plant growth\n4. Early pest detection and management can save your crops\n5. Crop rotation helps maintain soil fertility\n\nFor more specific advice, please try rephrasing your question or ask about a specific topic like crops, fertilizers, weather, or plant diseases.",
                    
                    "hi": "मुझे आपके प्रश्न का विस्तृत उत्तर देने में वर्तमान में समस्या हो रही है। यहां कुछ सामान्य कृषि सुझाव दिए गए हैं जो आपकी मदद कर सकते हैं:\n\n1. फसल चयन के लिए, अपनी स्थानीय मिट्टी के प्रकार और जलवायु परिस्थितियों पर विचार करें\n2. नियमित मिट्टी परीक्षण आपकी फसलों के लिए सही उर्वरक निर्धारित करने में मदद करता है\n3. उचित सिंचाई अनुसूची स्वस्थ पौधों की वृद्धि के लिए महत्वपूर्ण है\n4. कीट का प्रारंभिक पता लगाना और प्रबंधन आपकी फसलों को बचा सकता है\n5. फसल चक्र मिट्टी की उर्वरता को बनाए रखने में मदद करता है\n\nअधिक विशिष्ट सलाह के लिए, कृपया अपने प्रश्न को फिर से बताने का प्रयास करें या फसलों, उर्वरकों, मौसम या पौधों की बीमारियों के बारे में पूछें।",
                    
                    "ta": "உங்கள் கேள்விக்கான விரிவான பதிலை நான் தற்போது வழங்க முடியவில்லை. உங்களுக்கு உதவக்கூடிய சில பொதுவான விவசாய குறிப்புகள் இங்கே உள்ளன:\n\n1. பயிர் தேர்வுக்கு, உங்கள் স்থानीய மண்ணின் வகை மற்றும் காலநிலை நிலைமைகளைக் கருத்தில் கொள்ளுங்கள்\n2. வழக்கமான மண் சோதனை உங்கள் பயிர்களுக்கான சரியான உரம் தீர்மானிக்க உதவுகிறது\n3. சரியான நீர்ப்பாசन அட்டவணை ஆரோக்கியமான தாவர வளர்ச்சிக்கு முக்கியமானது\n4. பூச்சிகளின் ஆரம்ப கண்டறிதல் மற்றும் நிர்வாகம் உங்கள் பயிர்களைக் காக்க முடியும்\n5. பயிர் சுழற்சி மண்ணின் வளம் பராமரிக்க உதவுகிறது\n\nআরও구체적인 sलाह के लिए, कृपया अपने प्रश्न को फिर से बताने का प्रयास करें या फसलों, उर्वरकों, मौसम या पौधों की बीमारियों के बारे में पूछें।"
                }
                
                fallback_text = fallback_responses.get(language.lower(), fallback_responses.get("en"))
                logger.info("Returning fallback response in %s", language_name)
                return {"reply": fallback_text}

    except Exception:  # pylint: disable=broad-except
        logger.error("Error in get_faq_or_ai_response", exc_info=True)
        # Handle any other unexpected errors
        return {"reply": "I'm sorry, but I encountered an error while processing your request. Please try again later."}
