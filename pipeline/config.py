"""Configuration models for Video Pipeline.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


def _normalize_series(values: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, str):
        raw_items = values.split(",")
    else:
        raw_items = values
    normalized = tuple(item.strip() for item in raw_items if item and item.strip())
    return normalized


@dataclass(frozen=True, slots=True)
class VideoJobConfig:
    input_video: Path
    video_id: str
    character: str
    series: tuple[str, ...] = field(default_factory=tuple)
    frame_interval: float = 0.5
    textures_dir: Path | None = None

    def __post_init__(self) -> None:
        if not self.video_id.strip():
            raise ValueError("video_id must not be empty.")
        if self.frame_interval <= 0:
            raise ValueError("frame_interval must be greater than zero.")

    @classmethod
    def create(
        cls,
        input_video: str | Path,
        video_id: str,
        character: str,
        series: str | Iterable[str],
        frame_interval: float = 0.5,
        textures_dir: str | Path | None = None,
    ) -> "VideoJobConfig":
        return cls(
            input_video=Path(input_video).expanduser().resolve(),
            video_id=video_id.strip(),
            character=character.strip(),
            series=_normalize_series(series),
            frame_interval=frame_interval,
            textures_dir=Path(textures_dir).expanduser().resolve() if textures_dir else None,
        )

    @property
    def series_csv(self) -> str:
        return ", ".join(self.series)


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    dry_run: bool = False
    skip_existing: bool = True
    npz_export: bool = False
    strict: bool = False
    capture_system_info: bool = True


@dataclass(frozen=True, slots=True)
class PathConfig:
    project_root: Path
    input_root: Path
    output_root: Path
    model_root: Path
    log_root: Path
    frames_dir: Path
    textures_dir: Path
    rgb_dir: Path
    mask_dir: Path
    depth_dir: Path
    segments_dir: Path
    processed_dir: Path
    normal_dir: Path
    pose_dir: Path
    pose_json_dir: Path
    captions_dir: Path
    tags_dir: Path
    data_dir: Path

    @classmethod
    def build(
        cls,
        project_root: str | Path,
        *,
        input_root: str | Path | None = None,
        output_root: str | Path | None = None,
        model_root: str | Path | None = None,
        log_root: str | Path | None = None,
    ) -> "PathConfig":
        project_root_path = Path(project_root).expanduser().resolve()
        input_root_path = (project_root_path / "input" if input_root is None else Path(input_root)).expanduser().resolve()
        output_root_path = (
            project_root_path / "output_layers" if output_root is None else Path(output_root)
        ).expanduser().resolve()
        model_root_path = (project_root_path / "models" if model_root is None else Path(model_root)).expanduser().resolve()
        log_root_path = (project_root_path / "logs" if log_root is None else Path(log_root)).expanduser().resolve()

        return cls(
            project_root=project_root_path,
            input_root=input_root_path,
            output_root=output_root_path,
            model_root=model_root_path,
            log_root=log_root_path,
            frames_dir=project_root_path / "frames",
            textures_dir=output_root_path / "textured",
            rgb_dir=output_root_path / "rgb",
            mask_dir=output_root_path / "mask",
            depth_dir=output_root_path / "depth",
            segments_dir=output_root_path / "segments",
            processed_dir=output_root_path / "processed",
            normal_dir=output_root_path / "normal_map",
            pose_dir=output_root_path / "pose",
            pose_json_dir=output_root_path / "pose_json",
            captions_dir=output_root_path / "captions",
            tags_dir=output_root_path / "tags",
            data_dir=output_root_path / "data",
        )

    def ensure_runtime_directories(self) -> None:
        for path in (
            self.input_root,
            self.output_root,
            self.log_root,
            self.frames_dir,
            self.textures_dir,
            self.rgb_dir,
            self.mask_dir,
            self.depth_dir,
            self.segments_dir,
            self.processed_dir,
            self.normal_dir,
            self.pose_dir,
            self.pose_json_dir,
            self.captions_dir,
            self.tags_dir,
            self.data_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def dataset_root(self, video_id: str) -> Path:
        return self.data_dir / f"{video_id}_data"


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    job: VideoJobConfig
    paths: PathConfig
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    def as_dict(self) -> dict[str, object]:
        def display_path(path: Path | None) -> str | None:
            if path is None:
                return None
            try:
                return str(path.resolve().relative_to(self.paths.project_root))
            except Exception:
                return str(path)

        return {
            "job": {
                "input_video": display_path(self.job.input_video),
                "video_id": self.job.video_id,
                "character": self.job.character,
                "series": list(self.job.series),
                "frame_interval": self.job.frame_interval,
                "textures_dir": display_path(self.job.textures_dir),
            },
            "paths": {
                "project_root": ".",
                "input_root": display_path(self.paths.input_root),
                "output_root": display_path(self.paths.output_root),
                "model_root": display_path(self.paths.model_root),
                "log_root": display_path(self.paths.log_root),
                "frames_dir": display_path(self.paths.frames_dir),
                "textures_dir": display_path(self.paths.textures_dir),
                "rgb_dir": display_path(self.paths.rgb_dir),
                "mask_dir": display_path(self.paths.mask_dir),
                "depth_dir": display_path(self.paths.depth_dir),
                "segments_dir": display_path(self.paths.segments_dir),
                "processed_dir": display_path(self.paths.processed_dir),
                "normal_dir": display_path(self.paths.normal_dir),
                "pose_dir": display_path(self.paths.pose_dir),
                "pose_json_dir": display_path(self.paths.pose_json_dir),
                "captions_dir": display_path(self.paths.captions_dir),
                "tags_dir": display_path(self.paths.tags_dir),
                "data_dir": display_path(self.paths.data_dir),
            },
            "runtime": {
                "dry_run": self.runtime.dry_run,
                "skip_existing": self.runtime.skip_existing,
                "npz_export": self.runtime.npz_export,
                "strict": self.runtime.strict,
                "capture_system_info": self.runtime.capture_system_info,
            },
        }


__all__ = ["PathConfig", "PipelineConfig", "RuntimeConfig", "VideoJobConfig"]
