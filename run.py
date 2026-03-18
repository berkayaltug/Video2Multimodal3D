"""Public single-video CLI for Video Pipeline.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.config import PathConfig, PipelineConfig, RuntimeConfig, VideoJobConfig
from pipeline.prep_pipeline import main as run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Video Pipeline on a single video.")
    parser.add_argument("--input", required=True, help="Path to the input video file.")
    parser.add_argument("--video-id", required=True, help="Stable identifier used in output naming.")
    parser.add_argument("--character", required=True, help="Primary character or object label.")
    parser.add_argument("--series", required=True, help="Comma separated source series or universe labels.")
    parser.add_argument("--frame-interval", type=float, default=0.5, help="Frame sampling interval in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration and emit a plan without running heavy inference.")
    parser.add_argument("--strict", action="store_true", help="Raise errors instead of downgrading optional integrations to skipped.")
    parser.add_argument("--npz-export", action="store_true", help="Enable dataset packaging contract for NPZ export.")
    parser.add_argument("--textures-dir", help="Optional directory containing texture renders for the current video.")
    parser.add_argument("--project-root", default=Path(__file__).resolve().parent, help="Project root for resolving default paths.")
    parser.add_argument("--input-root", help="Override the input root directory.")
    parser.add_argument("--output-root", help="Override the output root directory.")
    parser.add_argument("--models-root", help="Override the models root directory.")
    parser.add_argument("--logs-root", help="Override the logs root directory.")
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-run steps even if extracted frames already exist.",
    )
    return parser


def build_config(args: argparse.Namespace) -> PipelineConfig:
    project_root = Path(args.project_root).expanduser().resolve()
    paths = PathConfig.build(
        project_root,
        input_root=args.input_root,
        output_root=args.output_root,
        model_root=args.models_root,
        log_root=args.logs_root,
    )
    job = VideoJobConfig.create(
        input_video=args.input,
        video_id=args.video_id,
        character=args.character,
        series=args.series,
        frame_interval=args.frame_interval,
        textures_dir=args.textures_dir,
    )
    runtime = RuntimeConfig(
        dry_run=args.dry_run,
        skip_existing=not args.no_skip_existing,
        npz_export=args.npz_export,
        strict=args.strict,
    )
    return PipelineConfig(job=job, paths=paths, runtime=runtime)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)
    return run_pipeline(config)


if __name__ == "__main__":
    raise SystemExit(main())
