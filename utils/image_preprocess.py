"""
OpenCV-based image preprocessing for EfficientNet currency detection.
Converts image bytes to a normalized tensor ready for inference.
"""

from __future__ import annotations

import io
from typing import Optional, Tuple

import numpy as np

# ImageNet normalization constants
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

TARGET_SIZE: Tuple[int, int] = (224, 224)  # EfficientNet-B0 default input


def bytes_to_numpy(image_bytes: bytes) -> np.ndarray:
    """
    Decode image bytes to a NumPy array (H, W, C) in RGB order.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, etc.)

    Returns:
        NumPy array with shape (H, W, 3) in RGB uint8 format.

    Raises:
        ValueError: If the image cannot be decoded.
    """
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise ImportError("opencv-python-headless is required for image preprocessing") from exc

    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise ValueError("Failed to decode image bytes. Ensure the input is a valid image.")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return img_rgb


def resize_image(image: np.ndarray, size: Tuple[int, int] = TARGET_SIZE) -> np.ndarray:
    """
    Resize image to target dimensions using high-quality interpolation.

    Args:
        image: NumPy array (H, W, 3) in uint8 format.
        size: Target (width, height) tuple.

    Returns:
        Resized NumPy array (size[1], size[0], 3).
    """
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise ImportError("opencv-python-headless is required") from exc

    return cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to float32 with ImageNet mean/std.

    Args:
        image: NumPy array (H, W, 3) in uint8 format.

    Returns:
        Normalized float32 array (H, W, 3).
    """
    img_float = image.astype(np.float32) / 255.0
    img_normalized = (img_float - IMAGENET_MEAN) / IMAGENET_STD
    return img_normalized


def to_tensor(image: np.ndarray):
    """
    Convert (H, W, C) NumPy array to (1, C, H, W) PyTorch tensor.

    Args:
        image: Normalized float32 NumPy array (H, W, 3).

    Returns:
        PyTorch tensor with shape (1, 3, H, W).
    """
    try:
        import torch  # type: ignore
    except ImportError as exc:
        raise ImportError("torch is required for tensor conversion") from exc

    # HWC -> CHW
    img_chw = np.transpose(image, (2, 0, 1))
    tensor = torch.from_numpy(img_chw).unsqueeze(0)  # add batch dim
    return tensor


def preprocess_image_bytes(image_bytes: bytes):
    """
    Full preprocessing pipeline: bytes → resized → normalized → tensor.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Tuple of (tensor (1, 3, 224, 224), original_rgb_array (H, W, 3))
        The original array is returned for Grad-CAM overlay.
    """
    original_rgb = bytes_to_numpy(image_bytes)
    resized = resize_image(original_rgb, TARGET_SIZE)
    normalized = normalize_image(resized)
    tensor = to_tensor(normalized)
    return tensor, original_rgb


def bytes_to_pil(image_bytes: bytes):
    """
    Convert image bytes to PIL Image (RGB).

    Args:
        image_bytes: Raw image bytes.

    Returns:
        PIL.Image.Image in RGB mode.
    """
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise ImportError("Pillow is required for PIL conversion") from exc

    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
