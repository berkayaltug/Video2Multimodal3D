"""Utility for checking external model weight placement.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WEIGHT_MANIFEST = {
    "pose": {
        "expected_path": "models/Yolo/yolo11x-pose.pt",
        "source": "Manual placement required. Download the Ultralytics YOLO pose weight and place it at the expected path.",
    },
    "segmentation": {
        "expected_path": "models/segment-anything/sam_vit_h_4b8939.pth",
        "source": "Manual placement required. Download the Segment Anything ViT-H checkpoint and place it at the expected path.",
    },
    "depth": {
        "expected_path": "models/depth_anything/checkpoints/depth_anything_v2_vitl.pth",
        "source": "Manual placement required. Download the Depth Anything V2 ViT-L checkpoint and place it at the expected path.",
    },
    "normal_map": {
        "expected_path": "models/StableNormal",
        "source": "Clone or export StableNormal into models/StableNormal/ so torch.hub can load it locally.",
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the presence of external model weights.")
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[1], help="Project root directory.")
    parser.add_argument("--json", action="store_true", help="Print the weight report as JSON.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()

    report = {}
    missing = 0
    for name, entry in WEIGHT_MANIFEST.items():
        expected_path = project_root / entry["expected_path"]
        exists = expected_path.exists()
        if not exists:
            missing += 1
        report[name] = {
            "expected_path": str(expected_path),
            "exists": exists,
            "source": entry["source"],
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for name, entry in report.items():
            status = "OK" if entry["exists"] else "MISSING"
            print(f"[{status}] {name}: {entry['expected_path']}")
            if not entry["exists"]:
                print(f"        {entry['source']}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
