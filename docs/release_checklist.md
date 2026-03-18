# Release Checklist

1. Run `python scripts/verify_release.py`.
2. Run `python scripts/smoke_test.py`.
3. Confirm `README.md` and `WHITEPAPER.md` render correctly on GitHub.
4. Run `python scripts/download_weights.py` to verify model placement.
5. Initialize git with `git init` if the repo is not yet versioned.
6. Review `git status` to ensure weights, outputs, caches, and local inputs stay untracked.
7. Create the first commit and connect the remote.
8. Push the public-ready branch to GitHub.
