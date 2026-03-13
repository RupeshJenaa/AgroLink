from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
from chatbot.translator import translate_text

# Create router
crop_router = APIRouter()

# Load the trained model and preprocessing objects
model_path = os.path.join(os.path.dirname(__file__), '..', 'models')
model = joblib.load(os.path.join(model_path, 'crop_recommendation_model.pkl'))
scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
label_encoder = joblib.load(os.path.join(model_path, 'label_encoder.pkl'))

class CropRecommendationRequest(BaseModel):
    nitrogen: float
    phosphorous: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class CropRecommendationResponse(BaseModel):
    recommended_crop: str
    confidence: float

@crop_router.post("/predict", response_model=CropRecommendationResponse)
async def predict_crop(request: CropRecommendationRequest, lang: str = "en"):
    try:
        # Create input array
        input_data = np.array([[
            request.nitrogen,
            request.phosphorous,
            request.potassium,
            request.temperature,
            request.humidity,
            request.ph,
            request.rainfall
        ]])
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = model.predict(input_scaled)
        prediction_proba = model.predict_proba(input_scaled)
        
        # Get the crop name
        crop_name = label_encoder.inverse_transform(prediction)[0]
        
        # Get confidence score
        confidence = float(np.max(prediction_proba) * 100)
        
        # Translate if necessary
        translated_crop = translate_text(crop_name, "en", lang)
        
        return CropRecommendationResponse(
            recommended_crop=translated_crop,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}") from e