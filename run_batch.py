"""Public batch CLI for Video Pipeline.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path


REQUIRED_COLUMNS = ("video_path", "video_id", "character", "series")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Video Pipeline for a CSV manifest of videos.")
    parser.add_argument("--manifest", required=True, help="CSV manifest with columns: video_path,video_id,character,series")
    parser.add_argument("--dry-run", action="store_true", help="Validate the manifest and print the jobs without running them.")
    parser.add_argument("--frame-interval", type=float, default=0.5, help="Frame sampling interval for all jobs.")
    parser.add_argument("--strict", action="store_true", help="Pass strict mode through to run.py")
    parser.add_argument("--npz-export", action="store_true", help="Pass NPZ export mode through to run.py")
    parser.add_argument("--project-root", default=Path(__file__).resolve().parent, help="Project root for locating run.py")
    parser.add_argument("--input-root", help="Optional input root override forwarded to run.py")
    parser.add_argument("--output-root", help="Optional output root override forwarded to run.py")
    parser.add_argument("--models-root", help="Optional models root override forwarded to run.py")
    parser.add_argument("--logs-root", help="Optional logs root override forwarded to run.py")
    return parser


def load_manifest(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Manifest is empty or missing a header row.")

        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Manifest is missing required column(s): {', '.join(missing)}")

        rows = []
        for index, row in enumerate(reader, start=2):
            normalized = {key: (value or "").strip() for key, value in row.items()}
            missing_values = [column for column in REQUIRED_COLUMNS if not normalized.get(column)]
            if missing_values:
                raise ValueError(
                    f"Manifest row {index} is missing required value(s): {', '.join(missing_values)}"
                )
            video_path = Path(normalized["video_path"])
            if not video_path.is_absolute():
                video_path = (manifest_path.parent / video_path).resolve()
            normalized["video_path"] = str(video_path)
            rows.append(normalized)
        return rows


def build_command(args: argparse.Namespace, row: dict[str, str], project_root: Path) -> list[str]:
    command = [
        sys.executable,
        str(project_root / "run.py"),
        "--input",
        row["video_path"],
        "--video-id",
        row["video_id"],
        "--character",
        row["character"],
        "--series",
        row["series"],
        "--frame-interval",
        str(args.frame_interval),
    ]
    if args.dry_run:
        command.append("--dry-run")
    if args.strict:
        command.append("--strict")
    if args.npz_export:
        command.append("--npz-export")

    for flag, value in (
        ("--input-root", args.input_root),
        ("--output-root", args.output_root),
        ("--models-root", args.models_root),
        ("--logs-root", args.logs_root),
    ):
        if value:
            command.extend([flag, value])
    return command


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()

    rows = load_manifest(manifest_path)
    print(f"Loaded {len(rows)} job(s) from {manifest_path}")

    for row in rows:
        command = build_command(args, row, project_root)
        if args.dry_run:
            print("DRY-RUN:", " ".join(command))
            continue

        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
