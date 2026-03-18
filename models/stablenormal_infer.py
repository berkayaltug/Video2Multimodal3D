from __future__ import annotations

from pathlib import Path


class StableNormalEstimator:
    """Lazy adapter for StableNormal."""

    def __init__(
        self,
        repo_or_dir: str | Path = Path(__file__).resolve().parent / "StableNormal",
        hub_model: str = "StableNormal_turbo",
        device: str | None = None,
        yoso_version: str = "yoso-normal-v1-8-1",
    ) -> None:
        self.repo_or_dir = Path(repo_or_dir)
        self.hub_model = hub_model
        self.device = device
        self.yoso_version = yoso_version
        self._model = None

    def load(self):
        if self._model is not None:
            return self._model

        import torch

        source = "local" if self.repo_or_dir.exists() else "github"
        load_target = str(self.repo_or_dir) if source == "local" else "hugoycj/StableNormal"
        self._model = torch.hub.load(
            load_target,
            self.hub_model,
            source=source,
            trust_repo=True,
            yoso_version=self.yoso_version,
        )
        if self.device and hasattr(self._model, "to"):
            self._model = self._model.to(self.device)
        return self._model

    def predict_normals(self, rgba_image):
        model = self.load()
        return model(rgba_image, data_type="object")

    def predict_and_save(self, rgba_image, output_dir: str | Path, base_name: str):
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        output_path = output_dir_path / f"{base_name}_normal.png"
        normal_map = self.predict_normals(rgba_image)
        normal_map.save(output_path)
        return output_path


__all__ = ["StableNormalEstimator"]
