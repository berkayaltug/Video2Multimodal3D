"""Video Pipeline orchestration entrypoint.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pipeline.config import PipelineConfig


@dataclass(slots=True)
class StepResult:
    name: str
    status: str
    detail: str
    duration_sec: float = 0.0
    outputs: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelRequirement:
    name: str
    expected_path: Path | None = None
    python_modules: tuple[str, ...] = ()
    note: str = ""


MODEL_REQUIREMENTS = {
    "pose": ModelRequirement(
        name="pose",
        expected_path=Path("Yolo") / "yolo11x-pose.pt",
        python_modules=("ultralytics",),
        note="Ultralytics YOLO pose weights are not bundled in the public repo.",
    ),
    "segmentation": ModelRequirement(
        name="segmentation",
        expected_path=Path("segment-anything") / "sam_vit_h_4b8939.pth",
        python_modules=("segment_anything",),
        note="Segment Anything weights must be placed under models/segment-anything/.",
    ),
    "depth": ModelRequirement(
        name="depth",
        expected_path=Path("depth_anything") / "checkpoints" / "depth_anything_v2_vitl.pth",
        python_modules=("transformers", "torch"),
        note="Depth Anything checkpoints are intentionally excluded from version control.",
    ),
    "normal_map": ModelRequirement(
        name="normal_map",
        expected_path=Path("StableNormal"),
        python_modules=("torch",),
        note="StableNormal can be loaded from the local repo clone or via torch.hub.",
    ),
    "captions": ModelRequirement(
        name="captions",
        python_modules=("transformers", "torch"),
        note="Captioning requires BLIP model downloads at runtime.",
    ),
    "tags": ModelRequirement(
        name="tags",
        python_modules=("huggingface_hub", "onnxruntime", "pandas"),
        note="Tagging relies on WaifuDiffusion-compatible tagger weights.",
    ),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _recursive_size_mb(root: Path) -> float:
    if not root.exists():
        return 0.0

    total_bytes = 0
    for path in root.rglob("*"):
        if path.is_file():
            total_bytes += path.stat().st_size
    return round(total_bytes / (1024 * 1024), 2)


def _safe_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def _collect_system_info() -> dict[str, object]:
    import platform

    info = {
        "timestamp_utc": _utc_now(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }

    try:
        import psutil

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(Path.cwd().anchor or str(Path.cwd()))
        info.update(
            {
                "cpu_count": psutil.cpu_count(logical=True),
                "ram_total_gb": round(memory.total / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }
        )
    except Exception:
        info["psutil"] = "unavailable"

    try:
        import torch

        info["torch_version"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            info["cuda_version"] = torch.version.cuda
            info["gpu_name"] = torch.cuda.get_device_name(0)
    except Exception:
        info["torch"] = "unavailable"

    return info


class PipelineRunner:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.results: list[StepResult] = []
        self.started_at = time.time()

    @property
    def frame_pattern(self) -> str:
        return f"{self.config.job.video_id}_*.jpg"

    def _display_path(self, path: Path | str) -> str:
        path_obj = Path(path)
        try:
            return str(path_obj.resolve().relative_to(self.config.paths.project_root))
        except Exception:
            return str(path_obj)

    def run(self) -> int:
        print(f"[pipeline] starting video_id={self.config.job.video_id} dry_run={self.config.runtime.dry_run}")
        self._prepare_workspace()
        try:
            self._execute_step("validate_input", self._validate_input)
            self._execute_step("extract_frames", self._extract_frames)
            self._execute_step(
                "pose_estimation",
                lambda: self._optional_integration_step(
                    "pose",
                    "Pose estimation integration is configured but not bundled in this lightweight public release.",
                    [self.config.paths.pose_dir, self.config.paths.pose_json_dir],
                ),
            )
            self._execute_step(
                "segmentation",
                lambda: self._optional_integration_step(
                    "segmentation",
                    "Segmentation is documented as an external integration point for the public repo.",
                    [self.config.paths.segments_dir, self.config.paths.processed_dir],
                ),
            )
            self._execute_step(
                "depth_estimation",
                lambda: self._optional_integration_step(
                    "depth",
                    "Depth estimation stays optional until weights are installed locally.",
                    [self.config.paths.depth_dir],
                ),
            )
            self._execute_step(
                "normal_estimation",
                lambda: self._optional_integration_step(
                    "normal_map",
                    "Surface normal estimation stays optional until StableNormal is configured.",
                    [self.config.paths.normal_dir],
                ),
            )
            self._execute_step(
                "caption_generation",
                lambda: self._optional_integration_step(
                    "captions",
                    "Caption generation remains optional and model-backed.",
                    [self.config.paths.captions_dir],
                ),
            )
            self._execute_step(
                "tag_generation",
                lambda: self._optional_integration_step(
                    "tags",
                    "Semantic tagging remains optional and model-backed.",
                    [self.config.paths.tags_dir],
                ),
            )
            self._execute_step("dataset_packaging", self._package_dataset)
            self._execute_step("write_summary", self._write_summary)
        except Exception as exc:
            print(f"[pipeline] failed: {exc}")
            self.results.append(
                StepResult(
                    name="pipeline",
                    status="failed",
                    detail=str(exc),
                )
            )
            self._write_summary()
            if self.config.runtime.strict:
                raise
            return 1
        print(f"[pipeline] completed video_id={self.config.job.video_id}")
        return 0

    def _prepare_workspace(self) -> None:
        self.config.paths.ensure_runtime_directories()
        snapshot_path = self.config.paths.log_root / f"{self.config.job.video_id}_config.json"
        snapshot_path.write_text(
            json.dumps(self.config.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _execute_step(self, name: str, handler) -> None:
        print(f"[step] {name} ...")
        start = time.time()
        result = handler()
        result.duration_sec = round(time.time() - start, 3)
        self.results.append(result)
        print(f"[step] {name}: {result.status} - {result.detail}")

    def _validate_input(self) -> StepResult:
        input_video = self.config.job.input_video
        if not input_video.exists() and not self.config.runtime.dry_run:
            raise FileNotFoundError(f"Input video was not found: {input_video}")

        detail_bits = [
            f"input={self._display_path(input_video)}",
            f"video_id={self.config.job.video_id}",
            f"frame_interval={self.config.job.frame_interval}",
            f"dry_run={self.config.runtime.dry_run}",
        ]
        if not input_video.exists() and self.config.runtime.dry_run:
            detail_bits.append("input_missing_but_allowed_for_dry_run=true")
        return StepResult(
            name="validate_input",
            status="completed",
            detail=" | ".join(detail_bits),
        )

    def _extract_frames(self) -> StepResult:
        existing_frames = sorted(self.config.paths.frames_dir.glob(self.frame_pattern))
        frame_template = self.config.paths.frames_dir / f"{self.config.job.video_id}_%04d.jpg"
        ffmpeg_binary = shutil.which("ffmpeg")
        command = [
            ffmpeg_binary or "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(self.config.job.input_video),
            "-vf",
            f"fps=1/{self.config.job.frame_interval}",
            str(frame_template),
        ]

        if self.config.runtime.dry_run:
            return StepResult(
                name="extract_frames",
                status="planned",
                detail="Dry-run: " + " ".join(command),
                outputs=[self._display_path(frame_template)],
            )

        if existing_frames and self.config.runtime.skip_existing:
            return StepResult(
                name="extract_frames",
                status="skipped",
                detail=f"Skipped because {len(existing_frames)} extracted frame(s) already exist.",
                outputs=[self._display_path(path) for path in existing_frames[:5]],
            )

        if ffmpeg_binary is None:
            raise RuntimeError("ffmpeg is required for frame extraction but was not found on PATH.")

        subprocess.run(command, check=True)
        extracted_frames = sorted(self.config.paths.frames_dir.glob(self.frame_pattern))
        return StepResult(
            name="extract_frames",
            status="completed",
            detail=f"Extracted {len(extracted_frames)} frame(s).",
            outputs=[self._display_path(path) for path in extracted_frames[:5]],
        )

    def _optional_integration_step(
        self,
        requirement_key: str,
        public_note: str,
        output_directories: Iterable[Path],
    ) -> StepResult:
        requirement = MODEL_REQUIREMENTS[requirement_key]
        for directory in output_directories:
            directory.mkdir(parents=True, exist_ok=True)

        missing_files: list[str] = []
        if requirement.expected_path is not None:
            expected_path = self.config.paths.model_root / requirement.expected_path
            if not expected_path.exists():
                missing_files.append(str(expected_path))

        missing_modules = [
            module_name
            for module_name in requirement.python_modules
            if not _safe_import(module_name)
        ]

        detail_parts = [public_note]
        if missing_files:
            detail_parts.append("missing_files=" + ", ".join(missing_files))
        if missing_modules:
            detail_parts.append("missing_modules=" + ", ".join(missing_modules))
        if requirement.note:
            detail_parts.append(requirement.note)

        status = "planned" if self.config.runtime.dry_run else "skipped"
        return StepResult(
            name=requirement_key,
            status=status,
            detail=" | ".join(detail_parts),
            outputs=[self._display_path(path) for path in output_directories],
        )

    def _package_dataset(self) -> StepResult:
        dataset_root = self.config.paths.dataset_root(self.config.job.video_id)
        dataset_root.mkdir(parents=True, exist_ok=True)
        manifest_path = dataset_root / "dataset_manifest.json"

        manifest = {
            "video_id": self.config.job.video_id,
            "input_video": self._display_path(self.config.job.input_video),
            "series": list(self.config.job.series),
            "character": self.config.job.character,
            "frame_glob": self._display_path(self.config.paths.frames_dir / self.frame_pattern),
            "dry_run": self.config.runtime.dry_run,
            "npz_export": self.config.runtime.npz_export,
            "generated_at_utc": _utc_now(),
            "steps": [result.as_dict() for result in self.results],
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        if not self.config.runtime.npz_export:
            return StepResult(
                name="dataset_packaging",
                status="completed",
                detail="Wrote dataset manifest only. NPZ export is disabled in the public release defaults.",
                outputs=[self._display_path(manifest_path)],
            )

        return StepResult(
            name="dataset_packaging",
            status="planned" if self.config.runtime.dry_run else "completed",
            detail="Dataset packaging contract is ready; enable project-specific NPZ exporters to materialize frame archives.",
            outputs=[self._display_path(manifest_path)],
        )

    def _write_summary(self) -> StepResult:
        finished_at = time.time()
        total_frames = len(list(self.config.paths.frames_dir.glob(self.frame_pattern)))
        total_size_mb = _recursive_size_mb(self.config.paths.output_root)
        summary = {
            "video_id": self.config.job.video_id,
            "status": "failed" if any(result.status == "failed" for result in self.results) else "ok",
            "dry_run": self.config.runtime.dry_run,
            "total_frames": total_frames,
            "output_size_mb": total_size_mb,
            "duration_sec": round(finished_at - self.started_at, 3),
            "started_at_utc": datetime.fromtimestamp(self.started_at, timezone.utc).isoformat(),
            "finished_at_utc": _utc_now(),
            "steps": [result.as_dict() for result in self.results],
        }
        if self.config.runtime.capture_system_info:
            summary["system"] = _collect_system_info()

        summary_json = self.config.paths.log_root / f"{self.config.job.video_id}_summary.json"
        summary_txt = self.config.paths.log_root / "summary_log.txt"
        summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        summary_line = (
            f"[{self.config.job.video_id}] "
            f"frames={total_frames} "
            f"duration_sec={summary['duration_sec']} "
            f"output_mb={total_size_mb} "
            f"dry_run={self.config.runtime.dry_run}"
        )
        existing = summary_txt.read_text(encoding="utf-8") if summary_txt.exists() else ""
        summary_txt.write_text((existing + summary_line + "\n"), encoding="utf-8")

        return StepResult(
            name="write_summary",
            status="completed",
            detail=summary_line,
            outputs=[self._display_path(summary_json), self._display_path(summary_txt)],
        )


def main(config: PipelineConfig) -> int:
    runner = PipelineRunner(config)
    return runner.run()


__all__ = ["MODEL_REQUIREMENTS", "PipelineRunner", "StepResult", "main"]
