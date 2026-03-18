from __future__ import annotations

import numpy as np
from PIL import Image


class DepthAnythingEstimator:
    """Lazy wrapper around the Hugging Face Depth Anything checkpoints."""

    MODEL_IDS = {
        "vitb": "LiheYoung/depth-anything-small-hf",
        "vitl": "LiheYoung/depth-anything-large-hf",
    }

    def __init__(self, model_type: str = "vitl", device: str = "cpu") -> None:
        self.model_type = model_type if model_type in self.MODEL_IDS else "vitl"
        self.device = device
        self._processor = None
        self._model = None

    def load(self) -> None:
        if self._model is not None and self._processor is not None:
            return

        from transformers import AutoImageProcessor, AutoModelForDepthEstimation

        model_id = self.MODEL_IDS[self.model_type]
        self._processor = AutoImageProcessor.from_pretrained(model_id)
        self._model = AutoModelForDepthEstimation.from_pretrained(model_id).to(self.device)

    def predict(self, image_pil: Image.Image) -> Image.Image:
        import torch

        self.load()
        assert self._processor is not None
        assert self._model is not None

        batch = self._processor(images=image_pil, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self._model(**batch)
            prediction = outputs.predicted_depth
            resized = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=image_pil.size[::-1],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        depth = resized.cpu().numpy()
        depth = depth - depth.min()
        max_value = depth.max()
        if max_value > 0:
            depth = depth / max_value
        depth_img = (depth * 255).astype(np.uint8)
        return Image.fromarray(depth_img)


__all__ = ["DepthAnythingEstimator"]
