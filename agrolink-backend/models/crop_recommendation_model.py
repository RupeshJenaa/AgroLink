import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

def train_crop_recommendation_model():
    """
    Train a crop recommendation model using the dataset
    """
    # Resolve dataset path dynamically from script location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(backend_dir)
    dataset_path = os.path.join(project_root, 'Crop_recommendation.csv')

    # Load the dataset
    data = pd.read_csv(dataset_path)
    
    # Separate features and target
    X = data.drop('label', axis=1)
    y = data['label']
    
    # Encode the target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Save the model and preprocessing objects
    joblib.dump(model, 'crop_recommendation_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    
    print("\nModel and preprocessing objects saved successfully!")
    
    return model, scaler, label_encoder

def predict_crop(model, scaler, label_encoder, N, P, K, temperature, humidity, ph, rainfall):
    """
    Predict the crop based on input parameters
    """
    # Create input array
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Scale the input
    input_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction = model.predict(input_scaled)
    prediction_proba = model.predict_proba(input_scaled)
    
    # Get the crop name
    crop_name = label_encoder.inverse_transform(prediction)[0]
    
    # Get confidence score
    confidence = np.max(prediction_proba) * 100
    
    return crop_name, confidence

if __name__ == "__main__":
    # Train the model
    model, scaler, label_encoder = train_crop_recommendation_model()
    
    # Example prediction
    crop, confidence = predict_crop(model, scaler, label_encoder, 90, 42, 43, 20.8, 82.0, 6.5, 202.9)
    print(f"\nExample prediction: {crop} (Confidence: {confidence:.2f}%)")