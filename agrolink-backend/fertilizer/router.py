"""
Fertilizer Recommendation API Router

Provides endpoint to recommend fertilizers based on:
- Environmental conditions (temperature, humidity, moisture)
- Soil type
- Crop type
- Current nutrient levels (NPK)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import joblib
import numpy as np
import pandas as pd
import os
from chatbot.translator import translate_text

# Create router
fertilizer_router = APIRouter()

# Load the trained model and encoders
model_path = os.path.join(os.path.dirname(__file__), '..', 'models')

try:
    model = joblib.load(os.path.join(model_path, 'fertilizer_recommendation_model.pkl'))
    label_encoders = joblib.load(os.path.join(model_path, 'fertilizer_label_encoders.pkl'))
    print("✓ Fertilizer recommendation model loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load fertilizer model: {str(e)}")
    model = None
    label_encoders = None

class FertilizerRequest(BaseModel):
    """Request model for fertilizer recommendation"""
    temperature: float = Field(..., description="Temperature in Celsius", ge=-10, le=60)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    moisture: float = Field(..., description="Soil moisture percentage", ge=0, le=100)
    soil_type: str = Field(..., description="Soil type (Sandy, Loamy, Black, Red, Clayey)")
    crop_type: str = Field(..., description="Crop type")
    nitrogen: float = Field(..., description="Nitrogen content", ge=0)
    potassium: float = Field(..., description="Potassium content", ge=0)
    phosphorous: float = Field(..., description="Phosphorous content", ge=0)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "temperature": 30,
                "humidity": 60,
                "moisture": 40,
                "soil_type": "Loamy",
                "crop_type": "Wheat",
                "nitrogen": 20,
                "potassium": 15,
                "phosphorous": 10
            }
        }
    }

class FertilizerResponse(BaseModel):
    """Response model for fertilizer recommendation"""
    recommended_fertilizer: str
    confidence: float
    soil_type: str
    crop_type: str
    alternative_fertilizers: Optional[List[dict]] = None
    usage_tips: Optional[str] = None

# Fertilizer usage information
FERTILIZER_INFO = {
    "Urea": {
        "description": "High nitrogen fertilizer (46% N)",
        "usage": "Apply 2-3 weeks after planting. Water immediately after application.",
        "benefits": "Promotes vegetative growth and green foliage"
    },
    "DAP": {
        "description": "Di-ammonium Phosphate (18% N, 46% P)",
        "usage": "Apply at the time of sowing or planting.",
        "benefits": "Excellent for root development and early plant growth"
    },
    "10-26-26": {
        "description": "Balanced NPK (10% N, 26% P, 26% K)",
        "usage": "Apply during soil preparation or as basal dose.",
        "benefits": "Good for flowering and fruiting stages"
    },
    "14-35-14": {
        "description": "High phosphorus NPK (14% N, 35% P, 14% K)",
        "usage": "Apply at the time of planting.",
        "benefits": "Promotes strong root system and early growth"
    },
    "17-17-17": {
        "description": "Balanced NPK (17% N, 17% P, 17% K)",
        "usage": "Apply as per crop requirement throughout growing season.",
        "benefits": "Suitable for most crops, balanced nutrition"
    },
    "20-20": {
        "description": "Nitrogen-Phosphorus fertilizer (20% N, 20% P)",
        "usage": "Apply during active growth phase.",
        "benefits": "Good for vegetative and root growth"
    },
    "28-28": {
        "description": "High NP fertilizer (28% N, 28% P)",
        "usage": "Apply in split doses during growth stages.",
        "benefits": "Boosts both foliage and root development"
    }
}

@fertilizer_router.post("/recommend", response_model=FertilizerResponse)
async def recommend_fertilizer(request: FertilizerRequest, lang: str = "en"):
    """
    Get fertilizer recommendation based on soil, crop, and environmental conditions.
    
    Returns the most suitable fertilizer with confidence score and usage tips.
    """
    if model is None or label_encoders is None:
        raise HTTPException(
            status_code=503,
            detail="Fertilizer recommendation model is not available. Please ensure the model is trained."
        )
    
    try:
        # Get label encoders
        le_soil = label_encoders['soil_type']
        le_crop = label_encoders['crop_type']
        le_fertilizer = label_encoders['fertilizer']
        
        # Validate and encode soil type
        try:
            soil_encoded = le_soil.transform([request.soil_type])[0]
        except ValueError:
            valid_soils = ', '.join(le_soil.classes_)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid soil type '{request.soil_type}'. Valid options: {valid_soils}"
            )
        
        # Validate and encode crop type
        try:
            crop_encoded = le_crop.transform([request.crop_type])[0]
        except ValueError:
            valid_crops = ', '.join(le_crop.classes_)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid crop type '{request.crop_type}'. Valid options: {valid_crops}"
            )
        
        # Create input dataframe
        input_data = pd.DataFrame({
            'Temperature': [request.temperature],
            'Humidity': [request.humidity],
            'Moisture': [request.moisture],
            'Soil Type': [soil_encoded],
            'Crop Type': [crop_encoded],
            'Nitrogen': [request.nitrogen],
            'Potassium': [request.potassium],
            'Phosphorous': [request.phosphorous]
        })
        
        # Make prediction
        prediction = model.predict(input_data)
        prediction_proba = model.predict_proba(input_data)[0]
        
        # Get recommended fertilizer
        recommended_fertilizer = le_fertilizer.inverse_transform(prediction)[0]
        confidence = float(np.max(prediction_proba) * 100)
        
        # Get alternative recommendations (top 3)
        top_3_indices = np.argsort(prediction_proba)[-3:][::-1]
        alternatives = []
        
        for idx in top_3_indices[1:]:  # Skip the first one as it's the main recommendation
            fert_name = le_fertilizer.inverse_transform([idx])[0]
            fert_confidence = float(prediction_proba[idx] * 100)
            if fert_confidence > 5:  # Only include if confidence > 5%
                alternatives.append({
                    "name": translate_text(fert_name, "en", lang),
                    "confidence": round(fert_confidence, 2)
                })
        
        # Get usage tips
        usage_tips = None
        if recommended_fertilizer in FERTILIZER_INFO:
            info = FERTILIZER_INFO[recommended_fertilizer]
            usage_tips = f"{info['description']}. {info['usage']} {info['benefits']}."
            usage_tips = translate_text(usage_tips, "en", lang)
        
        return FertilizerResponse(
            recommended_fertilizer=translate_text(recommended_fertilizer, "en", lang),
            confidence=round(confidence, 2),
            soil_type=translate_text(request.soil_type, "en", lang),
            crop_type=translate_text(request.crop_type, "en", lang),
            alternative_fertilizers=alternatives if alternatives else None,
            usage_tips=usage_tips
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making fertilizer recommendation: {str(e)}"
        )

@fertilizer_router.get("/soil-types")
async def get_soil_types():
    """Get list of valid soil types"""
    if label_encoders is None:
        return {"soil_types": ["Sandy", "Loamy", "Black", "Red", "Clayey"]}
    return {"soil_types": label_encoders['soil_type'].classes_.tolist()}

@fertilizer_router.get("/crop-types")
async def get_crop_types():
    """Get list of valid crop types"""
    if label_encoders is None:
        return {"crop_types": []}
    return {"crop_types": label_encoders['crop_type'].classes_.tolist()}

@fertilizer_router.get("/fertilizer-info/{fertilizer_name}")
async def get_fertilizer_info(fertilizer_name: str):
    """Get detailed information about a specific fertilizer"""
    if fertilizer_name in FERTILIZER_INFO:
        return {
            "name": fertilizer_name,
            **FERTILIZER_INFO[fertilizer_name]
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Information not available for fertilizer: {fertilizer_name}"
        )
