# Video2Multimodal3D
## A Video-Driven Multimodal 3D AI Training Data Preparation Pipeline

**Author**: Berkay Altuğ  
**Contact**: berkay_altug@outlook.com  
**Affiliation**: Independent Researcher and Developer

## Abstract

Video2Multimodal3D is a modular preprocessing system for converting raw object videos into a structured multimodal dataset layout for geometry-aware AI workflows. The pipeline is designed around a public orchestration layer that keeps heavyweight model checkpoints outside version control while preserving a stable dataset contract for research and production experiments.

The system organizes frame extraction, optional model-backed annotations, and dataset packaging around a reproducible workspace. Generated artifacts can include RGB frames, segmentation outputs, pose metadata, depth predictions, surface normal maps, captions, semantic tags, and packaged frame-level dataset manifests. The public release prioritizes dry-run validation, explicit configuration, and lightweight GitHub distribution.

## Problem Statement

Turning raw video captures into training-ready multimodal datasets is operationally expensive. Most local pipelines accumulate hard-coded paths, environment-specific assumptions, large vendor snapshots, and ad hoc execution patterns. These issues make the project difficult to share, reproduce, or publish.

This release addresses that gap by reframing the repository as:

- a clean public interface for single-video and batch processing
- a stable path and dataset contract
- a documented integration layer for heavy external models
- a lightweight GitHub-ready package

## Design Goals

The public release focuses on six goals:

1. Import-safe execution with no side effects at module import time.
2. Explicit configuration instead of hidden globals.
3. Dry-run support for validation before expensive execution.
4. Stable workspace layout across Windows development environments.
5. Exclusion of large checkpoints and vendor metadata from git.
6. Clear documentation for downstream research and reproducibility.

## Public Pipeline Contract

The pipeline is centered on three public interfaces:

- `pipeline/config.py`
  Defines `VideoJobConfig`, `RuntimeConfig`, `PathConfig`, and `PipelineConfig`.
- `pipeline/prep_pipeline.py`
  Exposes `main(config: PipelineConfig) -> int`.
- CLI entrypoints
  `run.py` for single videos and `run_batch.py` for CSV manifests.

This contract keeps orchestration logic stable even when individual model integrations evolve.

## Execution Model

The public orchestration layer currently performs the following high-level stages:

1. Validate the input job configuration.
2. Prepare the workspace directories and config snapshot.
3. Extract frames with FFmpeg.
4. Resolve optional integrations for pose, segmentation, depth, normal maps, captions, and tags.
5. Emit dataset manifests and summary logs.

Heavy inference stages remain explicit integration points because they require local checkpoints, GPU configuration, and third-party model packages that should not be committed to git.

## Dataset Contract

For each video job, the public release creates:

- a per-run config snapshot in `logs/`
- a JSON summary report in `logs/`
- a dataset manifest under `output_layers/data/<video_id>_data/`

The workspace layout reserves directories for the following modalities:

- RGB
- mask
- depth
- segments
- processed segmentation views
- normal maps
- pose overlays
- pose JSON
- captions
- tags
- textured inputs

This layout is intended to stay stable even when implementation details change.

## GitHub Release Strategy

The repository is prepared for public sharing with the following release decisions:

- large weights are ignored and checked via `scripts/download_weights.py`
- nested vendor git metadata is treated as non-public local state
- dry-run validation is a first-class workflow
- release verification is handled by `scripts/verify_release.py`
- smoke validation is handled by `scripts/smoke_test.py`

This keeps the repo lightweight while preserving a practical path back to full local execution.

## Research Context

The broader research motivation behind Video2Multimodal3D is multimodal 3D learning. The dataset layout is intended to support systems that learn from aligned appearance, geometry, structure, and semantics together.

This framing also supports future work on compositional image-conditioned 3D learning, where part-aware structure and geometry supervision become central to model quality.

## Current Limitations

- The public release does not bundle model checkpoints.
- Several advanced steps remain environment-dependent integrations rather than guaranteed built-in inference.
- Local runtime quality still depends on GPU, drivers, and third-party package compatibility.

These constraints are intentional because the release optimizes for public reproducibility and repository hygiene first.

## Next Steps

The next recommended milestones are:

1. Add project-specific execution adapters for the optional heavy steps.
2. Add integration tests around frame extraction and dataset manifest generation.
3. Publish a reproducible dependency file for the target training environment.
4. Connect the dataset outputs directly to downstream training experiments.

## Conclusion

Video2Multimodal3D now provides a public, GitHub-ready foundation for multimodal video-to-dataset preprocessing. The current release is intentionally lightweight, configuration-driven, and explicit about its external dependencies. That makes it suitable for open publication, collaborative development, and future research iteration without dragging local workstation state into version control.
