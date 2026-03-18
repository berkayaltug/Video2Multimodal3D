"""Dry-run smoke test for the public Video Pipeline release.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        sample_video = temp_root / "sample.mp4"
        sample_video.write_bytes(b"")

        run_cmd = [
            sys.executable,
            str(project_root / "run.py"),
            "--input",
            str(sample_video),
            "--video-id",
            "sample",
            "--character",
            "bust",
            "--series",
            "marvel",
            "--dry-run",
            "--project-root",
            str(temp_root),
        ]
        run_result = subprocess.run(run_cmd, check=False)
        if run_result.returncode != 0:
            return run_result.returncode

        manifest_path = temp_root / "videos.csv"
        with manifest_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["video_path", "video_id", "character", "series"])
            writer.writeheader()
            writer.writerow(
                {
                    "video_path": str(sample_video),
                    "video_id": "sample_a",
                    "character": "bust",
                    "series": "marvel",
                }
            )
            writer.writerow(
                {
                    "video_path": str(sample_video),
                    "video_id": "sample_b",
                    "character": "statue",
                    "series": "dc",
                }
            )

        batch_cmd = [
            sys.executable,
            str(project_root / "run_batch.py"),
            "--manifest",
            str(manifest_path),
            "--dry-run",
            "--project-root",
            str(project_root),
        ]
        batch_result = subprocess.run(batch_cmd, check=False)
        return batch_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
