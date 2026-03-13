"""
Plant Disease Prediction Model Training Script

Uses a Random Forest classifier on a synthetic feature set derived from image
color statistics (mean/std of R,G,B channels + derived features). In production,
replace with a CNN trained on PlantVillage dataset using TensorFlow/Keras.

This lightweight approach still allows the API to function properly for a demo.
Run this script once to generate disease_model.pkl and disease_class_labels.json.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import json
import os

# ─────────────────────────────────────────────
# Disease class definitions (PlantVillage-style)
# ─────────────────────────────────────────────
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Corn_(maize)___Cercospora_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Rice___Brown_spot",
    "Rice___Leaf_blast",
    "Rice___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
    "Wheat___Brown_Rust",
    "Wheat___Yellow_Rust",
    "Wheat___healthy",
]

TREATMENT_MAP = {
    "Apple___Apple_scab": "Apply fungicides like Captan or Mancozeb. Remove infected leaves. Ensure good air circulation.",
    "Apple___Black_rot": "Prune infected branches. Apply Bordeaux mixture. Remove mummified fruit.",
    "Apple___Cedar_apple_rust": "Apply protective fungicides in spring. Remove nearby cedar/juniper trees if possible.",
    "Apple___healthy": "Plant is healthy! Continue regular watering and fertilization.",
    "Corn_(maize)___Cercospora_leaf_spot": "Apply fungicides like Azoxystrobin. Rotate crops. Use resistant varieties.",
    "Corn_(maize)___Common_rust_": "Apply Mancozeb fungicide. Use resistant hybrid seeds. Avoid overhead irrigation.",
    "Corn_(maize)___Northern_Leaf_Blight": "Apply Propiconazole fungicide. Use resistant varieties. Crop rotation.",
    "Corn_(maize)___healthy": "Plant is healthy! Continue regular watering and fertilization.",
    "Grape___Black_rot": "Apply Myclobutanil or Mancozeb. Remove infected clusters. Good canopy management.",
    "Grape___Esca_(Black_Measles)": "Prune infected wood. Apply Trichoderma biocontrol. Wound protectants after pruning.",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Apply copper-based fungicides. Improve air circulation. Destroy fallen leaves.",
    "Grape___healthy": "Plant is healthy! Continue regular care.",
    "Potato___Early_blight": "Apply Chlorothalonil. Ensure adequate soil nutrition. Remove infected leaves.",
    "Potato___Late_blight": "Apply Metalaxyl fungicide immediately. Avoid overhead watering. Remove infected plants.",
    "Potato___healthy": "Plant is healthy! Continue regular care.",
    "Rice___Brown_spot": "Apply Iprobenfos or Tricyclazole. Proper fertilization with potassium. Drain fields periodically.",
    "Rice___Leaf_blast": "Apply Tricyclazole immediately. Avoid excess nitrogen. Use resistant varieties.",
    "Rice___healthy": "Plant is healthy! Continue regular paddy care.",
    "Tomato___Bacterial_spot": "Apply copper-based bactericides. Avoid working with wet plants. Use certified disease-free seeds.",
    "Tomato___Early_blight": "Apply Mancozeb or Chlorothalonil. Remove lower infected leaves. Mulch around plants.",
    "Tomato___Late_blight": "Apply Metalaxyl + Mancozeb immediately. Destroy infected plants. Avoid overhead irrigation.",
    "Tomato___Leaf_Mold": "Improve ventilation. Apply fungicides like Chlorothalonil. Avoid wetting foliage.",
    "Tomato___Septoria_leaf_spot": "Apply copper or Mancozeb fungicides. Remove infected leaves. Crop rotation.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Apply Abamectin or insecticidal soap. Increase humidity. Introduce predatory mites.",
    "Tomato___Target_Spot": "Apply Chlorothalonil or Azoxystrobin. Remove infected lower leaves. Maintain good nutrition.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whitefly vectors with insecticides. Use reflective mulch. Remove infected plants.",
    "Tomato___Tomato_mosaic_virus": "Remove and destroy infected plants. Disinfect tools with bleach. Use resistant varieties.",
    "Tomato___healthy": "Plant is healthy! Continue regular care.",
    "Wheat___Brown_Rust": "Apply Propiconazole fungicide. Use resistant varieties. Early sowing to avoid peak infection.",
    "Wheat___Yellow_Rust": "Apply Tebuconazole fungicide. Use certified resistant seeds. Monitor regularly.",
    "Wheat___healthy": "Plant is healthy! Continue regular care.",
}

def generate_synthetic_data(n_samples=5000):
    """Generate synthetic image feature data (R,G,B stats) for each disease class."""
    np.random.seed(42)
    X = []
    y = []

    # Each disease has somewhat unique colour/texture characteristics
    class_params = [
        # (r_mean, g_mean, b_mean, noise_scale)
        (120, 80, 60, 20), (80, 40, 30, 25), (150, 100, 50, 20), (80, 140, 60, 15),
        (100, 100, 50, 20), (120, 80, 40, 25), (90, 120, 50, 20), (80, 150, 60, 15),
        (100, 60, 50, 20), (110, 80, 70, 25), (110, 90, 60, 20), (90, 150, 70, 15),
        (130, 100, 50, 25), (100, 70, 50, 30), (80, 140, 60, 15),
        (110, 80, 50, 20), (100, 90, 60, 25), (80, 140, 60, 15),
        (110, 80, 60, 25), (120, 90, 50, 25), (100, 60, 50, 30),
        (90, 100, 70, 20), (110, 80, 50, 25), (130, 100, 80, 30),
        (110, 90, 60, 25), (140, 160, 50, 30), (100, 100, 80, 25), (80, 150, 60, 15),
        (130, 100, 50, 25), (120, 130, 50, 25), (80, 140, 60, 15),
    ]

    samples_per_class = n_samples // len(DISEASE_CLASSES)

    for class_idx, (rm, gm, bm, noise) in enumerate(class_params):
        for _ in range(samples_per_class):
            r_mean = np.clip(np.random.normal(rm, noise), 0, 255)
            g_mean = np.clip(np.random.normal(gm, noise), 0, 255)
            b_mean = np.clip(np.random.normal(bm, noise), 0, 255)
            r_std = np.random.uniform(10, 50)
            g_std = np.random.uniform(10, 50)
            b_std = np.random.uniform(10, 50)
            # Ratio features
            rg_ratio = r_mean / (g_mean + 1e-5)
            rb_ratio = r_mean / (b_mean + 1e-5)
            gb_ratio = g_mean / (b_mean + 1e-5)
            brightness = (r_mean + g_mean + b_mean) / 3
            greenness = g_mean - (r_mean + b_mean) / 2
            X.append([r_mean, g_mean, b_mean, r_std, g_std, b_std, rg_ratio, rb_ratio, gb_ratio, brightness, greenness])
            y.append(class_idx)

    return np.array(X), np.array(y)


if __name__ == "__main__":
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(n_samples=6200)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Training set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")
    print("Training Random Forest classifier...")
    clf = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Test Accuracy: {acc * 100:.1f}%")

    # Save model
    model_dir = os.path.dirname(__file__)
    joblib.dump(clf, os.path.join(model_dir, "disease_model.pkl"))
    print("✓ Saved disease_model.pkl")

    # Save labels
    labels = {str(i): name for i, name in enumerate(DISEASE_CLASSES)}
    with open(os.path.join(model_dir, "disease_class_labels.json"), "w") as f:
        json.dump(labels, f, indent=2)
    print("✓ Saved disease_class_labels.json")

    # Save treatment map
    with open(os.path.join(model_dir, "disease_treatment_map.json"), "w") as f:
        json.dump(TREATMENT_MAP, f, indent=2)
    print("✓ Saved disease_treatment_map.json")

    print(f"\nModel trained with {len(DISEASE_CLASSES)} disease classes.")
    print("All files saved successfully! Start the FastAPI server and test the /api/disease/predict endpoint.")
