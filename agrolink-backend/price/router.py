"""
Price Prediction API Router

Provides endpoints for:
- Predicting crop market prices  
- Recording actual sale prices (to improve the model)
- Fetching historical price data
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
import os

from auth.dependencies import require_farmer, require_authenticated, CurrentUser
from firebase_config import get_db
from chatbot.translator import translate_text

# Create router
price_router = APIRouter()

# Load the trained model and encoders
model_path = os.path.join(os.path.dirname(__file__), '..', 'models')

try:
    model = joblib.load(os.path.join(model_path, 'price_prediction_model.pkl'))
    encoders = joblib.load(os.path.join(model_path, 'price_label_encoders.pkl'))
    # Support both old (LabelEncoder dict) and new (OrdinalEncoder dict) formats
    enc_crop = encoders.get('crop')
    enc_state = encoders.get('state')
    crop_avg = encoders.get('crop_avg', {})
    state_avg = encoders.get('state_avg', {})
    overall_avg = encoders.get('overall_avg', 30.0)
    base_prices = encoders.get('base_prices', {})
    default_price = encoders.get('default_price', 40)
    state_multiplier = encoders.get('state_multiplier', {})
    ALL_CROPS = encoders.get('all_crops', [])
    ALL_STATES = encoders.get('all_states', [])
    print("✓ Price prediction model loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load price prediction model: {str(e)}")
    model = None
    enc_crop = enc_state = None
    crop_avg = state_avg = {}
    overall_avg = 30.0
    base_prices = {}
    default_price = 40
    state_multiplier = {}
    ALL_CROPS = []
    ALL_STATES = []

class PricePredictionRequest(BaseModel):
    """Request model for price prediction"""
    crop_type: str = Field(..., description="Type of crop")
    quantity: float = Field(..., description="Quantity in kg", gt=0)
    state: str = Field(..., description="State/Location")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "crop_type": "Wheat",
                "quantity": 1000,
                "state": "Punjab"
            }
        }
    }

class PricePredictionResponse(BaseModel):
    """Response model for price prediction"""
    crop_type: str
    quantity: float
    state: str
    predicted_price_per_kg: float
    predicted_total_value: float
    confidence_interval_low: float
    confidence_interval_high: float
    historical_average: Optional[float] = None
    current_month: int
    prediction_date: str

class PriceRecordRequest(BaseModel):
    """Request model for recording actual sale price"""
    crop_type: str
    quantity: float = Field(..., gt=0)
    actual_price_per_kg: float = Field(..., gt=0)
    state: str
    sale_date: Optional[str] = None
    notes: Optional[str] = None

class HistoricalPriceData(BaseModel):
    """Historical price data point"""
    crop_type: str
    price_per_kg: float
    quantity: float
    state: str
    date: str
    farmer_id: str

@price_router.post("/predict", response_model=PricePredictionResponse)
async def predict_price(
    request: PricePredictionRequest,
    current_user: CurrentUser = Depends(require_farmer),
    lang: str = "en"
):
    """
    Predict crop market price. Accepts any crop name and any Indian state.
    Unknown crops/states fall back to average-based pricing.
    """
    if model is None or enc_crop is None:
        raise HTTPException(
            status_code=503,
            detail="Price prediction model is not available. Please train the model first."
        )

    try:
        normalized_crop = request.crop_type.strip().title()
        normalized_state = request.state.strip().title()
        current_month = datetime.now().month

        # ── Encode crop ───────────────────────────────────────────────────
        # OrdinalEncoder returns -1 for unknown; LabelEncoder raises ValueError
        crop_is_known = True
        try:
            # Try OrdinalEncoder path first
            crop_encoded = enc_crop.transform([[normalized_crop]])[0][0]
            if crop_encoded == -1:          # unknown to OrdinalEncoder
                crop_is_known = False
                crop_encoded = 0            # use index 0 as proxy; price overridden below
        except AttributeError:
            # Old LabelEncoder path
            try:
                crop_encoded = enc_crop.transform([normalized_crop])[0]
            except ValueError:
                crop_is_known = False
                crop_encoded = 0

        # ── Encode state ──────────────────────────────────────────────────
        state_is_known = True
        try:
            state_encoded = enc_state.transform([[normalized_state]])[0][0]
            if state_encoded == -1:
                state_is_known = False
                state_encoded = 0
        except AttributeError:
            try:
                state_encoded = enc_state.transform([normalized_state])[0]
            except ValueError:
                state_is_known = False
                state_encoded = 0

        # ── Predict ───────────────────────────────────────────────────────
        input_data = pd.DataFrame({
            'crop_type': [float(crop_encoded)],
            'state': [float(state_encoded)],
            'month': [current_month],
            'quantity': [request.quantity]
        })
        predicted_price = float(model.predict(input_data)[0])

        # ── Override predicted price for unknown crop using base price ─────
        # This ensures even a new crop the user types gets a sensible price.
        if not crop_is_known:
            # Use saved base_prices dict, or fall back to overall average
            raw_base = base_prices.get(normalized_crop, default_price)
            s_mult = state_multiplier.get(normalized_state, 1.0)
            seasonal = 1 + 0.10 * __import__('math').sin(2 * 3.14159 * current_month / 12)
            qty_discount = 1 - min((request.quantity / 100000) * 0.12, 0.10)
            predicted_price = raw_base * s_mult * seasonal * qty_discount

        confidence_margin = predicted_price * 0.15
        confidence_low = float(max(0, predicted_price - confidence_margin))
        confidence_high = float(predicted_price + confidence_margin)
        total_value = float(predicted_price * request.quantity)

        # ── Historical average from Firestore ─────────────────────────────
        historical_avg = None
        try:
            db = get_db()
            prices_ref = db.collection('market_prices')
            query = prices_ref.where('crop_type', '==', request.crop_type).limit(20)
            docs = query.stream()
            prices = [doc.to_dict().get('price_per_kg', 0) for doc in docs]
            if prices:
                historical_avg = sum(prices) / len(prices)
        except Exception as e:
            print(f"Could not fetch historical prices: {str(e)}")

        return PricePredictionResponse(
            crop_type=translate_text(request.crop_type, "en", lang),
            quantity=request.quantity,
            state=translate_text(request.state, "en", lang),
            predicted_price_per_kg=round(predicted_price, 2),
            predicted_total_value=round(total_value, 2),
            confidence_interval_low=round(confidence_low, 2),
            confidence_interval_high=round(confidence_high, 2),
            historical_average=round(historical_avg, 2) if historical_avg else None,
            current_month=current_month,
            prediction_date=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making price prediction: {str(e)}"
        )

@price_router.post("/record")
async def record_price(
    request: PriceRecordRequest,
    current_user: CurrentUser = Depends(require_farmer)
):
    """
    Record actual sale price to build historical data.
    Only accessible to farmers.
    """
    try:
        db = get_db()
        
        # Parse sale date or use current date
        if request.sale_date:
            try:
                sale_date = datetime.fromisoformat(request.sale_date)
            except:
                sale_date = datetime.now()
        else:
            sale_date = datetime.now()
        
        # Create price record
        price_data = {
            'crop_type': request.crop_type,
            'quantity': request.quantity,
            'price_per_kg': request.actual_price_per_kg,
            'total_value': request.quantity * request.actual_price_per_kg,
            'state': request.state,
            'farmer_id': current_user.uid,
            'farmer_email': current_user.email,
            'sale_date': sale_date,
            'month': sale_date.month,
            'year': sale_date.year,
            'recorded_at': datetime.now(),
            'notes': request.notes
        }
        
        # Add to Firestore
        db.collection('market_prices').add(price_data)
        
        return {
            "success": True,
            "message": "Price data recorded successfully",
            "data": {
                "crop_type": request.crop_type,
                "price_per_kg": request.actual_price_per_kg,
                "total_value": price_data['total_value']
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error recording price: {str(e)}"
        )

@price_router.get("/history/{crop_type}")
async def get_price_history(
    crop_type: str,
    limit: int = 50,
    current_user: CurrentUser = Depends(require_authenticated)
):
    """
    Get historical price data for a specific crop.
    Accessible to all authenticated users.
    """
    try:
        db = get_db()
        
        # Query Firestore for price history
        prices_ref = db.collection('market_prices')
        query = prices_ref.where('crop_type', '==', crop_type)\
                         .order_by('sale_date', direction='DESCENDING')\
                         .limit(limit)
        
        docs = query.stream()
        
        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append({
                'price_per_kg': data.get('price_per_kg'),
                'quantity': data.get('quantity'),
                'state': data.get('state'),
                'date': data.get('sale_date').isoformat() if data.get('sale_date') else None,
                'month': data.get('month'),
                'year': data.get('year')
            })
        
        if not history:
            return {
                "crop_type": crop_type,
                "message": "No historical data available for this crop yet",
                "history": []
            }
        
        # Calculate statistics
        prices = [h['price_per_kg'] for h in history]
        
        return {
            "crop_type": crop_type,
            "total_records": len(history),
            "average_price": round(sum(prices) / len(prices), 2),
            "min_price": round(min(prices), 2),
            "max_price": round(max(prices), 2),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching price history: {str(e)}"
        )

@price_router.get("/crops")
async def get_available_crops():
    """Get full list of crops for which price prediction is available"""
    return {"crops": sorted(ALL_CROPS)}


@price_router.get("/states")
async def get_available_states():
    """Get full list of all Indian states for price prediction"""
    return {"states": sorted(ALL_STATES)}
