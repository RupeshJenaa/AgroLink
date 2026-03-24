import logging
import os
import csv
from dotenv import load_dotenv
from chatbot.translator import translate_text

# Set up logging
logger = logging.getLogger(__name__)

# load variables from .env file
load_dotenv()

# Use the Groq SDK
from groq import Groq

# Create the client — it automatically looks for GROQ_API_KEY in environment
# Since you might have pasted it in .env, ensure it's loaded
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use — Groq's lightning fast, very capable and completely free model
MODEL_ID = "llama-3.3-70b-versatile"

# Generation configuration mapping (similar parameters to what we had)
generation_kwargs = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 8192,
}

# Load FAQ dataset
faq_data = []

def load_faq_data():
    """Load FAQ data from CSV file"""
    faq_list = []
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        faq_file_path = os.path.join(current_dir, 'data', 'faq_dataset.csv')
        
        logger.info("Looking for FAQ file at: %s", faq_file_path)
        
        with open(faq_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            faq_list = list(reader)
    except FileNotFoundError:
        logger.error("Error loading FAQ data: File not found at %s", faq_file_path)
        faq_list = []
    except Exception:
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
        if score > best_score and score > 0.6:
            best_score = score
            best_match = entry['answer']
    
    return best_match  # Return best match or None

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
            # No FAQ match — use AI to generate response in target language
            ai_response = None
            try:
                logger.info("Using AI model %s to generate response in %s", MODEL_ID, language_name)
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
                
                # Groq Chat Completions API Call
                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    **generation_kwargs
                )
                
                # Check if response has valid content
                if response and response.choices and response.choices[0].message.content:
                    ai_response = response.choices[0].message.content.strip()
                    logger.info("AI response generated successfully in %s: %s...", language_name, ai_response[:100])
                else:
                    logger.warning("AI response is empty or invalid")
                    ai_response = None
                    
            except Exception as ai_error:
                logger.error("AI Error: %s", str(ai_error))
                ai_response = None
            
            # Determine final response
            if ai_response:
                logger.info("Returning AI-generated response in %s", language_name)
                return {"reply": ai_response}
            else:
                # No AI response, provide fallback
                logger.info("No AI response, using fallback")
                fallback_responses = {
                    "en": "I'm currently unable to generate a detailed response for your question. Here are some general farming tips that might help:\n\n1. For crop selection, consider your local soil type and climate conditions\n2. Regular soil testing helps determine the right fertilizers for your crops\n3. Proper irrigation scheduling is crucial for healthy plant growth\n4. Early pest detection and management can save your crops\n5. Crop rotation helps maintain soil fertility\n\nFor more specific advice, please try rephrasing your question or ask about a specific topic like crops, fertilizers, weather, or plant diseases.",
                    
                    "hi": "मुझे आपके प्रश्न का विस्तृत उत्तर देने में वर्तमान में समस्या हो रही है। यहां कुछ सामान्य कृषि सुझाव दिए गए हैं जो आपकी मदद कर सकते हैं:\n\n1. फसल चयन के लिए, अपनी स्थानीय मिट्टी के प्रकार और जलवायु परिस्थितियों पर विचार करें\n2. नियमित मिट्टी परीक्षण आपकी फसलों के लिए सही उर्वरक निर्धारित करने में मदद करता है\n3. उचित सिंचाई अनुसूची स्वस्थ पौधों की वृद्धि के लिए महत्वपूर्ण है\n4. कीट का प्रारंभिक पता लगाना और प्रबंधन आपकी फसलों को बचा सकता है\n5. फसल चक्र मिट्टी की उर्वरता को बनाए रखने में मदद करता है\n\nअधिक विशिष्ट सलाह के लिए, कृपया अपने प्रश्न को फिर से बताने का प्रयास करें या फसलों, उर्वरकों, मौसम या पौधों की बीमारियों के बारे में पूछें।",
                    
                    "or": "ମୁଁ ବର୍ତ୍ତମାନ ଆପଣଙ୍କ ପ୍ରଶ୍ନର ବିସ୍ତୃତ ଉତ୍ତର ଦେବାରେ ଅସମର୍ଥ। ଏଠାରେ କିଛି ସାଧାରଣ କୃଷି ସୁଝାବ ଅଛି:\n\n1. ଫସଲ ଚୟନ ପାଇଁ ଆପଣଙ୍କ ସ୍ଥାନୀୟ ମାଟିର ପ୍ରକାର ଏବଂ ଜଳବାୟୁ ବିଚାର କରନ୍ତୁ\n2. ନିୟମିତ ମାଟି ପରୀକ୍ଷା ଆପଣଙ୍କ ଫସଲ ପାଇଁ ସଠିକ୍ ସାର ନିର୍ଧାରଣ କରିବାରେ ସାହାଯ୍ୟ କରେ\n3. ସ୍ାସ୍ଥ୍ୟକର ଉଦ୍ଭିଦ ବୃଦ୍ଧି ପାଇଁ ଉଚିତ ଜଳସେଚନ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ\n4. ଆଦିମ କୀଟ ଚିହ୍ନଟ ଆପଣଙ୍କ ଫସଲ ବଞ୍ଚାଇ ପାରିବ\n5. ଫସଲ ଚକ୍ର ମାଟିର ଉର୍ବରତା ବଜାୟ ରଖିବାରେ ସାହାଯ୍ୟ କରେ",
                    
                    "bn": "আমি বর্তমানে আপনার প্রশ্নের বিস্তারিত উত্তর দিতে অক্ষম। এখানে কিছু সাধারণ কৃষি পরামর্শ রয়েছে:\n\n1. ফসল নির্বাচনের জন্য আপনার স্থানীয় মাটির ধরন এবং জলবায়ু বিবেচনা করুন\n2. নিয়মিত মাটি পরীক্ষা আপনার ফসলের জন্য সঠিক সার নির্ধারণে সাহায্য করে\n3. সুস্থ উদ্ভিদ বৃদ্ধির জন্য সঠিক সেচ গুরুত্বপূর্ণ\n4. প্রাথমিক কীটপতঙ্গ সনাক্তকরণ আপনার ফসল বাঁচাতে পারে\n5. শস্য আবর্তন মাটির উর্বরতা বজায় রাখতে সাহায্য করে",
                    
                    "ta": "உங்கள் கேள்விக்கான விரிவான பதிலை நான் தற்போது வழங்க முடியவில்லை. உங்களுக்கு உதவக்கூடிய சில பொதுவான விவசாய குறிப்புகள்:\n\n1. பயிர் தேர்வுக்கு உங்கள் மண்ணின் வகை மற்றும் காலநிலையைக் கருத்தில் கொள்ளுங்கள்\n2. வழக்கமான மண் சோதனை சரியான உரம் தீர்மானிக்க உதவுகிறது\n3. ஆரோக்கியமான தாவர வளர்ச்சிக்கு சரியான நீர்ப்பாசனம் முக்கியம்\n4. ஆரம்ப பூச்சி கண்டறிதல் உங்கள் பயிர்களைக் காக்கும்\n5. பயிர் சுழற்சி மண்ணின் வளத்தை பராமரிக்க உதவுகிறது",
                    
                    "te": "మీ ప్రశ్నకు వివరమైన సమాధానం ఇవ్వడంలో నేను ప్రస్తుతం అసమర్థుడను. ఇక్కడ కొన్ని సాధారణ వ్యవసాయ చిట్కాలు ఉన్నాయి:\n\n1. పంట ఎంపికకు మీ స్థానిక నేల రకం మరియు వాతావరణాన్ని పరిగణించండి\n2. క్రమం తప్పక నేల పరీక్ష సరైన ఎరువు నిర్ణయించడంలో సహాయపడుతుంది\n3. ఆరోగ్యకరమైన మొక్కల పెరుగుదలకు సరైన నీటిపారుదల ముఖ్యం\n4. ప్రారంభ చీడ గుర్తింపు మీ పంటలను కాపాడగలదు\n5. పంట మార్పిడి నేల సారవంతత్వాన్ని నిర్వహించడంలో సహాయపడుతుంది",
                    
                    "kn": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ವಿವರವಾದ ಉತ್ತರ ನೀಡಲು ನನಗೆ ಪ್ರಸ್ತುತ ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. ಇಲ್ಲಿ ಕೆಲವು ಸಾಮಾನ್ಯ ಕೃಷಿ ಸಲಹೆಗಳಿವೆ:\n\n1. ಬೆಳೆ ಆಯ್ಕೆಗಾಗಿ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಮಣ್ಣಿನ ಪ್ರಕಾರ ಮತ್ತು ಹವಾಮಾನವನ್ನು ಪರಿಗಣಿಸಿ\n2. ನಿಯಮಿತ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಸರಿಯಾದ ಗೊಬ್ಬರ ನಿರ್ಧರಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ\n3. ಆರೋಗ್ಯಕರ ಸಸ್ಯಗಳ ಬೆಳವಣಿಗೆಗೆ ಸರಿಯಾದ ನೀರಾವರಿ ಮುಖ್ಯ\n4. ಆರಂಭಿಕ ಕೀಟ ಪತ್ತೆ ನಿಮ್ಮ ಬೆಳೆಗಳನ್ನು ಉಳಿಸಬಹುದು\n5. ಬೆಳೆ ಸರದಿ ಮಣ್ಣಿನ ಸಾರವನ್ನು ಕಾಪಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ",
                    
                    "mr": "मी तुमच्या प्रश्नाचे सविस्तर उत्तर देण्यात सध्या अक्षम आहे. येथे काही सामान्य कृषी टिप्स आहेत:\n\n1. पीक निवडीसाठी तुमच्या स्थानिक मातीचा प्रकार आणि हवामान विचारात घ्या\n2. नियमित माती चाचणी योग्य खत ठरवण्यात मदत करते\n3. निरोगी वनस्पती वाढीसाठी योग्य सिंचन महत्त्वाचे आहे\n4. लवकर कीड ओळखणे तुमची पिके वाचवू शकते\n5. पीक बदल मातीची सुपीकता टिकवून ठेवण्यास मदत करतो"
                }
                
                fallback_text = fallback_responses.get(language.lower(), fallback_responses.get("en"))
                logger.info("Returning fallback response in %s", language_name)
                return {"reply": fallback_text}

    except Exception:
        logger.error("Error in get_faq_or_ai_response", exc_info=True)
        return {"reply": "I'm sorry, but I encountered an error while processing your request. Please try again later."}
