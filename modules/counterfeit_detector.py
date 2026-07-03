"""
Counterfeit Currency Detector — CV module.
Uses EfficientNet-B0 fine-tuned on Indian currency note images.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

MODEL_PATH = Path(__file__).parent.parent / "models" / "efficientnet_currency.pth"

# Class mapping: index → label
CLASS_LABELS = {0: "FAKE", 1: "REAL"}
NUM_CLASSES = 2


def load_model() -> Optional[object]:
    """
    Load fine-tuned EfficientNet-B0 from models/efficientnet_currency.pth.

    Returns:
        PyTorch model in eval mode, or None if file not found.
    """
    if not MODEL_PATH.exists():
        print(f"[CounterfeitDetector] Model not found at {MODEL_PATH}. Running in demo mode.")
        return None

    try:
        import torch  # type: ignore
        import torchvision.models as models  # type: ignore

        model = models.efficientnet_b0(weights=None)
        # Replace classifier head for binary classification
        in_features = model.classifier[1].in_features
        import torch.nn as nn  # type: ignore
        model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)

        state_dict = torch.load(str(MODEL_PATH), map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()

        print(f"[CounterfeitDetector] Model loaded from {MODEL_PATH}")
        return model

    except Exception as exc:
        print(f"[CounterfeitDetector] Failed to load model: {exc}")
        return None


def predict(image_bytes: bytes, model=None) -> dict:
    """
    Predict whether a currency note image is REAL or FAKE.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG of currency note).
        model: Loaded EfficientNet model (or None for demo mode).

    Returns:
        dict with keys:
            - verdict (str): "REAL" or "FAKE"
            - confidence (float): Confidence score [0, 1]
            - scores (dict): {"REAL": float, "FAKE": float}
            - demo_mode (bool): True if model not loaded
    """
    if model is None:
        return _demo_predict(image_bytes)

    try:
        import torch  # type: ignore
        import torch.nn.functional as F  # type: ignore
        from utils.image_preprocess import preprocess_image_bytes  # type: ignore

        input_tensor, _ = preprocess_image_bytes(image_bytes)

        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=-1).squeeze()

        fake_prob = probs[0].item()
        real_prob = probs[1].item()
        pred_idx = probs.argmax().item()
        verdict = CLASS_LABELS[pred_idx]
        confidence = probs[pred_idx].item()

        return {
            "verdict": verdict,
            "confidence": confidence,
            "scores": {"FAKE": fake_prob, "REAL": real_prob},
            "demo_mode": False,
        }

    except Exception as exc:
        print(f"[CounterfeitDetector] Inference error: {exc}")
        return _demo_predict(image_bytes)


def _demo_predict(image_bytes: bytes) -> dict:
    """
    Demo prediction when no model is loaded.
    Returns a placeholder result for UI demonstration.
    """
    import random

    # Deterministic seed from image size for reproducible demo results
    seed = len(image_bytes) % 100
    random.seed(seed)

    fake_prob = random.uniform(0.1, 0.9)
    real_prob = 1.0 - fake_prob
    verdict = "REAL" if real_prob > fake_prob else "FAKE"
    confidence = max(fake_prob, real_prob)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "scores": {"FAKE": fake_prob, "REAL": real_prob},
        "demo_mode": True,
    }


def get_gradcam(image_bytes: bytes, model) -> Optional["PIL.Image.Image"]:  # noqa: F821
    """
    Generate a Grad-CAM visualization highlighting suspicious regions.

    Args:
        image_bytes: Raw image bytes of the currency note.
        model: Loaded EfficientNet model.

    Returns:
        PIL Image with Grad-CAM heatmap overlay, or None if generation fails.
    """
    if model is None:
        return _demo_gradcam(image_bytes)

    try:
        from utils.gradcam import generate_gradcam_overlay  # type: ignore

        overlay = generate_gradcam_overlay(image_bytes, model, class_idx=0)  # 0 = FAKE class
        return overlay

    except Exception as exc:
        print(f"[CounterfeitDetector] Grad-CAM error: {exc}")
        return _demo_gradcam(image_bytes)


def _demo_gradcam(image_bytes: bytes) -> Optional["PIL.Image.Image"]:  # noqa: F821
    """
    Generate a simple demo heatmap when model is not available.
    Overlays a semi-transparent red gradient on the image.
    """
    try:
        import numpy as np
        from PIL import Image  # type: ignore
        import io

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((400, 300))
        img_array = np.array(img, dtype=np.float32)

        # Create a simple gradient heatmap (demo only)
        h, w = img_array.shape[:2]
        gradient = np.zeros((h, w), dtype=np.float32)
        # Highlight center region as "suspicious" for demo
        gradient[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = 0.6
        gradient = gradient + np.random.uniform(0, 0.2, gradient.shape).astype(np.float32)
        gradient = np.clip(gradient, 0, 1)

        # Red overlay
        overlay = img_array.copy()
        overlay[:, :, 0] = np.clip(img_array[:, :, 0] * 0.6 + gradient * 150, 0, 255)
        overlay[:, :, 1] = np.clip(img_array[:, :, 1] * 0.6, 0, 255)
        overlay[:, :, 2] = np.clip(img_array[:, :, 2] * 0.6, 0, 255)

        return Image.fromarray(overlay.astype(np.uint8))

    except Exception as exc:
        print(f"[CounterfeitDetector] Demo Grad-CAM error: {exc}")
        return None


def get_analysis_details(image_bytes: bytes) -> dict:
    """
    Extract basic image statistics for display alongside the verdict.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        dict with image metadata (size, color channels, brightness, etc.)
    """
    try:
        import io
        import numpy as np
        from PIL import Image  # type: ignore

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(img)

        return {
            "width": img.width,
            "height": img.height,
            "mean_brightness": float(img_array.mean()),
            "color_variance": float(img_array.var()),
            "file_size_kb": len(image_bytes) / 1024,
        }

    except Exception:
        return {}
