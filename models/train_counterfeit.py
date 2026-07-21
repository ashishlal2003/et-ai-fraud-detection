"""
Fine-tune EfficientNet-B0 for binary classification: real vs fake Indian currency notes.

Note: If data/currency_dataset/ is empty or missing, see instructions below for
sourcing data from Kaggle.

Expected directory layout:
    data/currency_dataset/
        real/    <- images of genuine Indian currency notes
        fake/    <- images of counterfeit Indian currency notes

Kaggle datasets to search:
    - "Indian Currency Note Detection" by various uploaders
    - "Fake Currency Detection India" dataset
    - Search: https://www.kaggle.com/datasets?search=indian+currency+fake

Download instructions:
    1. Install kaggle CLI: pip install kaggle
    2. Set up ~/.kaggle/kaggle.json with your API key
    3. kaggle datasets download -d <username>/<dataset-name>
    4. Unzip and organise into data/currency_dataset/real/ and data/currency_dataset/fake/

Usage:
    python models/train_counterfeit.py
"""

import os
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent          # fraud-shield/
DATA_DIR = ROOT / "data" / "currency_dataset"
SAVE_PATH = ROOT / "models" / "efficientnet_currency.pth"

REAL_DIR = DATA_DIR / "real"
FAKE_DIR = DATA_DIR / "fake"

# ---------------------------------------------------------------------------
# Hyper-parameters
# ---------------------------------------------------------------------------
IMG_SIZE = 224
BATCH_SIZE = 32
NUM_EPOCHS = 10
LR = 1e-4
VAL_SPLIT = 0.2
SEED = 42

CLASS_NAMES = ["fake", "real"]   # alphabetical order used by ImageFolder


# ---------------------------------------------------------------------------
# Data transforms
# ---------------------------------------------------------------------------

def get_transforms():
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    return train_tf, val_tf


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def build_model(num_classes: int = 2) -> nn.Module:
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    # Replace classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes),
    )
    return model


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return total_loss / total, correct / total, all_preds, all_labels


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Check data availability
    if not DATA_DIR.exists() or not REAL_DIR.exists() or not FAKE_DIR.exists():
        print("=" * 60)
        print("DATA DIRECTORY NOT FOUND")
        print("=" * 60)
        print(f"Expected: {DATA_DIR}")
        print("\nTo source data from Kaggle:")
        print("  1. pip install kaggle")
        print("  2. Place your kaggle.json at ~/.kaggle/kaggle.json")
        print("  3. Search for Indian currency datasets:")
        print("     https://www.kaggle.com/datasets?search=indian+currency+fake")
        print("  4. Download and unzip, then organise into:")
        print(f"     {REAL_DIR}/  <- genuine note images")
        print(f"     {FAKE_DIR}/  <- counterfeit note images")
        print("\nRecommended datasets:")
        print("  kaggle datasets download -d \"your-chosen/dataset\"")
        sys.exit(0)

    real_count = len(list(REAL_DIR.glob("*.*")))
    fake_count = len(list(FAKE_DIR.glob("*.*")))
    if real_count == 0 or fake_count == 0:
        print(f"WARNING: real images={real_count}, fake images={fake_count}")
        print("Directories exist but are empty. Please add images and re-run.")
        print(f"  {REAL_DIR}  <- genuine note images")
        print(f"  {FAKE_DIR}  <- counterfeit note images")
        sys.exit(0)

    print(f"Dataset: {real_count} real | {fake_count} fake images")

    train_tf, val_tf = get_transforms()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Full dataset with train transforms first; val subset will use val_tf
    full_dataset = datasets.ImageFolder(str(DATA_DIR), transform=train_tf)
    print(f"Classes detected by ImageFolder: {full_dataset.classes}")

    n_val = int(len(full_dataset) * VAL_SPLIT)
    n_train = len(full_dataset) - n_val
    generator = torch.Generator().manual_seed(SEED)
    train_subset, val_subset = random_split(full_dataset, [n_train, n_val], generator=generator)

    # Override val transforms
    val_dataset = datasets.ImageFolder(str(DATA_DIR), transform=val_tf)
    val_subset.dataset = val_dataset   # share indices, different transforms

    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4, pin_memory=True)

    model = build_model(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

    best_val_acc = 0.0
    history = []

    print(f"\n{'Epoch':>5} {'Train Loss':>11} {'Train Acc':>10} {'Val Loss':>10} {'Val Acc':>9} {'LR':>10}")
    print("-" * 60)

    for epoch in range(1, NUM_EPOCHS + 1):
        tr_loss, tr_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        vl_loss, vl_acc, val_preds, val_labels = eval_epoch(model, val_loader, criterion, device)
        scheduler.step(vl_acc)

        history.append({"epoch": epoch, "tr_loss": tr_loss, "tr_acc": tr_acc, "vl_loss": vl_loss, "vl_acc": vl_acc})
        current_lr = optimizer.param_groups[0]["lr"]
        print(f"{epoch:>5} {tr_loss:>11.4f} {tr_acc:>9.4f} {vl_loss:>10.4f} {vl_acc:>9.4f} {current_lr:>10.2e}")

        if vl_acc > best_val_acc:
            best_val_acc = vl_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": vl_acc,
                "class_names": full_dataset.classes,
            }, str(SAVE_PATH))
            print(f"  --> Best model saved (val_acc={vl_acc:.4f})")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.4f}")

    # Load best model for final evaluation
    checkpoint = torch.load(str(SAVE_PATH), map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    _, final_acc, final_preds, final_labels = eval_epoch(model, val_loader, criterion, device)

    print(f"\n=== Final Accuracy on Validation Set: {final_acc:.4f} ===")
    print("\nClassification Report:")
    print(classification_report(final_labels, final_preds, target_names=full_dataset.classes))

    print("Confusion Matrix:")
    cm = confusion_matrix(final_labels, final_preds)
    print(f"  {'':8}", "  ".join(full_dataset.classes))
    for i, row_name in enumerate(full_dataset.classes):
        print(f"  {row_name:8}", "  ".join(f"{v:6}" for v in cm[i]))

    print(f"\nBest model saved to: {SAVE_PATH}")


if __name__ == "__main__":
    main()
