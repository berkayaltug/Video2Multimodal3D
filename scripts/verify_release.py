"""Lightweight release verification for the public repository.

Author: Berkay Altuğ
Contact: berkay_altug@outlook.com
Affiliation: Independent Researcher and Developer
"""

from __future__ import annotations

import argparse
import py_compile
import re
from pathlib import Path


COMPILE_TARGETS = [
    "run.py",
    "run_batch.py",
    "pipeline/prep_pipeline.py",
    "pipeline/config.py",
    "models/depth_anything_infer.py",
    "models/stablenormal_infer.py",
    "pipeline/wdtagger.py",
]

LARGE_FILE_LIMIT = 100 * 1024 * 1024
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
IGNORED_LARGE_FILE_SUFFIXES = {".pt", ".pth", ".onnx", ".pb", ".bin", ".safetensors", ".gguf"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight GitHub release checks.")
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[1], help="Project root directory.")
    return parser


def compile_targets(project_root: Path) -> list[str]:
    errors = []
    for relative_path in COMPILE_TARGETS:
        try:
            py_compile.compile(str(project_root / relative_path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(str(exc))
    return errors


def find_nested_git_dirs(project_root: Path) -> list[str]:
    return [
        str(path)
        for path in project_root.rglob(".git")
        if path.is_dir() and path.parent != project_root
    ]


def find_large_files(project_root: Path) -> list[str]:
    return [
        f"{path} ({path.stat().st_size} bytes)"
        for path in project_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() not in IGNORED_LARGE_FILE_SUFFIXES
        and path.stat().st_size > LARGE_FILE_LIMIT
    ]


def validate_markdown_links(markdown_path: Path) -> list[str]:
    errors = []
    text = markdown_path.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        resolved = (markdown_path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"Broken link in {markdown_path.name}: {target}")
    return errors


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()

    errors = []
    errors.extend(compile_targets(project_root))
    errors.extend(f"Nested git directory: {path}" for path in find_nested_git_dirs(project_root))
    errors.extend(f"Large file exceeds GitHub limit: {path}" for path in find_large_files(project_root))

    for markdown_name in ("README.md", "WHITEPAPER.md"):
        markdown_path = project_root / markdown_name
        if not markdown_path.exists():
            errors.append(f"Missing required markdown file: {markdown_name}")
            continue
        errors.extend(validate_markdown_links(markdown_path))

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
