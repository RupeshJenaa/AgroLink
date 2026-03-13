"""
Plant Disease Prediction - CNN Training Script
===============================================
Architecture : MobileNetV2  (transfer learning from ImageNet)
Dataset      : PlantVillage  (folder-based structure)
Output files : disease_model_cnn.pth
               disease_class_labels.json
               disease_treatment_map.json

Usage:
    python models/train_plantvillage_cnn.py

The script auto-detects CUDA / MPS / CPU and trains for a fixed number of
epochs, saving the best checkpoint (by validation accuracy).
"""

import os
import json
import copy
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms
from torchvision.models import MobileNet_V2_Weights

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

# Absolute path to the PlantVillage root that contains sub-folders per class.
# Adjust if yours is nested differently.
DATASET_ROOTS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "PlantVillage"),
    os.path.join(os.path.dirname(__file__), "..", "..", "PlantVillage", "PlantVillage"),
]

OUTPUT_DIR = os.path.dirname(__file__)          # saves next to the training script

MODEL_FILENAME   = "disease_model_cnn.pth"
LABELS_FILENAME  = "disease_class_labels.json"
TREATMENT_FILENAME = "disease_treatment_map.json"

IMG_SIZE   = 224        # MobileNetV2 expects at least 224×224
BATCH_SIZE = 32
NUM_EPOCHS = 15         # increase for better accuracy
LR         = 0.001
VAL_SPLIT  = 0.2
NUM_WORKERS = 0         # set to 0 for Windows compatibility (avoids pickle errors)

# ─────────────────────────────────────────────────────────────────────────────
# TREATMENT MAP  (expand as needed)
# ─────────────────────────────────────────────────────────────────────────────

TREATMENT_MAP = {
    # Pepper
    "Pepper__bell___Bacterial_spot": (
        "Apply copper-based bactericides (e.g., Kocide 3000). "
        "Avoid overhead irrigation. Use certified disease-free seeds. "
        "Remove and destroy infected plant material."
    ),
    "Pepper__bell___healthy": "Plant is healthy! Continue regular watering, fertilization, and monitoring.",

    # Potato
    "Potato___Early_blight": (
        "Apply Chlorothalonil or Mancozeb fungicide. "
        "Ensure adequate potassium nutrition. Remove infected leaves promptly. "
        "Practice crop rotation with non-Solanaceous crops."
    ),
    "Potato___Late_blight": (
        "Apply Metalaxyl or Cymoxanil-based fungicide immediately — late blight spreads rapidly. "
        "Avoid overhead watering. Remove and destroy infected plants. "
        "Use certified disease-free seed potatoes."
    ),
    "Potato___healthy": "Plant is healthy! Continue regular hilling, watering, and monitoring.",

    # Tomato
    "Tomato_Bacterial_spot": (
        "Apply copper-based bactericides. Avoid working with wet plants. "
        "Use certified disease-free seeds. Remove infected plant debris."
    ),
    "Tomato_Early_blight": (
        "Apply Mancozeb or Chlorothalonil fungicide. "
        "Remove lower infected leaves. Mulch around plants to reduce soil splash. "
        "Ensure good air circulation."
    ),
    "Tomato_Late_blight": (
        "Apply Metalaxyl + Mancozeb immediately. Destroy infected plants — do NOT compost. "
        "Avoid overhead irrigation. Use resistant varieties where available."
    ),
    "Tomato_Leaf_Mold": (
        "Improve greenhouse ventilation. Apply Chlorothalonil or Azoxystrobin. "
        "Avoid wetting foliage during irrigation. Remove heavily infected leaves."
    ),
    "Tomato_Septoria_leaf_spot": (
        "Apply copper-based or Mancozeb fungicides. Remove infected leaves. "
        "Practice crop rotation. Avoid overhead irrigation."
    ),
    "Tomato_Spider_mites_Two_spotted_spider_mite": (
        "Apply Abamectin or insecticidal soap/neem oil. Increase humidity around plants. "
        "Introduce predatory mites (Phytoseiulus persimilis). "
        "Avoid broad-spectrum insecticides that kill natural enemies."
    ),
    "Tomato__Target_Spot": (
        "Apply Chlorothalonil or Azoxystrobin fungicide. "
        "Remove infected lower leaves. Maintain good plant nutrition. "
        "Ensure adequate plant spacing for air circulation."
    ),
    "Tomato__Tomato_YellowLeaf__Curl_Virus": (
        "Control whitefly vectors with imidacloprid or reflective mulch. "
        "Remove and destroy infected plants immediately. "
        "Use virus-resistant tomato varieties. Install insect-proof screens in greenhouses."
    ),
    "Tomato__Tomato_mosaic_virus": (
        "Remove and destroy infected plants — do NOT compost. "
        "Disinfect tools with 10% bleach solution between plants. "
        "Wash hands after handling tobacco products. Use TMV-resistant varieties."
    ),
    "Tomato_healthy": "Plant is healthy! Continue regular care, watering, and monitoring.",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def find_dataset_root():
    """Return the first valid ImageFolder-style dataset root directory."""
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    for path in DATASET_ROOTS:
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            continue
        # Only accept directories whose immediate subdirs contain image files
        subdirs = [d for d in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, d))]
        if not subdirs:
            continue
        # Check that at least one subdir has image files
        for sd in subdirs[:5]:   # sample first 5 subdirs
            sd_path = os.path.join(abs_path, sd)
            files = os.listdir(sd_path)
            if any(os.path.splitext(f)[1].lower() in IMAGE_EXTS for f in files):
                return abs_path
    raise FileNotFoundError(
        "Could not locate PlantVillage dataset. "
        f"Searched: {[os.path.abspath(p) for p in DATASET_ROOTS]}"
    )


def build_transforms():
    """Return (train_transform, val_transform)."""
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std  = [0.229, 0.224, 0.225]

    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
        transforms.RandomCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    return train_tf, val_tf


def build_model(num_classes: int) -> nn.Module:
    """Build a MobileNetV2 model fine-tuned for `num_classes` outputs."""
    model = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)

    # Freeze all backbone layers initially
    for param in model.parameters():
        param.requires_grad = False

    # Replace the classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes),
    )

    # Unfreeze the last 5 conv blocks for fine-tuning
    for name, param in model.features.named_parameters():
        block_idx = int(name.split(".")[0]) if name.split(".")[0].isdigit() else -1
        if block_idx >= 14:
            param.requires_grad = True

    return model


def train_model(model, dataloaders, dataset_sizes, criterion, optimizer, scheduler, device, num_epochs):
    """Full training loop. Returns (best_model, history)."""
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc       = 0.0
    history        = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

    for epoch in range(num_epochs):
        t0 = time.time()
        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        print("-" * 40)

        for phase in ("train", "val"):
            model.train() if phase == "train" else model.eval()

            running_loss, running_corrects = 0.0, 0

            for inputs, labels in dataloaders[phase]:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    loss    = criterion(outputs, labels)
                    preds   = outputs.argmax(dim=1)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss     += loss.item() * inputs.size(0)
                running_corrects += (preds == labels).sum().item()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc  = running_corrects / dataset_sizes[phase]

            print(f"  {phase.capitalize():5s} — Loss: {epoch_loss:.4f}  Acc: {epoch_acc * 100:.2f}%")
            history[f"{phase}_loss"].append(epoch_loss)
            history[f"{phase}_acc"].append(epoch_acc)

            if phase == "val":
                scheduler.step(epoch_loss)
                if epoch_acc > best_acc:
                    best_acc = epoch_acc
                    best_model_wts = copy.deepcopy(model.state_dict())
                    print(f"  ✓ New best val accuracy: {best_acc * 100:.2f}%")

        print(f"  Epoch time: {time.time() - t0:.1f}s")

    model.load_state_dict(best_model_wts)
    print(f"\nTraining complete. Best val accuracy: {best_acc * 100:.2f}%")
    return model, history


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Device ───────────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    # ── Dataset ──────────────────────────────────────────────────────────────
    dataset_root = find_dataset_root()
    print(f"Dataset root  : {dataset_root}")

    train_tf, val_tf = build_transforms()

    full_dataset = datasets.ImageFolder(root=dataset_root, transform=train_tf)
    class_names  = full_dataset.classes
    num_classes  = len(class_names)
    print(f"Classes found : {num_classes}")
    for i, c in enumerate(class_names):
        print(f"  [{i:2d}] {c}")

    # Save class label mapping
    labels_path = os.path.join(OUTPUT_DIR, LABELS_FILENAME)
    labels_dict = {str(i): name for i, name in enumerate(class_names)}
    with open(labels_path, "w") as f:
        json.dump(labels_dict, f, indent=2)
    print(f"\n✓ Saved {LABELS_FILENAME}")

    # Save treatment map (only for classes in the dataset)
    effective_treatment = {}
    for cls in class_names:
        effective_treatment[cls] = TREATMENT_MAP.get(
            cls, "Consult a local agricultural extension officer for diagnosis and treatment."
        )
    treatment_path = os.path.join(OUTPUT_DIR, TREATMENT_FILENAME)
    with open(treatment_path, "w") as f:
        json.dump(effective_treatment, f, indent=2)
    print(f"✓ Saved {TREATMENT_FILENAME}")

    # Train / val split
    n_val   = int(len(full_dataset) * VAL_SPLIT)
    n_train = len(full_dataset) - n_val
    train_ds, val_ds = random_split(
        full_dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(42)
    )
    # Apply different transform to validation split
    val_ds.dataset = copy.deepcopy(full_dataset)
    val_ds.dataset.transform = val_tf

    dataloaders = {
        "train": DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=NUM_WORKERS, pin_memory=(device.type == "cuda")),
        "val":   DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=(device.type == "cuda")),
    }
    dataset_sizes = {"train": n_train, "val": n_val}
    print(f"\nTrain samples : {n_train}")
    print(f"Val   samples : {n_val}")

    # ── Model ────────────────────────────────────────────────────────────────
    model = build_model(num_classes).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=3, factor=0.5)

    # ── Train ────────────────────────────────────────────────────────────────
    print("\nStarting training…")
    model, history = train_model(
        model, dataloaders, dataset_sizes,
        criterion, optimizer, scheduler,
        device, NUM_EPOCHS
    )

    # ── Save model ───────────────────────────────────────────────────────────
    model_path = os.path.join(OUTPUT_DIR, MODEL_FILENAME)
    torch.save({
        "model_state_dict": model.state_dict(),
        "class_names":      class_names,
        "num_classes":      num_classes,
        "img_size":         IMG_SIZE,
        "architecture":     "mobilenet_v2",
    }, model_path)
    print(f"✓ Saved {MODEL_FILENAME}")

    print("\n=== Training Complete ===")
    print(f"Model    : {model_path}")
    print(f"Labels   : {labels_path}")
    print(f"Treatments: {treatment_path}")
    print("\nRestart the FastAPI server and test the /api/disease/predict endpoint.")


if __name__ == "__main__":
    main()
