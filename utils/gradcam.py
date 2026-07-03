"""
Grad-CAM implementation for EfficientNet using PyTorch forward/backward hooks.
Returns a heatmap overlaid on the original image as a PIL Image.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np


class GradCAM:
    """
    Gradient-weighted Class Activation Mapping for CNN models.

    Usage:
        gradcam = GradCAM(model, target_layer=model.features[-1])
        heatmap_pil = gradcam.generate(input_tensor, original_image_rgb, class_idx=0)
    """

    def __init__(self, model, target_layer):
        """
        Args:
            model: PyTorch model (EfficientNet).
            target_layer: The convolutional layer to hook (typically the last conv layer).
        """
        self.model = model
        self.target_layer = target_layer
        self._gradients: Optional[any] = None
        self._activations: Optional[any] = None
        self._register_hooks()

    def _register_hooks(self) -> None:
        """Register forward and backward hooks on the target layer."""

        def save_activation(module, input, output):
            self._activations = output.detach()

        def save_gradient(module, grad_input, grad_output):
            self._gradients = grad_output[0].detach()

        self.target_layer.register_forward_hook(save_activation)
        self.target_layer.register_full_backward_hook(save_gradient)

    def generate(
        self,
        input_tensor,
        original_image_rgb: np.ndarray,
        class_idx: Optional[int] = None,
    ):
        """
        Generate Grad-CAM heatmap overlaid on the original image.

        Args:
            input_tensor: Preprocessed tensor (1, C, H, W).
            original_image_rgb: Original RGB image as numpy array (H, W, 3) uint8.
            class_idx: Target class index. If None, uses the predicted class.

        Returns:
            PIL.Image.Image with Grad-CAM heatmap overlaid on original image.
        """
        try:
            import torch  # type: ignore
            import torch.nn.functional as F  # type: ignore
        except ImportError as exc:
            raise ImportError("torch is required for Grad-CAM") from exc

        self.model.eval()
        input_tensor = input_tensor.requires_grad_(True)

        # Forward pass
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        # Zero gradients and backward
        self.model.zero_grad()
        score = output[0, class_idx]
        score.backward()

        # Pool gradients across spatial dimensions
        gradients = self._gradients  # (1, C, H, W)
        activations = self._activations  # (1, C, H, W)

        weights = gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)
        cam = (weights * activations).sum(dim=1, keepdim=True)  # (1, 1, H, W)
        cam = F.relu(cam)

        # Resize CAM to input image size
        h, w = original_image_rgb.shape[:2]
        cam_resized = F.interpolate(cam, size=(h, w), mode="bilinear", align_corners=False)
        cam_np = cam_resized.squeeze().cpu().numpy()

        # Normalize to [0, 1]
        cam_min, cam_max = cam_np.min(), cam_np.max()
        if cam_max - cam_min > 1e-8:
            cam_np = (cam_np - cam_min) / (cam_max - cam_min)
        else:
            cam_np = np.zeros_like(cam_np)

        return _overlay_heatmap(cam_np, original_image_rgb)


def _overlay_heatmap(
    cam: np.ndarray,
    original_rgb: np.ndarray,
    alpha: float = 0.4,
    colormap_name: str = "jet",
) -> "PIL.Image.Image":  # noqa: F821
    """
    Overlay a Grad-CAM heatmap on the original image.

    Args:
        cam: Normalized heatmap array (H, W) in [0, 1].
        original_rgb: Original image (H, W, 3) uint8.
        alpha: Blend weight for heatmap overlay (0=original, 1=heatmap only).
        colormap_name: Matplotlib colormap name.

    Returns:
        PIL.Image.Image with heatmap blended onto the original.
    """
    try:
        import cv2  # type: ignore
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise ImportError("opencv-python-headless and Pillow are required for heatmap overlay") from exc

    # Convert CAM to uint8 heatmap using OpenCV colormap
    cam_uint8 = (cam * 255).astype(np.uint8)
    heatmap_bgr = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)

    # Resize heatmap to match original if needed
    h, w = original_rgb.shape[:2]
    if heatmap_rgb.shape[:2] != (h, w):
        heatmap_rgb = cv2.resize(heatmap_rgb, (w, h), interpolation=cv2.INTER_LINEAR)

    # Blend heatmap with original image
    original_float = original_rgb.astype(np.float32)
    heatmap_float = heatmap_rgb.astype(np.float32)
    blended = (1 - alpha) * original_float + alpha * heatmap_float
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    return Image.fromarray(blended)


def get_efficientnet_target_layer(model):
    """
    Return the last convolutional block of an EfficientNet model for Grad-CAM.

    Works with torchvision EfficientNet-B0 architecture.

    Args:
        model: EfficientNet model from torchvision.

    Returns:
        The target layer (last features block).
    """
    # torchvision EfficientNet: model.features is a Sequential of blocks
    # The last block before the classifier is model.features[-1]
    return model.features[-1]


def generate_gradcam_overlay(
    image_bytes: bytes,
    model,
    class_idx: Optional[int] = None,
) -> Optional["PIL.Image.Image"]:  # noqa: F821
    """
    High-level function to generate Grad-CAM from raw image bytes.

    Args:
        image_bytes: Raw image bytes.
        model: Loaded EfficientNet PyTorch model.
        class_idx: Target class (0=FAKE, 1=REAL). If None, uses predicted class.

    Returns:
        PIL Image with Grad-CAM overlay, or None if generation fails.
    """
    try:
        from utils.image_preprocess import preprocess_image_bytes  # type: ignore

        input_tensor, original_rgb = preprocess_image_bytes(image_bytes)
        target_layer = get_efficientnet_target_layer(model)

        gradcam = GradCAM(model, target_layer)
        overlay = gradcam.generate(input_tensor, original_rgb, class_idx=class_idx)
        return overlay

    except Exception as exc:
        print(f"[GradCAM] Failed to generate heatmap: {exc}")
        return None
