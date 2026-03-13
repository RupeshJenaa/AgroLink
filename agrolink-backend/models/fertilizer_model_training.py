"""
Fertilizer Recommendation Model Training

This script trains a machine learning model to recommend fertilizers based on:
- Environmental factors: Temperature, Humidity, Moisture
- Soil characteristics: Soil Type
- Crop information: Crop Type
- Nutrient levels: Nitrogen, Potassium, Phosphorous

The model uses the Fertilizer Prediction.csv dataset provided.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_fertilizer_model():
    """Train and save the fertilizer recommendation model"""
    
    # Get the path to the dataset (in project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(backend_dir)
    dataset_path = os.path.join(project_root, 'Fertilizer Prediction.csv')
    
    print(f"Loading dataset from: {dataset_path}")
    
    # Load the dataset
    df = pd.read_csv(dataset_path)
    
    # Display basic information
    print("\n" + "="*50)
    print("Dataset Information")
    print("="*50)
    print(f"Total samples: {len(df)}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
    
    # Check for missing values
    print(f"\nMissing values:")
    print(df.isnull().sum())
    
    # Clean column names (remove spaces and fix spelling)
    df.columns = df.columns.str.strip()
    if 'Temparature' in df.columns:
        df.rename(columns={'Temparature': 'Temperature'}, inplace=True)
    
    # Separate features and target
    features = ['Temperature', 'Humidity', 'Moisture', 'Soil Type', 
                'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous']
    target = 'Fertilizer Name'
    
    X = df[features].copy()
    y = df[target].copy()
    
    print(f"\n" + "="*50)
    print("Unique values in categorical columns")
    print("="*50)
    print(f"Soil Types: {X['Soil Type'].unique()}")
    print(f"Crop Types: {X['Crop Type'].unique()}")
    print(f"Fertilizers: {y.unique()}")
    
    # Encode categorical variables
    label_encoders = {}
    
    # Encode Soil Type
    le_soil = LabelEncoder()
    X['Soil Type'] = le_soil.fit_transform(X['Soil Type'])
    label_encoders['soil_type'] = le_soil
    
    # Encode Crop Type
    le_crop = LabelEncoder()
    X['Crop Type'] = le_crop.fit_transform(X['Crop Type'])
    label_encoders['crop_type'] = le_crop
    
    # Encode target (Fertilizer Name)
    le_fertilizer = LabelEncoder()
    y_encoded = le_fertilizer.fit_transform(y)
    label_encoders['fertilizer'] = le_fertilizer
    
    print(f"\n" + "="*50)
    print("Encoded Features Sample")
    print("="*50)
    print(X.head())
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n" + "="*50)
    print("Train/Test Split")
    print("="*50)
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Train Random Forest Classifier
    print(f"\n" + "="*50)
    print("Training Random Forest Model")
    print("="*50)
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_accuracy = accuracy_score(y_train, y_pred_train)
    test_accuracy = accuracy_score(y_test, y_pred_test)
    
    print(f"\nTraining Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    print(f"Testing Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    print(f"\n" + "="*50)
    print("Classification Report (Test Set)")
    print("="*50)
    print(classification_report(y_test, y_pred_test, 
                                target_names=le_fertilizer.classes_))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n" + "="*50)
    print("Feature Importance")
    print("="*50)
    print(feature_importance)
    
    # Save the model and encoders
    models_dir = os.path.join(backend_dir, 'models')
    
    model_path = os.path.join(models_dir, 'fertilizer_recommendation_model.pkl')
    encoders_path = os.path.join(models_dir, 'fertilizer_label_encoders.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(label_encoders, encoders_path)
    
    print(f"\n" + "="*50)
    print("Model Saved Successfully")
    print("="*50)
    print(f"Model: {model_path}")
    print(f"Encoders: {encoders_path}")
    
    # Test prediction
    print(f"\n" + "="*50)
    print("Sample Prediction Test")
    print("="*50)
    
    # Example: Wheat crop, Loamy soil, Temperature: 30°C, Humidity: 60%, 
    # Moisture: 40%, N:20, P:10, K:15
    sample_data = pd.DataFrame({
        'Temperature': [30],
        'Humidity': [60],
        'Moisture': [40],
        'Soil Type': [le_soil.transform(['Loamy'])[0]],
        'Crop Type': [le_crop.transform(['Wheat'])[0]],
        'Nitrogen': [20],
        'Potassium': [15],
        'Phosphorous': [10]
    })
    
    prediction = model.predict(sample_data)
    prediction_proba = model.predict_proba(sample_data)
    
    recommended_fertilizer = le_fertilizer.inverse_transform(prediction)[0]
    confidence = np.max(prediction_proba) * 100
    
    print(f"Input: Wheat, Loamy soil, 30°C, 60% humidity, 40% moisture")
    print(f"       N:20, P:10, K:15")
    print(f"Recommended Fertilizer: {recommended_fertilizer}")
    print(f"Confidence: {confidence:.2f}%")
    
    return model, label_encoders, test_accuracy

if __name__ == "__main__":
    print("="*50)
    print("FERTILIZER RECOMMENDATION MODEL TRAINING")
    print("="*50)
    
    model, encoders, accuracy = train_fertilizer_model()
    
    print(f"\n" + "="*50)
    print("Training Complete!")
    print(f"Final Test Accuracy: {accuracy*100:.2f}%")
    print("="*50)
