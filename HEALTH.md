# Health Check

> Status of the most recent attempt to run this fork end-to-end in the Hermes VM environment.
> Last verified: 2026-06-24.

## What was attempted

```bash
cd ~/projects/AmamooIntelligence
uv sync          # Pyproject.toml declares Python >=3.10; uv picked 3.13.12
uv run pytest    # (blocked by uv sync failure)
```

## Result

`uv sync` **failed in this environment** during the build-isolation phase:

```
Failed to build `openjarvis @ file:///home/hermes/projects/AmamooIntelligence`
Failed to resolve requirements from `build-system.requires`
No solution found when resolving: `hatchling`, `editables~=0.3`
Request failed after 3 retries
Failed to fetch: .../trove_classifiers-...whl.metadata (and other build deps)
error sending request for url (...) — operation timed out
```

### Root cause

The Hermes VM can reach `pypi.org` and `files.pythonhosted.org` directly (`curl` returns 200 in 2-7s), but `uv`'s internal HTTP client is intermittently timing out on metadata fetches during build-isolation. The exact failing URLs are reachable from the same machine via `curl`, so the issue is **transport-level inside uv** — not a PyPI outage or a missing package.

A 600-second retry with `UV_HTTP_TIMEOUT=300` still timed out.

## Workarounds for this environment

If you need to run `uv sync` from this VM:

1. **Pre-warm the build deps manually** with `pip` (which uses a different HTTP client), then re-run `uv sync`:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install hatchling "editables>=0.3" trove-classifiers maturin
   uv sync
   ```
2. **Disable build isolation** (only safe if the build deps are already installed in the venv):
   ```bash
   uv sync --no-build-isolation
   ```
3. **Run on a different machine** — the GitHub Actions runner used by the weekly upstream-sync workflow is on GitHub's infrastructure and has no such issue (see `.github/workflows/upstream-sync.yml`).

## What this means for the fork

- **No code defect.** The fork's commits are: docs, attribution, and one workflow file. None of those touch Python imports, so a `uv sync` failure cannot be caused by the fork layer.
- **The CI sync workflow doesn't depend on `uv sync`.** It only checks out the repo, fetches upstream, merges, and opens a PR. It runs on GitHub-hosted runners where this issue does not reproduce.
- **Local testing** requires either the workaround above or running on a different host.

If you can confirm `uv sync` works for you on a fresh machine, please open a PR to update the "Last verified" line at the top of this file with the new date and a green checkmark.