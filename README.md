<h1 align="center">Video2Multimodal3D</h1>
<p align="center">
  <strong>Video Pipeline for Multimodal 3D Data Preparation</strong><br>
</p>

<p align="center">
  <em>Video Pipeline is a lightweight public release of a research preprocessing system that turns raw turntable or handheld object videos into a structured, multimodal dataset layout for geometry-aware AI workflows.</em><br>
</p>

<p align="center">
  <strong>From raw object video to aligned multimodal 3D-ready training data</strong><br>
</p>

<p align="center">
  <img src="docs/video-pipeline.png" alt="Video Pipeline for Multimodal 3D Data Preparation" />
</p>

---

This repository packages the public-facing version of a larger internal preprocessing workflow. Its role is to bridge the gap between raw captured video and structured data that can later support multimodal 3D learning, geometry-aware supervision, and part-aware training workflows.

The repository is organized around a clean public contract:

- `run.py` is the single-video CLI.
- `run_batch.py` runs a CSV manifest.
- `pipeline/config.py` defines the pipeline configuration objects.
- `pipeline/prep_pipeline.py` is the import-safe orchestration layer.
- heavyweight checkpoints stay outside git and are checked with `scripts/download_weights.py`.

## Why This Repo Exists

The project addresses a practical gap between raw capture and trainable data:

`video -> aligned frames -> multimodal annotations -> dataset package`

The intended downstream use is multimodal 3D learning, especially research directions that combine appearance, geometry, structure, and semantics in the same training sample.

Raw RGB video by itself is not enough for robust 3D-oriented learning. A usable training sample generally needs:

- consistent frame identity
- modality alignment
- structural filtering
- reproducible packaging
- semantic and geometric side channels

This public release focuses on making that contract clean, documented, and publishable on GitHub.

## Core Design Goals

The current release is built around a few explicit engineering goals:

- import-safe execution with no hidden side effects
- explicit config objects instead of mutable module globals
- dry-run validation before heavy execution
- stable output contracts across local environments
- lightweight public distribution with external model weights kept outside git
- clear documentation for future research reuse

## End-to-End Pipeline

The broader pipeline concept follows the sequence below:

```text
Video
-> Frame extraction
-> RGB / mask preparation
-> Pose estimation
-> Segmentation
-> Depth prediction
-> Surface normal prediction
-> Caption generation
-> Tag generation
-> Dataset packaging
-> Logging and summary export
```

In the public release, frame extraction, workspace creation, config logging, dataset manifest generation, and summary reporting are first-class supported features. The heavier CV modules are retained as integration points so the repository stays lightweight and reproducible.

## Processing Stages

The whitepaper draft defines the system as a multi-stage data preparation chain. The most important stages are:

- `Frame extraction`
  Uses FFmpeg to sample frames from the source video at a configurable interval.
- `RGB and mask preparation`
  Establishes the canonical visual layer and foreground-aware preprocessing path.
- `Pose estimation`
  Generates pose overlays and pose JSON, and can also act as a structural validity filter.
- `Segmentation`
  Produces main object segmentation and part-level decomposition for part-aware learning.
- `Depth`
  Adds monocular geometric cues through Depth Anything integration.
- `Surface normals`
  Adds local orientation cues through StableNormal integration.
- `Caption and tagging`
  Adds semantic text metadata and prompt-oriented descriptors.
- `Packaging`
  Writes manifests, summaries, and training-oriented directory structures.

## Dataset Philosophy

The design principle behind the pipeline is not just to export images, but to keep all modalities centered on a shared frame identity. That means each frame can later become a training sample with aligned:

- appearance
- segmentation structure
- pose or structural metadata
- geometric depth cues
- surface orientation
- semantic text annotations

This is the key reason the repository reserves a stable directory layout even when some modules are optional in the public build.

## Repository Layout

```text
.
├── pipeline/
│   ├── config.py
│   ├── prep_pipeline.py
│   ├── pose_utils.py
│   ├── tag_prompt_synth.py
│   └── wdtagger.py
├── models/
│   ├── depth_anything_infer.py
│   └── stablenormal_infer.py
├── scripts/
│   ├── download_weights.py
│   ├── smoke_test.py
│   └── verify_release.py
├── docs/
│   ├── archive/WHITEPAPER_raw.md
│   └── release_checklist.md
├── run.py
├── run_batch.py
└── WHITEPAPER.md
```

## Setup

1. Create a Python environment.
2. Install the project dependencies you need for your enabled integrations.
3. Place large model checkpoints under `models/` without committing them to git.
4. Verify expected paths:

```bash
python scripts/download_weights.py
```

The public repo keeps heavyweight artifacts out of version control by design.

On Ubuntu / WSL you also need `ffmpeg` on `PATH` for frame extraction:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Quickstart

Single video dry-run:

```bash
python run.py --input input/sample.mp4 --video-id sample --character bust --series marvel --dry-run
```

Single video execution:

```bash
python run.py --input input/sample.mp4 --video-id sample --character bust --series marvel
```

Batch dry-run with a CSV manifest:

```bash
python run_batch.py --manifest input/videos.csv --dry-run
```

If the pipeline appears to exit silently during real execution, the first thing to verify is `ffmpeg` availability. Frame extraction is the first mandatory runtime dependency.

## Batch Manifest

The public batch contract is a CSV file with the following columns:

```text
video_path,video_id,character,series
```

An example file is included at [input/videos.csv](input/videos.csv).
Relative `video_path` values are resolved from the manifest directory.

## Output Structure

The orchestration layer creates a stable workspace under `output_layers/` and `logs/`.

```text
output_layers/
├── captions/
├── data/
│   └── <video_id>_data/
│       └── dataset_manifest.json
├── depth/
├── mask/
├── normal_map/
├── pose/
├── pose_json/
├── processed/
├── rgb/
├── segments/
├── tags/
└── textured/

logs/
├── <video_id>_config.json
├── <video_id>_summary.json
└── summary_log.txt
```

In the lightweight public release, the dataset manifest and summary files are guaranteed. Heavy inference outputs depend on locally installed adapters and weights.

## Quality Control and Skip Logic

The original pipeline design emphasized file-based validation and redundant process avoidance. That design intent is preserved here:

- dry-run checks validate the job before expensive execution
- existing outputs can be reused instead of recomputed
- config snapshots make runs auditable
- summary logs provide a compact record of what happened

This matters in practice because multimodal preprocessing is expensive, storage-heavy, and usually iterative.

## Research Framing

The updated whitepaper draft makes the broader intent clearer: this is not only a utility for extracting frames, but a data engineering layer for future 3D AI experiments. The pipeline is meant to support workflows where a model may eventually consume aligned RGB, structure, geometry, and semantics together instead of relying on a single visual channel.

That framing is especially relevant for:

- image-conditioned 3D learning
- geometry-aware representation learning
- part-aware or compositional training setups
- multimodal supervision experiments

## Verification

Run the release checks:

```bash
python scripts/verify_release.py
python scripts/smoke_test.py
```

The release checklist is available at [docs/release_checklist.md](docs/release_checklist.md).

## Research Context

This pipeline is part of a broader research effort around compositional, image-conditioned 3D learning. The dataset contract is designed to support future training systems that need aligned geometry, structure, and semantics rather than RGB-only supervision.

The public whitepaper lives in [WHITEPAPER.md](WHITEPAPER.md). The original working draft is archived at [docs/archive/WHITEPAPER_raw.md](docs/archive/WHITEPAPER_raw.md).

## Limitations

- Large checkpoints are intentionally excluded from git.
- Several heavy vision modules are documented as optional integration points in the public release.
- The public CLI guarantees dry-run validation first; full inference depends on local environment setup.

## License

MIT License — This repository is released under the terms of the [LICENSE](LICENSE).
