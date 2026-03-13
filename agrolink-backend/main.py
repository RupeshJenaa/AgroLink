from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.router import chatbot_router
from crop.router import crop_router
from fertilizer.router import fertilizer_router
from price.router import price_router
from disease.router import disease_router
from firebase_config import initialize_firebase

app = FastAPI(title="AgroLink API", version="2.0.0")

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Firebase Admin SDK on application startup"""
    try:
        initialize_firebase()
        print("✓ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Firebase initialization failed: {str(e)}")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(crop_router, prefix="/api/crop", tags=["Crop Recommendation"])
app.include_router(fertilizer_router, prefix="/api/fertilizer", tags=["Fertilizer Recommendation"])
app.include_router(price_router, prefix="/api/price", tags=["Price Prediction"])
app.include_router(disease_router, prefix="/api/disease", tags=["Plant Disease Prediction"])

@app.get("/")
def root():
    return {
        "message": "AgroLink backend is running!",
        "version": "2.0.0",
        "features": ["chatbot", "crop_recommendation", "fertilizer_recommendation", "price_prediction", "authentication"]
    }