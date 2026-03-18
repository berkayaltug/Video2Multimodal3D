import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
from models.depth_anything.depth_anything_v2.dpt import DepthAnythingV2
from models.depth_anything.depth_anything_v2.util.transform import Resize, NormalizeImage, PrepareForNet
from torchvision.transforms import Compose


class DepthAnything(DepthAnythingV2):
    def __init__(self, model_path: str, device: str = "cuda"):
        super().__init__()
        self.device = device

        # Modeli yükle
        self.model = DepthAnythingV2(
            enable_attention_hooks=False
        ).to(device)

        checkpoint = torch.load(model_path, map_location=device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        # Transform
        self.transform = Compose([
            Resize(
                width=518,
                height=518,
                resize_target=False,
                keep_aspect_ratio=True,
                ensure_multiple_of=14,
                resize_method="minimal",
                image_interpolation_method=cv2.INTER_CUBIC,
            ),
            NormalizeImage(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            PrepareForNet(),
        ])

    def forward(self, image):
        with torch.no_grad():
            image = self.transform({"image": image})["image"]
            image = torch.from_numpy(image).unsqueeze(0).to(self.device)

            depth = self.model(image)
            depth = F.interpolate(
                depth.unsqueeze(1),
                size=image.shape[2:],  # geri orijinal boyuta
                mode="bicubic",
                align_corners=False
            ).squeeze()

        return depth
