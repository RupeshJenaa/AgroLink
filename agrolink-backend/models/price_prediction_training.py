"""
Price Prediction Model Training

Trains a model to predict crop market prices based on:
- Crop type (any crop, uses a default price for unknown ones)
- Quantity (in kg)
- Location/State (all 28 Indian states + UTs)
- Season/Month

The model uses OrdinalEncoder instead of LabelEncoder so unknown
crops and states can be handled gracefully via a fallback.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# ─── Comprehensive Crop List ───────────────────────────────────────────────
# Covers major kharif, rabi, horticultural and cash crops
ALL_CROPS = [
    # Cereals
    'Rice', 'Wheat', 'Maize', 'Barley', 'Millets', 'Sorghum', 'Paddy',
    'Oats', 'Ragi', 'Jowar', 'Bajra', 'Finger Millet',
    # Pulses
    'Pulses', 'Lentils', 'Chickpea', 'Pigeon Pea', 'Moong Dal',
    'Urad Dal', 'Black Gram', 'Green Gram', 'Kidney Beans',
    # Oilseeds & Cash Crops
    'Groundnut', 'Ground Nuts', 'Soybean', 'Sunflower', 'Mustard',
    'Sesame', 'Castor', 'Linseed', 'Cotton', 'Sugarcane', 'Jute',
    'Tobacco', 'Oil seeds',
    # Vegetables
    'Tomato', 'Potato', 'Onion', 'Brinjal', 'Cabbage', 'Cauliflower',
    'Carrot', 'Radish', 'Peas', 'Spinach', 'Okra', 'Bitter Gourd',
    'Bottle Gourd', 'Pumpkin', 'Cucumber', 'Capsicum', 'Garlic', 'Ginger',
    # Fruits
    'Banana', 'Mango', 'Apple', 'Grapes', 'Pomegranate', 'Guava',
    'Papaya', 'Citrus', 'Pineapple', 'Watermelon', 'Muskmelon',
    # Spices & Plantation
    'Turmeric', 'Pepper', 'Cardamom', 'Coriander', 'Cumin',
    'Chilli', 'Clove', 'Coconut', 'Arecanut', 'Cashew',
    # Flowers
    'Rose', 'Jasmine', 'Marigold',
]

# Base prices for crops (INR per kg)
BASE_PRICES = {
    'Rice': 25, 'Wheat': 22, 'Maize': 18, 'Barley': 20, 'Millets': 30,
    'Sorghum': 22, 'Paddy': 20, 'Oats': 28, 'Ragi': 32, 'Jowar': 20,
    'Bajra': 18, 'Finger Millet': 30, 'Pulses': 70, 'Lentils': 75,
    'Chickpea': 65, 'Pigeon Pea': 80, 'Moong Dal': 85, 'Urad Dal': 90,
    'Black Gram': 80, 'Green Gram': 75, 'Kidney Beans': 100,
    'Groundnut': 55, 'Ground Nuts': 55, 'Soybean': 45, 'Sunflower': 50,
    'Mustard': 55, 'Sesame': 120, 'Castor': 60, 'Linseed': 65,
    'Cotton': 60, 'Sugarcane': 3, 'Jute': 40, 'Tobacco': 120,
    'Oil seeds': 50, 'Tomato': 20, 'Potato': 15, 'Onion': 18,
    'Brinjal': 22, 'Cabbage': 12, 'Cauliflower': 25, 'Carrot': 30,
    'Radish': 15, 'Peas': 40, 'Spinach': 20, 'Okra': 35,
    'Bitter Gourd': 40, 'Bottle Gourd': 18, 'Pumpkin': 15,
    'Cucumber': 20, 'Capsicum': 60, 'Garlic': 100, 'Ginger': 80,
    'Banana': 25, 'Mango': 50, 'Apple': 120, 'Grapes': 80,
    'Pomegranate': 100, 'Guava': 30, 'Papaya': 20, 'Citrus': 35,
    'Pineapple': 40, 'Watermelon': 12, 'Muskmelon': 22,
    'Turmeric': 90, 'Pepper': 400, 'Cardamom': 1200, 'Coriander': 100,
    'Cumin': 200, 'Chilli': 120, 'Clove': 600, 'Coconut': 30,
    'Arecanut': 400, 'Cashew': 800, 'Rose': 150, 'Jasmine': 200,
    'Marigold': 50,
}
DEFAULT_PRICE = 40  # fallback for any crop not in the dict

# ─── All 28 Indian States + Major UTs ──────────────────────────────────────
ALL_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
    'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    # Union Territories
    'Delhi', 'Jammu And Kashmir', 'Ladakh', 'Chandigarh',
    'Dadra And Nagar Haveli', 'Daman And Diu', 'Lakshadweep',
    'Puducherry', 'Andaman And Nicobar Islands',
]

# Regional price multiplier (captures regional market realities)
STATE_MULTIPLIER = {
    'Punjab': 1.10, 'Haryana': 1.08, 'Uttar Pradesh': 1.00,
    'Maharashtra': 1.05, 'Karnataka': 1.02, 'Tamil Nadu': 1.03,
    'Andhra Pradesh': 1.02, 'Telangana': 1.02, 'West Bengal': 0.98,
    'Gujarat': 1.06, 'Rajasthan': 0.97, 'Madhya Pradesh': 0.96,
    'Bihar': 0.94, 'Odisha': 0.93, 'Jharkhand': 0.92,
    'Chhattisgarh': 0.93, 'Kerala': 1.08, 'Himachal Pradesh': 1.05,
    'Uttarakhand': 1.02, 'Assam': 0.95, 'Arunachal Pradesh': 0.92,
    'Manipur': 0.90, 'Meghalaya': 0.91, 'Mizoram': 0.89,
    'Nagaland': 0.88, 'Tripura': 0.91, 'Sikkim': 0.94, 'Goa': 1.10,
    'Delhi': 1.15, 'Jammu And Kashmir': 1.03, 'Ladakh': 1.00,
    'Chandigarh': 1.12, 'Dadra And Nagar Haveli': 1.00,
    'Daman And Diu': 1.01, 'Lakshadweep': 1.10, 'Puducherry': 1.05,
    'Andaman And Nicobar Islands': 1.08,
}


def create_dataset():
    """Generate a comprehensive synthetic dataset for training."""
    np.random.seed(42)
    n_samples = 5000
    data = []

    for _ in range(n_samples):
        crop = np.random.choice(ALL_CROPS)
        state = np.random.choice(ALL_STATES)
        month = np.random.randint(1, 13)
        quantity = np.random.randint(50, 20000)

        base = BASE_PRICES.get(crop, DEFAULT_PRICE)
        state_mult = STATE_MULTIPLIER.get(state, 1.0)
        seasonal = 1 + 0.12 * np.sin(2 * np.pi * month / 12)
        qty_discount = 1 - min((quantity / 100000) * 0.15, 0.12)
        noise = np.random.normal(1, 0.12)

        price = base * state_mult * seasonal * qty_discount * noise
        price = max(price, base * 0.4)

        data.append({
            'crop_type': crop,
            'state': state,
            'month': month,
            'quantity': quantity,
            'price_per_kg': round(price, 2)
        })

    return pd.DataFrame(data)


def train_price_prediction_model():
    print("=" * 50)
    print("PRICE PREDICTION MODEL TRAINING")
    print("=" * 50)

    df = create_dataset()
    print(f"\nDataset: {len(df)} samples")
    print(f"Unique crops: {df['crop_type'].nunique()}")
    print(f"Unique states: {df['state'].nunique()}")

    X = df[['crop_type', 'state', 'month', 'quantity']].copy()
    y = df['price_per_kg'].copy()

    # OrdinalEncoder handles unknown categories gracefully
    enc_crop = OrdinalEncoder(
        handle_unknown='use_encoded_value',
        unknown_value=-1
    )
    enc_state = OrdinalEncoder(
        handle_unknown='use_encoded_value',
        unknown_value=-1
    )

    X = X.copy()
    X['crop_type'] = enc_crop.fit_transform(X[['crop_type']]).flatten()
    X['state'] = enc_state.fit_transform(X[['state']]).flatten()

    # Store known base prices and default per-category averages for router fallback
    crop_avg = df.groupby('crop_type')['price_per_kg'].mean().to_dict()
    state_avg = df.groupby('state')['price_per_kg'].mean().to_dict()
    overall_avg = float(y.mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    test_mae = mean_absolute_error(y_test, model.predict(X_test))
    test_r2 = r2_score(y_test, model.predict(X_test))
    print(f"\nTest MAE: Rs.{test_mae:.2f}/kg  |  R²: {test_r2:.4f}")

    # Save
    models_dir = os.path.dirname(os.path.abspath(__file__))
    joblib.dump(model, os.path.join(models_dir, 'price_prediction_model.pkl'))
    joblib.dump({
        'crop': enc_crop,
        'state': enc_state,
        'crop_avg': crop_avg,
        'state_avg': state_avg,
        'overall_avg': overall_avg,
        'base_prices': BASE_PRICES,
        'default_price': DEFAULT_PRICE,
        'state_multiplier': STATE_MULTIPLIER,
        'all_crops': ALL_CROPS,
        'all_states': ALL_STATES,
    }, os.path.join(models_dir, 'price_label_encoders.pkl'))

    print("\nModel and encoders saved successfully!")
    print(f"Crops supported: {len(ALL_CROPS)}")
    print(f"States supported: {len(ALL_STATES)}")
    return model, enc_crop, enc_state, test_r2


if __name__ == "__main__":
    model, enc_crop, enc_state, r2 = train_price_prediction_model()
    print(f"\nTraining Complete! R²: {r2:.4f}")
