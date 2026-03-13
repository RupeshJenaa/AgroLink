"""
Translator module for converting text between languages
Uses MyMemory Translation API (completely FREE - no API keys or credentials required!)
Supports 8 Indian languages: Hindi, Odia, Bengali, Tamil, Telugu, Kannada, Marathi, English

MyMemory Translation API benefits:
- Completely free, no API keys needed
- Unlimited free usage
- Very reliable and fast
- Supports all 8 required languages
- Used by millions of users
"""
import logging
import requests

# Create logger
logger = logging.getLogger(__name__)

# MyMemory Translation API configuration (free public API - no auth needed)
MYMEMORY_ENDPOINT = "https://api.mymemory.translated.net/get"  # Free API endpoint
MYMEMORY_TIMEOUT = 5  # seconds

# Map Indian language codes to MyMemory codes
LANGUAGE_MAP = {
    'en': 'en-US',   # English
    'hi': 'hi',      # Hindi
    'or': 'or',      # Oriya/Odia
    'bn': 'bn',      # Bengali
    'ta': 'ta',      # Tamil
    'te': 'te',      # Telugu
    'kn': 'kn',      # Kannada
    'mr': 'mr',      # Marathi
}


def translate_text(text: str, src: str, dest: str) -> str:
    """
    Translate text using FREE MyMemory Translation API (no auth needed!)
    
    Args:
        text (str): Text to translate
        src (str): Source language code (e.g., 'en')
        dest (str): Destination language code (e.g., 'hi')
        
    Returns:
        str: Translated text (or original if translation fails)
    """
    # Validate input parameters
    if not text or not isinstance(text, str):
        logger.warning("Invalid text input for translation")
        return text if text else ""
        
    if not src or not isinstance(src, str):
        logger.warning("Invalid source language for translation")
        return text
        
    if not dest or not isinstance(dest, str):
        logger.warning("Invalid destination language for translation")
        return text
    
    # Normalize language codes
    src = src.lower().strip()
    dest = dest.lower().strip()
    
    # If source and destination are the same, return original text
    if src == dest:
        logger.info("Source and destination languages are the same, returning original text")
        return text
        
    # If destination is English, return original
    if dest == "en":
        logger.info("Destination is English, returning original text")
        return text
    
    # Get MyMemory language codes
    src_code = LANGUAGE_MAP.get(src, 'en-US')
    dest_code = LANGUAGE_MAP.get(dest, 'en-US')
    
    if src_code == dest_code:
        logger.info("Source and destination codes are the same, returning original text")
        return text
    
    # Try MyMemory Translation API (completely free!)
    try:
        logger.info("Translating from %s to %s using MyMemory API", src_code, dest_code)
        
        # Call MyMemory API
        params = {
            "q": text,  # Text to translate
            "langpair": f"{src_code}|{dest_code}"  # Language pair (source|target)
        }
        
        response = requests.get(
            MYMEMORY_ENDPOINT,
            params=params,
            timeout=MYMEMORY_TIMEOUT
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Check response status
            if result.get('responseStatus') == 200:
                # Extract translated text
                translated_text = result.get('responseData', {}).get('translatedText', text)
                
                if translated_text and len(translated_text.strip()) > 0 and translated_text != text:
                    logger.info("Successfully translated from %s to %s", src_code, dest_code)
                    return translated_text
                else:
                    logger.warning("Translation returned empty or same result, returning original text")
                    return text
            else:
                logger.warning(
                    "MyMemory API returned status %d for %s->%s, returning original text",
                    result.get('responseStatus'), src_code, dest_code
                )
                return text
        else:
            logger.warning(
                "MyMemory API returned HTTP status %d for %s->%s, returning original text",
                response.status_code, src_code, dest_code
            )
            return text
            
    except requests.exceptions.Timeout:
        logger.warning("MyMemory API timeout for %s->%s, returning original text", src_code, dest_code)
        return text
    except requests.exceptions.ConnectionError as e:
        logger.warning("Connection error to MyMemory API: %s, returning original text", str(e))
        return text
    except Exception as e:  # pylint: disable=broad-except
        # Log error and return original text
        logger.warning("Translation error for %s->%s: %s, returning original text", src_code, dest_code, str(e))
        return text
