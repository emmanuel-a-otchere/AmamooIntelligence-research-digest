# AmamooIntelligence — Requirements Specification

| | |
|---|---|
| **Document version** | 1.0.0 |
| **Document date** | 2026-06-28 |
| **Repository** | `emmanuel-a-otchere/AmamooIntelligence` |
| **Upstream** | `open-jarvis/OpenJarvis` |
| **License** | Apache License, Version 2.0 (inherited from upstream) |
| **Document maintainer** | `@emmanuel-a-otchere` |
| **Status** | Living document — update on every architectural change |

> **Purpose.** This document is the canonical source of truth for what AmamooIntelligence is, what it does, how it is built, what it depends on, and where its limits lie. It exists so that:
>
> 1. A new contributor can understand the system without reading every file.
> 2. A future maintainer can decide what is in scope vs. accidental.
> 3. A reviewer evaluating a specialization proposal can compare it against the documented surface.
> 4. Anyone curious about licensing can find attribution and SPDX identifiers in one place.
>
> **Versioning.** This document follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
> - **MAJOR** — incompatible changes to scope, license, or architectural principles.
> - **MINOR** — new features, specializations, dependencies, or capabilities added in a backward-compatible way.
> - **PATCH** — clarifications, typo fixes, updated version numbers.
>
> The version number is recorded in **Appendix C — Change Log** along with what changed and why.

---

## Table of Contents

- [Part I — System Overview](#part-i--system-overview)
  - [1. Executive Summary](#1-executive-summary)
  - [2. Scope](#2-scope)
  - [3. License & Attribution](#3-license--attribution)
- [Part II — User-Facing Features](#part-ii--user-facing-features)
  - [4. Capabilities](#4-capabilities)
  - [5. Available Specializations](#5-available-specializations)
  - [6. Configuration Surface](#6-configuration-surface)
- [Part III — Backend Architecture](#part-iii--backend-architecture)
  - [7. System Architecture](#7-system-architecture)
  - [8. Data Flow](#8-data-flow)
  - [9. Storage & State Model](#9-storage--state-model)
  - [10. Security Boundary](#10-security-boundary)
- [Part IV — API Surface](#part-iv--api-surface)
  - [11. CLI Commands](#11-cli-commands)
  - [12. Python API](#12-python-api)
  - [13. Cron & Delivery Endpoints](#13-cron--delivery-endpoints)
- [Part V — Dependencies](#part-v--dependencies)
  - [14. Runtime Dependencies](#14-runtime-dependencies)
  - [15. Build & Test Dependencies](#15-build--test-dependencies)
  - [16. External Services](#16-external-services)
  - [17. Data Formats & Specifications](#17-data-formats--specifications)
  - [18. License Inventory](#18-license-inventory)
- [Part VI — Operations & Limitations](#part-vi--operations--limitations)
  - [19. Deployment Model](#19-deployment-model)
  - [20. Known Limitations](#20-known-limitations)
  - [21. Recovery & Rollback](#21-recovery--rollback)
  - [22. Monitoring & Observability](#22-monitoring--observability)
  - [23. Future Work / Non-Goals](#23-future-work--non-goals)
- [Appendix A — Source File Inventory](#appendix-a--source-file-inventory)
- [Appendix B — Test Coverage Snapshot](#appendix-b--test-coverage-snapshot)
- [Appendix C — Change Log](#appendix-c--change-log)

---

# Part I — System Overview

## 1. Executive Summary

**AmamooIntelligence** is a public fork of [`open-jarvis/OpenJarvis`](https://github.com/open-jarvis/OpenJarvis) — an Apache-2.0, Stanford-origin framework for building on-device personal-AI agents. The fork exists to **specialize** the upstream system for focused, vertical use cases while preserving the ability to pull weekly upstream improvements.

The fork adds three things on top of an unmodified upstream base:

1. **A weekly upstream-sync workflow** that opens — never auto-merges — pull requests when upstream `open-jarvis/OpenJarvis` advances. Bot branches `upstream-sync/<7-char-sha>` are auto-deleted after their PRs close.
2. **A specialization scaffold and playbook** (`docs/SPECIALIZING.md`, `use-cases/_template/`) that lets a downstream user or forker create new specializations on a feature branch without touching `src/openjarvis/core/`.
3. **One worked-example specialization** — `research-digest` — that demonstrates the pattern by ingesting RSS/Atom feeds and producing a daily morning briefing.

**Identity.** The fork is branded as `AmamooIntelligence` for downstream visibility, but it is and remains a derivative of `open-jarvis/OpenJarvis`. Every published artifact carries the Apache 2.0 license and credits upstream. The fork name appears in:

- The repository name on GitHub.
- The `ATTRIBUTION.md` file (forks do not claim upstream endorsement).
- README and `docs/` headers.
- Commit messages by the bot identity `upstream-sync-bot <upstream-sync-bot@users.noreply.github.com>`.
- The User-Agent string emitted by the `research-digest` specialization: `research-digest/0.1 (+amamoo)`.

## 2. Scope

### What this document covers

- The **fork infrastructure** added on top of upstream (2 workflows, 1 attribution file, 1 health file, 1 README banner, 4 docs, 1 scaffold).
- The **research-digest specialization** in its entirety — code, configuration, tests, documentation, planned promotion path.
- The **dependencies** required by the fork and the specialization (Python stdlib, third-party packages, system tools, GitHub Actions, external services).
- The **operational model** — how the fork is built, tested, deployed, synced, observed, and rolled back.

### What this document explicitly does NOT cover

- **The full upstream OpenJarvis codebase** — 1,000+ source files, 33 submodules, 40+ CLI commands. For upstream features, see [`open-jarvis/OpenJarvis` docs](https://open-jarvis.github.io/OpenJarvis/) and the project paper at [arxiv.org/abs/2605.17172](https://arxiv.org/abs/2605.17172).
- **The Tauri desktop GUI** (built and released by upstream's `desktop.yml` workflow) — included here only as an inherited capability.
- **The web frontend** (`frontend/`, port 5173) — inherited as-is.
- **The Rust acceleration layer** (`rust/crates/openjarvis-python/`) — inherited as-is.
- **MCP / A2A protocols** — inherited from upstream; the specialization does not use them.
- **Per-inference-engine backend details** (vLLM, MLX, SGLang, etc.) — the specialization uses Ollama only.

## 3. License & Attribution

### 3.1 Inherited license

This fork inherits the **Apache License, Version 2.0** from `open-jarvis/OpenJarvis` unchanged. The full text is preserved verbatim in `LICENSE` at the repository root. Key terms (per upstream Apache-2.0 §):

| Right | Granted | Notes |
|---|---|---|
| Commercial use | ✅ | |
| Modification | ✅ | Modified files must be marked. |
| Distribution | ✅ | `LICENSE` and `NOTICE` must travel with the work. |
| Sublicensing | ✅ | |
| Patent grant | ✅ | Implicit in Apache-2.0. |
| Trademark grant | ❌ | The name "OpenJarvis" is not granted; the fork name "AmamooIntelligence" is also not granted by upstream. |
| Patent retaliation | ⚠️ | Patent grant terminates if you sue over the Work. |

### 3.2 Attribution chain

```
open-jarvis/OpenJarvis    (Apache-2.0, © 2025 The OpenJarvis Authors)
       │
       │ forked 2026-06-24 by @emmanuel-a-otchere
       ▼
emmanuel-a-otchere/AmamooIntelligence    (Apache-2.0, © 2026 Emmanuel A. Otchere)
       │
       │ specialization branch usecase/research-digest
       ▼
specializations/research-digest/         (research-digest / 0.1, Apache-2.0)
```

### 3.3 Files that carry attribution

| File | What it credits |
|---|---|
| `LICENSE` | Full Apache 2.0 text (upstream copyright) |
| `ATTRIBUTION.md` | Upstream project name, repo URL, paper, fork date, contact |
| `README.md` | Fork banner with both `AmamooIntelligence` identity and `open-jarvis/OpenJarvis` lineage |
| `docs/REQUIREMENTS.md` | This document (Part V — License Inventory) |
| `specializations/research-digest/README.md` | Inherits Apache 2.0 |
| `specializations/research-digest/SPEC.md` | States Apache-2.0 inheritance explicitly |

### 3.4 Trademarks

Neither "OpenJarvis" nor "AmamooIntelligence" is granted as a trademark by either party. Use of these names in third-party contexts must not imply upstream endorsement.

---

# Part II — User-Facing Features

## 4. Capabilities

A user (or downstream forker) of AmamooIntelligence has access to two distinct capability surfaces:

### 4.1 Capabilities inherited from upstream OpenJarvis

These are available unchanged from the upstream codebase and are documented at [`open-jarvis.github.io/OpenJarvis`](https://open-jarvis.github.io/OpenJarvis/). They are listed here for completeness only — refer to upstream docs for the canonical reference.

| Capability | Inherited from | How exposed |
|---|---|---|
| CLI (`jarvis` command, ~40 subcommands) | `src/openjarvis/cli/` | Click-based console script `jarvis` |
| Python SDK (`from openjarvis import Jarvis`) | `src/openjarvis/sdk.py` | Python import |
| Tauri desktop GUI | `desktop/` + `rust/crates/openjarvis-python/` | `.dmg`/`.exe`/`.deb`/`.rpm`/`.AppImage` releases |
| Web frontend | `frontend/` | `localhost:5173` |
| FastAPI + SSE OpenAI-compatible server | `src/openjarvis/server/` | `jarvis serve` |
| 26+ messaging channels | `src/openjarvis/channels/` | Various SDKs |
| MCP / Google A2A | `src/openjarvis/mcp/`, `src/openjarvis/a2a/` | Protocol-native |
| Skills system (~13,700 community skills via OpenClaw) | `src/openjarvis/skills/` | `jarvis skill install` |
| Hardware-aware auto-config | `src/openjarvis/init/` | `jarvis init`, `jarvis doctor` |
| Energy & cost telemetry | `src/openjarvis/telemetry/` | `jarvis telemetry` |
| Adaptation layer (SFT, LoRA, GRPO) | `src/openjarvis/learning/` | `jarvis optimize` |

### 4.2 Capabilities added by the fork

| Capability | Where | How exposed |
|---|---|---|
| **Weekly upstream sync** | `.github/workflows/upstream-sync.yml` | GitHub Actions cron — Mon 06:00 UTC |
| **Bot-branch auto-cleanup** | `.github/workflows/cleanup-bot-branches.yml` | GitHub Actions — `pull_request: closed` |
| **Specialization scaffold** | `docs/SPECIALIZING.md`, `use-cases/_template/` | Human-authored files |
| **Specialization registry** | `use-cases/README.md` | Markdown index |
| **Health log** | `HEALTH.md` | Operator-facing markdown |
| **research-digest specialization** | `specializations/research-digest/` (branch `usecase/research-digest`) | TOML recipe + Python agent + RSS tool |

## 5. Available Specializations

### 5.1 Index

| Slug | Branch | Status | Description |
|---|---|---|---|
| `research-digest` | `usecase/research-digest` | Worked example (orchestrator stubbed, see § 20) | Daily morning briefing from RSS/Atom feeds |

### 5.2 research-digest — detail

**What it does.** Pulls fresh items from configured RSS / Atom feeds, identifies 2–4 themes, runs short deep-research passes per theme, synthesizes into a single Markdown briefing, optionally speaks it via TTS.

**What it actually ships (as of v1.0.0).** The RSS fetcher and the agent lifecycle scaffolding are complete and tested. The actual briefing generation is delegated to the upstream orchestrator agent — **the specialization ships a stub for that handoff** (see § 20.1). This makes the specialization a valid *demonstration of the pattern*, not a runnable end-to-end pipeline.

**Invocation patterns.**

| Pattern | Command | Where documented |
|---|---|---|
| Standalone (intended) | `uv run jarvis run --recipe configs/research-digest.toml --once` | `specializations/research-digest/README.md` |
| Scheduled | Configured in TOML `schedule.cron = "0 7 * * 1-5"` | `configs/research-digest.toml:9` |
| Test-only (current) | `uv run pytest tests/` | `specializations/research-digest/README.md` |

**Inputs.**

- Recipe: `configs/research-digest.toml`
- Default source bundle (4 feeds): HN RSS, arXiv cs.AI, arXiv cs.CL, MIT Tech Review.
- Operator can add sources — see `docs/SOURCES.md` for guidance.

**Outputs.**

- Markdown briefing: `briefings/{date}.md` (substituted at run time).
- Audio briefing: `briefings/{date}.mp3` (when `audio.enabled = true`).
- State sidecar: `{state_dir}/research_digest_state.json`.

## 6. Configuration Surface

### 6.1 Recipe TOML — `configs/research-digest.toml`

Full schema (verified against the file at commit `52fcd15`):

```toml
[meta]
version       = "1.0"          # string — recipe version
name          = "research_digest"  # string — slug, must match directory name

[model]
engine        = "ollama"       # string — inference engine key
model         = "qwen3:8b"     # string — model identifier

[schedule]
cron          = "0 7 * * 1-5"  # string — Vixie cron (5 fields)
timezone      = "local"        # string — "local" or IANA tz (e.g. "America/New_York")

[gather]
sources       = [...]          # list[string] — feed URLs (HTTPS only per docs)
max_items_per_source = 25      # int — cap items pulled per source

[cluster]
template      = "deep-researcher"  # string — upstream template
max_themes    = 4                 # int — cap themes to identify

[deep_research]
template      = "deep-researcher"  # string — upstream template
max_turns     = 8                 # int — turns per theme
min_citations = 3                 # int — min citations per theme

[synthesize]
output_path   = "briefings/{date}.md"  # string — {date} substituted at runtime

[audio]
enabled       = true              # bool
voice_provider = "edge"            # string — provider key
max_minutes   = 8                 # int — cap audio length
output_path   = "briefings/{date}.mp3"  # string

[agent]
type          = "orchestrator"    # string — upstream agent type
max_turns     = 60                # int — total workflow turns
temperature   = 0.4               # float — LLM temperature
tools         = [...]             # list[string] — tool identifiers
system_prompt = """..."""         # string — multi-line
```

### 6.2 Recipe tools referenced (8 total)

| Tool | Source | Used for |
|---|---|---|
| `rss_fetch` | This specialization (`src/tools/rss.py`) | Pull feeds |
| `web_search` | Upstream (`src/openjarvis/tools/web_search.py`) | General web search |
| `http_request` | Upstream (`src/openjarvis/tools/http_request.py`) | Direct HTTP fetches |
| `memory_store` | Upstream (`src/openjarvis/memory/`) | Persist intermediate state |
| `memory_search` | Upstream (`src/openjarvis/memory/`) | Recall past digests |
| `think` | Upstream (`src/openjarvis/tools/think.py`) | Reasoning step |
| `file_write` | Upstream (`src/openjarvis/tools/file_write.py`) | Write briefing files |
| `tts` | Upstream (`src/openjarvis/tools/tts.py`) | Audio version |

### 6.3 Environment variables

| Var | Purpose | Set by |
|---|---|---|
| `GITHUB_TOKEN` | Standard Actions token | GitHub Actions (auto) |
| `SYNC_TOKEN` | PAT with `workflow` scope | Repo secret (operator) |
| `GITHUB_OUTPUT` | Workflow step output | GitHub Actions (auto) |
| `OLLAMA_HOST` | Ollama endpoint | Operator (default `http://localhost:11434`) |

### 6.4 Repository secrets (production)

| Secret | Scope | Purpose |
|---|---|---|
| `SYNC_TOKEN` | `repo` + `workflow` | Lets the sync workflow push `upstream-sync/*` branches and the cleanup workflow delete them. `GITHUB_TOKEN` cannot do either due to GitHub Actions security boundary (community discussion #26583). |

---

# Part III — Backend Architecture

## 7. System Architecture

AmamooIntelligence has three concentric layers:

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3 — Specializations (this fork's differentiator)          │
│  • specializations/research-digest/                             │
│  • Future: specializations/*-*/                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ specialization pattern (no core modifications)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2 — Fork infrastructure (this fork's glue)               │
│  • .github/workflows/upstream-sync.yml                          │
│  • .github/workflows/cleanup-bot-branches.yml                   │
│  • docs/SPECIALIZING.md, docs/UPSTREAM-SYNC.md                  │
│  • use-cases/_template/, use-cases/README.md                    │
│  • ATTRIBUTION.md, HEALTH.md                                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ inherits unchanged, weekly sync
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 — Upstream OpenJarvis (Apache-2.0 base)                │
│  • 1,000+ source files, 33 submodules                           │
│  • Python SDK, CLI, Tauri desktop, web frontend, Rust layer     │
│  • Weekly sync from open-jarvis/OpenJarvis                      │
└─────────────────────────────────────────────────────────────────┘
```

### 7.1 Layer 1 — Upstream (inherited)

See [§ 4.1](#41-capabilities-inherited-from-upstream-openjarvis) for the capability list. Architecturally:

- **`src/openjarvis/`** — 33 submodules organized around five primitives (Intelligence, Engine, Agents, Tools & Memory, Learning).
- **`desktop/`** — Tauri/Rust GUI.
- **`frontend/`** — Vite + (likely) React/Vue web UI on port 5173.
- **`rust/crates/openjarvis-python/`** — Performance-critical Rust code, bridged via `_rust_bridge.py` and built with `maturin`.
- **`configs/openjarvis/`** — Default recipes: `morning-digest-mac`, `morning-digest-linux`, `morning-digest-minimal`, `deep-research`, `code-assistant`, `scheduled-monitor`, `chat-simple`.

### 7.2 Layer 2 — Fork infrastructure

**Sync workflow** — `.github/workflows/upstream-sync.yml`

| Trigger | When | What |
|---|---|---|
| Cron | Mondays 06:00 UTC | Compares `origin/main` to `upstream/main` |
| Manual dispatch | Any time | Same, with `force: true` to ignore the equality check |

Workflow steps:
1. `Checkout fork` (uses `SYNC_TOKEN` with `fetch-depth: 0`).
2. `Configure git` (bot identity `upstream-sync-bot <upstream-sync-bot@users.noreply.github.com>`).
3. `Add upstream remote` (`https://github.com/open-jarvis/OpenJarvis.git`).
4. `Check whether upstream has new commits` (compares SHAs).
5. `Merge upstream into bot branch` (creates `upstream-sync/<7-char-sha>` from `origin/main`, merges with `--no-ff`).
6. `Open or update PR` (via `actions/github-script@v7`, idempotent — updates an existing PR or creates a new one with title `chore(sync): upstream <7-char-sha> into main`).

**Skip conditions.** If `local == upstream` and `force` is not `true`, the workflow exits silently (no PR opened).

**Cleanup workflow** — `.github/workflows/cleanup-bot-branches.yml`

| Trigger | When | What |
|---|---|---|
| `pull_request: closed` | Any merged/closed PR | If head branch matches `upstream-sync/*`, delete it |

Why post-merge: GitHub restores the source branch when the merge commit is created (because the merge commit references it as a parent), so pre-merge deletion is undone. The reliable cleanup point is after the merge.

**Specialization scaffold** — `docs/SPECIALIZING.md` + `use-cases/_template/`

This is the human-facing playbook for creating a new specialization on a branch. The pattern is documented in `SPECIALIZING.md` and verified by the worked example on `usecase/research-digest`.

### 7.3 Layer 3 — Specializations

**`specializations/research-digest/`** — current sole specialization on branch `usecase/research-digest` (HEAD `52fcd15`).

Three modules:
- `src/tools/rss.py` — RSS 2.0 + Atom 1.0 fetcher, stdlib-only.
- `src/agents/research_digest.py` — Stateful scheduled agent that owns the digest lifecycle.
- `tests/` — 3 test files, 16 passing.

The full specialization tree is in [Appendix A](#appendix-a--source-file-inventory).

## 8. Data Flow

The specialization's intended data flow (when fully wired — see § 20.1 for the current stub state):

```
┌───────────────────────────────────────────────────────────────┐
│  1. TRIGGER (cron / manual)                                   │
│     schedule.cron = "0 7 * * 1-5" → ResearchDigestAgent.run() │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  2. IDEMPOTENCY CHECK                                         │
│     should_run() — same calendar day as last finished_at?     │
│     Yes → exit cleanly.  No → proceed.                        │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  3. GATHER                                                     │
│     For each source URL in recipe.gather.sources:             │
│       fetch_feed(url) → list[FeedItem]                        │
│     Max 25 items per source (per recipe).                     │
│     Fetcher: urllib.request, 15 s timeout, 2 MB hard cap.    │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  4. CLUSTER                                                    │
│     Identify 2–4 themes from gathered items.                  │
│     DELEGATED to upstream orchestrator (currently STUBBED).   │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  5. DEEP-RESEARCH (per theme)                                  │
│     Run deep-researcher template, max 8 turns,                │
│     min 3 citations per theme.                                │
│     DELEGATED to upstream orchestrator (currently STUBBED).   │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  6. SANITY-CHECK                                               │
│     Every URL in the candidate briefing must return 2xx.      │
│     Same logic as tests/test_url_sanity.py.                   │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  7. SYNTHESIZE                                                 │
│     Write briefings/{date}.md                                 │
│     DELEGATED to upstream orchestrator (currently STUBBED).   │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  8. AUDIO (optional)                                           │
│     If audio.enabled = true, call upstream tts tool.          │
│     Write briefings/{date}.mp3 (max 8 minutes).               │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  9. STATE PERSIST                                              │
│     Save DigestRun to {state_dir}/research_digest_state.json  │
│     Always saves, even on orchestrator failure.               │
└───────────────────────────────────────────────────────────────┘
```

### 8.1 Failure semantics

- **Per-source fetch failure** — logged at WARN, source is skipped, other sources continue.
- **Per-item parse failure** — logged at WARN, item is skipped, other items continue.
- **Orchestrator exception** — caught at `agent.run()`, logged, `str(exc)` stored in `run.errors`, state is still saved, `DigestRun` returned to caller.
- **State-load corruption** — `JSONDecodeError | KeyError | ValueError` is caught, logged at WARN, treated as fresh state.

## 9. Storage & State Model

### 9.1 Filesystem layout (per-deployment)

```
{deployment_root}/
├── configs/
│   └── research-digest.toml         # recipe (operator-supplied)
├── src/                             # (typically installed package, not on disk)
│   ├── agents/research_digest.py
│   └── tools/rss.py
├── briefings/
│   ├── 2026-06-28.md                # generated
│   └── 2026-06-28.mp3               # generated (if audio enabled)
└── {state_dir}/
    └── research_digest_state.json   # sidecar, persistent
```

### 9.2 State sidecar — `research_digest_state.json`

Shape (inferred from `research_digest.py:DigestRun.to_dict()`):

```json
{
  "started_at": "2026-06-28T07:00:00-04:00",
  "finished_at": "2026-06-28T07:08:42-04:00",
  "themes": ["theme 1", "theme 2", ...],
  "citations_total": 12,
  "output_path": "briefings/2026-06-28.md",
  "audio_path": "briefings/2026-06-28.mp3",
  "errors": []
}
```

Persistence rules:
- One file per `state_dir`, overwritten on each run (not appended).
- Write is best-effort; a failed write is logged but does not fail the run.

### 9.3 GitHub-side storage

- **Bot branches** (`upstream-sync/*`) — kept briefly until the cleanup workflow fires; deleted post-merge.
- **Sync PRs** — opened on `origin/main`, never auto-merged, dismissed after merge (the PR closes via the merge UI).
- **Repo secrets** — `SYNC_TOKEN` is the only one stored.

## 10. Security Boundary

### 10.1 GitHub Actions security boundary (GitHub community discussion #26583)

GitHub's auto-generated `GITHUB_TOKEN` **cannot**:
- Create, update, or delete workflow files (`.github/workflows/*.yml`).
- Push branches whose commits include workflow-file changes.

This is a hard security boundary, not configurable. The fix is to use a Personal Access Token (PAT) or GitHub App token with the `workflow` scope.

**In this repo:**
- `SYNC_TOKEN` is a PAT stored as a repo secret. It has `repo` + `workflow` scope.
- `upstream-sync.yml` uses `SYNC_TOKEN` for `actions/checkout` so the bot can push branches that contain modified workflow files (which upstream regularly introduces).
- `cleanup-bot-branches.yml` uses `SYNC_TOKEN` for the same reason on branch delete.
- `GITHUB_TOKEN` is used implicitly for `actions/github-script@v7` PR creation (which doesn't touch workflows).

### 10.2 Per-workflow permissions

The `permissions:` block is **intentionally absent** from both fork workflows:

- It does NOT accept a `workflows` key (GitHub rejects the YAML at parse time — HTTP 422 on dispatch).
- Without a per-workflow block, the workflow inherits the **repo-level setting** (`Read and write permissions`, set in `Settings → Actions → General → Workflow permissions`).

If you ever want to lock down other workflows in this repo, do it at the repo level.

### 10.3 RSS fetcher — bandit suppression

`src/tools/rss.py` includes `# noqa: S310` on the `urlopen` call. This is a deliberate bandit suppression because URLs come from operator config, not user input. URLs are validated at the recipe level (operator-supplied TOML), not at runtime.

### 10.4 Operator-configured network endpoints

The fetcher will hit whatever URL set the operator configures. There is **no runtime allow-list or denylist**. Operators are responsible for choosing reputable sources.

---

# Part IV — API Surface

## 11. CLI Commands

### 11.1 Fork-level commands (added by this fork)

There are **no new CLI commands** added by the fork. Both fork workflows are GitHub Actions, not user-facing CLIs.

### 11.2 Upstream CLI commands (inherited, listed for reference)

Per upstream `src/openjarvis/cli/__init__.py`:

| Group | Commands |
|---|---|
| Lifecycle | `init`, `doctor`, `quickstart`, `self-update` |
| Runtime | `ask`, `chat`, `serve`, `host`, `gateway`, `tunnel` |
| Models | `model`, `add` |
| Memory | `memory`, `mine`, `pearl` |
| Agents & workflows | `agents`, `workflow`, `skill`, `tool`, `operators`, `compose`, `registry` |
| Schedules / daemon | `scheduler`, `start`, `stop`, `restart`, `status` |
| Telemetry / evals | `telemetry`, `bench`, `eval`, `feedback`, `optimize` |
| Channels | `channel`, `channels`, `connect`, `digest`, `deep-research-setup`, `auth`, `scan`, `vault`, `config` |

For full CLI reference, see upstream docs.

## 12. Python API

### 12.1 `src/tools/rss.py` — public API

```python
@dataclass
class FeedItem:
    title: str
    link: str
    published: datetime | None
    summary: str
    source: str

def fetch_feed(url: str) -> list[FeedItem]:
    """Fetch and parse one RSS 2.0 or Atom 1.0 feed.

    Args:
        url: HTTPS URL of the feed (operator-configured).

    Returns:
        Flat list of parsed items. Empty list on any error
        (logged at WARN, never raises).

    Constraints:
        - 15 s timeout
        - 2 MB hard cap (raises ValueError internally, caught and
          logged; returns [] from the user's perspective)
        - User-Agent: "research-digest/0.1 (+amamoo)"
    """
```

Private helpers (not exported; leading underscore):
- `_fetch(url: str) -> bytes` — GET with timeout + size cap.
- `_parse_dt(text: str | None) -> datetime | None` — RFC 822 → ISO 8601 fallback.
- `_text(elem: ET.Element | None) -> str` — safe text extraction.

### 12.2 `src/agents/research_digest.py` — public API

```python
@dataclass
class DigestRun:
    started_at: datetime
    finished_at: datetime | None = None
    themes: list[str] = field(default_factory=list)
    citations_total: int = 0
    output_path: str | None = None
    audio_path: str | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]: ...

class ResearchDigestAgent:
    def __init__(
        self,
        recipe_path: str | Path,
        state_dir: str | Path,
    ): ...

    def should_run(self, now: datetime | None = None) -> bool:
        """Day-granularity idempotency. False if last finished_at is same day."""

    def run(self, now: datetime | None = None) -> DigestRun:
        """Execute the digest workflow. Always saves state, always returns."""

    def _invoke_orchestrator(self, run: DigestRun) -> None:
        """STUB — see § 20.1. Logs and records empty results."""
```

### 12.3 Internal helper convention

Public API = no leading underscore. Internal helpers = leading underscore. **Tests assert only the public API.**

## 13. Cron & Delivery Endpoints

### 13.1 GitHub-hosted schedules

| Schedule | Cron | Workflow | Action |
|---|---|---|---|
| Weekly (Mondays 06:00 UTC) | `0 6 * * 1` | `Sync upstream` | Open sync PR if upstream advanced |
| Daily (06:00 UTC) | `0 6 * * *` | `track-clones` | Inherited from upstream |
| Daily (06:00 UTC) | `0 6 * * *` | `installer-integration` | Inherited from upstream |
| PR-closed (event) | n/a | `Cleanup bot branches` | Delete `upstream-sync/*` branch |

### 13.2 Operator-side cron (planned, not implemented)

The specialization's recipe has `[schedule].cron = "0 7 * * 1-5"`. This is interpreted by the orchestrator, which the operator must deploy (e.g., via systemd timer, cron, or the upstream `jarvis scheduler start` daemon). **The specialization does not ship a cron config** — see § 20.2.

### 13.3 Manual dispatch

Both fork workflows (`upstream-sync.yml`, `cleanup-bot-branches.yml`) accept manual dispatch via the GitHub Actions UI. The sync workflow exposes a `force: bool` input that bypasses the "in sync" check.

---

# Part V — Dependencies

> This section is the canonical inventory. If a dependency changes, this section must be updated in the same commit (see Appendix C — Change Log convention).

## 14. Runtime Dependencies

### 14.1 Python third-party packages (declared in root `pyproject.toml`)

| Package | Version floor | Purpose | Used by specialization? |
|---|---|---|---|
| `click` | `>=8` | CLI framework | No (inherited base) |
| `datasets` | `>=4.5.0` | Training data utils | No |
| `httpx` | `>=0.27` | HTTP client | **No** (specialization uses stdlib `urllib`) |
| `openai` | `>=1.30` | OpenAI SDK | No (recipe uses Ollama, not OpenAI) |
| `rich` | `>=13` | Pretty CLI output | No |
| `tomli` | `>=2.0` (`python_version < '3.11'`) | TOML backport | Yes (via test_recipe_loads.py) |
| `maturin` | `>=1.12.6` | Build Rust extension | No |
| `croniter` | `>=2.0` | Cron parsing | No (recipe is TOML; cron parsing is upstream concern) |
| `mkdocs` + `mkdocs-material` + `mkdocstrings[python]` + `mkdocs-gen-files` + `mkdocs-literate-nav` | various | Docs site | No |

### 14.2 Upstream optional extras (declared but unused by specialization)

| Package | Version | Why declared |
|---|---|---|
| `mlx-lm` | `>=0.19` (`sys_platform == 'darwin'`) | Apple Silicon inference |
| `vllm` | `>=0.16.0` | GPU inference |
| `anthropic`, `google-genai`, `litellm` | various | Multi-provider LLM routing |
| `faiss-cpu`, `sentence-transformers`, `numpy` | various | Vector memory + embeddings |
| `torch`, `transformers`, `dspy`, `gepa` | various | Learning layer |
| `pdfplumber`, `rank-bm25` | various | Document parsing + retrieval |
| `fastapi`, `uvicorn`, `pydantic`, `python-multipart` | various | HTTP server |
| `openhands-sdk` | `>=1.0` (`python_version >= '3.12'`) | OpenHands integration |
| `pynvml`, `amdsmi`, `zeus-ml[apple]` | various | Hardware telemetry |
| Channel SDKs | various | 26+ messaging integrations |
| `playwright` | `>=1.40` | Browser automation |
| `cryptography`, `wasmtime`, `docker` | various | Security + sandboxing |
| `textual` | `>=0.80` | TUI dashboard |
| `faster-whisper`, `deepgram-sdk` | various | STT |
| `wandb`, `gspread`, `google-auth` | various | Eval + Sheets |

> **Important.** The specialization ships with **no `pyproject.toml` of its own**. All deps are inherited from the root. If you extract the specialization to a standalone package, copy the test-only `tomli` declaration explicitly.

### 14.3 Python stdlib modules used by specialization

| Module | File | Purpose |
|---|---|---|
| `__future__` | both | PEP 563 postponed annotations |
| `logging` | both | Structured WARN logging |
| `xml.etree.ElementTree` | `rss.py` | RSS/Atom parsing |
| `dataclasses` | both | `@dataclass` definitions |
| `datetime` | both | Date parsing + run timestamps |
| `urllib.request` | `rss.py` | HTTP GET |
| `urllib.error` | `rss.py` | Exception handling |
| `json` | `research_digest.py` | State persistence |
| `pathlib` | both | Path handling |
| `typing` | `research_digest.py` | `Any` annotation |
| `tomllib` (Py≥3.11) or `tomli` (Py<3.11) | `tests/test_recipe_loads.py` | Recipe parsing in tests |
| `sys` | `conftest.py`s | `sys.path` injection |
| `re` | `tests/test_url_sanity.py` | URL extraction |

### 14.4 System dependencies (declared in Dockerfiles / shell scripts)

| Dep | Where | Why |
|---|---|---|
| `python3` (3.12) | All Dockerfiles | Runtime |
| `node` (22) | Dockerfiles, `desktop.yml` | Tauri build + frontend |
| `bash` | `scripts/*.sh` | Shebang |
| `curl` | `scripts/quickstart.sh` | Bootstrap installers |
| `uv` | All Python workflows | Package management |
| `ollama` | `scripts/quickstart.sh`, recipe | Default inference engine |
| `npm` | `scripts/quickstart.sh`, `frontend.yml` | Frontend build |
| `brew` (macOS only) | `scripts/quickstart.sh` | Install on macOS |
| `apt` packages | `desktop.yml` | Tauri runtime (libwebkit2gtk, libgtk-3, etc.) |
| NVIDIA CUDA 12.4 | `deploy/docker/Dockerfile.gpu` | GPU inference |
| AMD ROCm 6.2 | `deploy/docker/Dockerfile.gpu.rocm` | AMD GPU inference |
| Rust stable + clippy | `ci.yml`, `desktop.yml` | Rust builds |
| Rust targets (`aarch64-apple-darwin`, etc.) | `desktop.yml` | Tauri cross-compile |

### 14.5 Resolved versions (from `uv.lock`)

363 packages total in the transitive lock. The specialization's runtime footprint is much smaller:

- **Specialization runtime** (transitive, via inherited `pyproject.toml`): `click`, `rich`, `httpx`, `openai`, `datasets` + stdlib.
- **Specialization test runtime**: above + `pytest` + `tomli` (Py<3.11).
- **True minimal runtime** (what the specialization *actually* uses at runtime): stdlib + `click` + `rich` (for the orchestrator's CLI output).

## 15. Build & Test Dependencies

### 15.1 Build

| Tool | Version | Where |
|---|---|---|
| `hatchling` | unpinned | `pyproject.toml:2` (PEP 517 backend) |
| `maturin` | `>=1.12.6` | `pyproject.toml:23, 135` (Rust extension) |
| `node` | 22 | Dockerfiles, `desktop.yml`, `frontend.yml` |
| `npm` | (latest) | `frontend.yml`, `scripts/quickstart.sh` |
| `rust` | stable + clippy | `ci.yml`, `desktop.yml` |
| `uv` | (latest) | All Python workflows |

### 15.2 Test

| Tool | Version | Purpose |
|---|---|---|
| `pytest` | `>=8` | Test runner |
| `pytest-asyncio` | `>=0.24` | Async test support (declared, not used by specialization) |
| `pytest-cov` | `>=5` | Coverage (declared, not used by specialization) |
| `respx` | `>=0.22` | httpx mocking (declared, not used by specialization) |
| `ruff` | `>=0.4` | Lint + format |

### 15.3 GitHub Actions (pinned to major version — not commit SHA)

| Action | Version | License | Used in |
|---|---|---|---|
| `actions/checkout` | `@v4` | MIT | All sync/ci/desktop/docs/frontend/upstream workflows |
| `actions/setup-python` | `@v5` | MIT | ci, docs |
| `actions/setup-node` | `@v4` | MIT | desktop, frontend |
| `astral-sh/setup-uv` | `@v4` | MIT | ci, docs |
| `dtolnay/rust-toolchain` | `@stable` | MIT | ci, desktop |
| `actions/cache` | `@v4` | MIT | ci |
| `swatinem/rust-cache` | `@v2` | MPL-2.0 | desktop |
| `tauri-apps/tauri-action` | `@v0` | MIT | desktop |
| `actions/github-script` | `@v7` | MIT | upstream-sync |
| `actions/upload-pages-artifact` | `@v3` | MIT | docs |
| `actions/deploy-pages` | `@v4` | MIT | docs |

> **Hardening note.** `@v4`, `@v5`, etc. are floating tags. For a higher-assurance supply chain, pin to commit SHAs. **Not a defect; a soft recommendation.**

### 15.4 GitHub-hosted runners

| Runner | Implied env (2026) |
|---|---|
| `ubuntu-latest` | Ubuntu 24.04 LTS (Noble) — Python 3.12, Node.js 20 preinstalled |
| `ubuntu-22.04` | Ubuntu 22.04 LTS (Jammy) — pinned for Tauri GTK 3 build |
| `macos-latest` | macOS 14/15 + Xcode CLT + Rust darwin targets |
| `windows-latest` | Windows Server 2022 + VS Build Tools + Rust MSVC |

## 16. External Services

### 16.1 RSS / Atom feeds (default, declared in recipe)

| URL | Protocol | Notes |
|---|---|---|
| `https://news.ycombinator.com/rss` | HTTPS | Hacker News |
| `https://arxiv.org/rss/cs.AI` | HTTPS | arXiv AI |
| `https://arxiv.org/rss/cs.CL` | HTTPS | arXiv Computation & Language |
| `https://www.technologyreview.com/feed/` | HTTPS | MIT Tech Review |

### 16.2 RSS / Atom feeds (suggested, not default — `docs/SOURCES.md`)

| URL | Notes |
|---|---|
| `https://arxiv.org/rss/cs.LG` | arXiv ML |
| `https://huggingface.co/blog/feed.xml` | HuggingFace |
| `https://feeds.arstechnica.com/arstechnica/index` | Ars Technica |
| `https://www.schneier.com/feed/atom/` | Schneier (Atom) |
| `https://krebsonsecurity.com/feed/` | Krebs |
| `https://feeds.feedburner.com/TheHackersNews` | The Hacker News |
| `https://www.nature.com/nature.rss` | Nature |
| `https://www.sciencemag.org/rss/news_current.xml` | Science Magazine |

### 16.3 Inference engine

| Endpoint | Purpose |
|---|---|
| Ollama at `http://localhost:11434` (default `OLLAMA_HOST`) | Recipe's `engine.key = "ollama"` |
| Model `qwen3:8b` | Recipe's `model.model` |

### 16.4 CI / automation services

| Service | Where | Purpose |
|---|---|---|
| `https://github.com/open-jarvis/OpenJarvis.git` | `upstream-sync.yml` | Upstream remote |
| GitHub Releases API | `desktop.yml` | Delete stale desktop assets |
| GitHub Pages | `docs.yml` | Deploy MkDocs site |
| PyPI (transitive) | All `uv sync` invocations | Resolves declared packages |
| Tauri update server | `desktop.yml` | Desktop app updater manifest |

### 16.5 External service risk surfaces

- The specialization is **fully external-dependent at runtime**: it hits 4 default RSS endpoints over HTTPS at every run.
- `test_url_sanity.py` runs a HEAD request against every URL in the sample briefing; CI will fail if any default source is down. The current fixture is stable (technologyreview.com, wikipedia.org, arxiv.org, example.com).
- There is no runtime allow-list or denylist. Operators choose what the specialization fetches.

## 17. Data Formats & Specifications

| Format | Spec | Used in | Parser |
|---|---|---|---|
| **RSS 2.0** | RSS 2.0.10 (Harvard Law) | `rss.py` | `xml.etree.ElementTree` |
| **Atom 1.0** | RFC 4287 | `rss.py` | `xml.etree.ElementTree` |
| **TOML** | TOML v1.0 (PEP 680 for Py≥3.11) | Recipe, `pyproject.toml`, upstream templates | `tomllib` / `tomli` |
| **Markdown** | CommonMark-ish | Output briefings + URL regex extraction | Regex only |
| **JSON** | RFC 8259 | State sidecar, GitHub Actions `$GITHUB_OUTPUT`, Tauri config | `json` stdlib |
| **XML** | W3C XML 1.0 | Both feed formats | `xml.etree.ElementTree` |
| **RFC 822 dates** | RFC 822 §5 | RSS `<pubDate>` | `datetime.strptime` |
| **ISO 8601 dates** | ISO 8601 / RFC 3339 | Atom `<updated>` / `<published>`, state sidecar | `datetime.fromisoformat` |
| **Cron expressions** | Vixie cron (5-field) | Recipe `[schedule].cron`, `upstream-sync.yml` cron | `croniter>=2.0` (upstream), GitHub Actions scheduler |
| **Semver** | semver.org 2.0.0 | `scripts/bump-desktop-version.sh` regex | Bash regex |
| **HTTP** | RFC 7230+ | All `urlopen` calls | `urllib.request` |

## 18. License Inventory

| Component | License | Source URL | Copyright |
|---|---|---|---|
| **AmamooIntelligence fork** | Apache-2.0 | https://github.com/emmanuel-a-otchere/AmamooIntelligence | © 2026 Emmanuel A. Otchere |
| **Upstream OpenJarvis** | Apache-2.0 | https://github.com/open-jarvis/OpenJarvis | © 2025 The OpenJarvis Authors |
| **research-digest specialization** | Apache-2.0 | (in this repo, branch `usecase/research-digest`) | © 2026 Emmanuel A. Otchere |

### 18.1 Python third-party licenses (declared dependencies)

| Package | License | Source |
|---|---|---|
| `click` | BSD-3-Clause | https://github.com/pallets/click |
| `datasets` | Apache-2.0 | https://github.com/huggingface/datasets |
| `httpx` | BSD-3-Clause | https://github.com/encode/httpx |
| `openai` | Apache-2.0 | https://github.com/openai/openai-python |
| `rich` | MIT | https://github.com/Textualize/rich |
| `tomli` | MIT | https://github.com/hukkin/tomli |
| `maturin` | Apache-2.0 / MIT | https://github.com/PyO3/maturin |
| `pytest` | MIT | https://github.com/pytest-dev/pytest |
| `pytest-asyncio` | Apache-2.0 | https://github.com/pytest-dev/pytest-asyncio |
| `pytest-cov` | MIT | https://github.com/pytest-dev/pytest-cov |
| `respx` | BSD-3-Clause | https://github.com/ldstep/prefect-respx |
| `ruff` | MIT | https://github.com/astral-sh/ruff |
| `croniter` | MIT | https://github.com/kiorky/croniter |
| `mkdocs` | BSD-2-Clause | https://github.com/mkdocs/mkdocs |
| `mkdocs-material` | MIT | https://github.com/squidfunk/mkdocs-material |
| `mkdocstrings` | MIT | https://github.com/mkdocstrings/mkdocstrings |

### 18.2 GitHub Actions licenses

| Action | License | Source |
|---|---|---|
| `actions/checkout` | MIT | https://github.com/actions/checkout |
| `actions/setup-python` | MIT | https://github.com/actions/setup-python |
| `actions/setup-node` | MIT | https://github.com/actions/setup-node |
| `actions/cache` | MIT | https://github.com/actions/cache |
| `actions/github-script` | MIT | https://github.com/actions/github-script |
| `actions/upload-pages-artifact` | MIT | https://github.com/actions/upload-pages-artifact |
| `actions/deploy-pages` | MIT | https://github.com/actions/deploy-pages |
| `astral-sh/setup-uv` | MIT | https://github.com/astral-sh/setup-uv |
| `dtolnay/rust-toolchain` | MIT | https://github.com/dtolnay/rust-toolchain |
| `swatinem/rust-cache` | MPL-2.0 | https://github.com/Swatinem/rust-cache |
| `tauri-apps/tauri-action` | MIT | https://github.com/tauri-apps/tauri-action |

### 18.3 Container base images

| Image | License | Source |
|---|---|---|
| `node:22-slim` | MIT (Node.js) | https://hub.docker.com/_/node |
| `python:3.12-slim` | PSF (Python) | https://hub.docker.com/_/python |
| `nvidia/cuda:12.4.0-runtime-ubuntu22.04` | NVIDIA EULA | https://hub.docker.com/r/nvidia/cuda |
| `rocm/dev-ubuntu-22.04:6.2` | MIT (ROCm) | https://hub.docker.com/r/rocm/dev-ubuntu |

> **Hardening note.** Dockerfiles use unpinned major-version tags (`node:22-slim`, `python:3.12-slim`), not digests. For reproducible builds, pin to `@sha256:...` digests. **Not a defect; a soft recommendation.**

---

# Part VI — Operations & Limitations

## 19. Deployment Model

### 19.1 The fork itself

- Hosted at `https://github.com/emmanuel-a-otchere/AmamooIntelligence`.
- Default branch: `main`.
- Visibility: public.
- License: Apache-2.0 (inherited).
- No branch protection enabled on `main` (PRs are merged at the maintainer's discretion).

### 19.2 How to deploy the specialization

**Current state: not end-to-end runnable.** The specialization is a worked example — the RSS fetcher and agent lifecycle work, but the orchestrator handoff is stubbed. To make it runnable end-to-end:

1. **Operator implementation of `_invoke_orchestrator`.** Override the method in `ResearchDigestAgent` to call upstream `openjarvis.agents.orchestrator.OrchestratorAgent` (or whichever orchestrator the deployment uses) with the recipe's `[agent]` block. The specialization is intentionally agnostic about which orchestrator runs the workflow — it only needs the call to populate `run.themes`, `run.citations_total`, `run.output_path`, and (if audio is enabled) `run.audio_path`.
2. **Recipe deployment.** Place `configs/research-digest.toml` where the orchestrator can find it (e.g., `~/.openjarvis/recipes/research-digest.toml`).
3. **Source configuration.** Edit the `gather.sources` list to match the operator's interests.
4. **Schedule.** Wire the cron into whatever scheduler runs the orchestrator (systemd timer, cron, upstream `jarvis scheduler start` daemon, etc.).
5. **Inference.** Ensure Ollama is running with `qwen3:8b` available (or change the model in the recipe).

### 19.3 Container deployments (inherited)

| Dockerfile | Purpose |
|---|---|
| `deploy/docker/Dockerfile` | CPU-only server build |
| `deploy/docker/Dockerfile.gpu` | NVIDIA GPU server build |
| `deploy/docker/Dockerfile.gpu.rocm` | AMD ROCm server build |
| `deploy/docker/Dockerfile.sandbox` | Sandbox runtime |

### 19.4 Desktop deployment (inherited)

Tauri-based `.dmg` / `.exe` / `.deb` / `.rpm` / `.AppImage` releases, built by upstream's `desktop.yml` on tags.

## 20. Known Limitations

### 20.1 The orchestrator handoff is a stub

`ResearchDigestAgent._invoke_orchestrator()` is an **explicit no-op**:

```python
def _invoke_orchestrator(self, run: DigestRun) -> None:
    """Hook for the upstream orchestrator. Implemented by the deployer.

    This stub records the intent without performing the call. A real
    deployment wires this to `openjarvis.agents.orchestrator.OrchestratorAgent`.
    """
    logger.info("Orchestrator invocation is a no-op in this specialization stub.")
    run.themes = []
    run.citations_total = 0
```

The comment is self-aware — the specialization is intentionally not runnable end-to-end. It demonstrates the pattern; the deployer wires the actual orchestrator. **This is by design, not an oversight.**

Implications:
- The `SPEC.md` success criteria (themes identified, deep-research passes, citations, briefing synthesized) are **not currently met by automated tests** because they cannot be exercised without the orchestrator wired up.
- `run()`, `should_run()`, state persistence, and idempotency **are** testable in principle but **are not currently tested**. See Appendix B for the test gap.

### 20.2 No operator-side cron ships with the specialization

The recipe declares `[schedule].cron = "0 7 * * 1-5"`, but **there is no systemd timer, crontab, or other scheduler file** shipped in the specialization. Operators must wire it themselves.

### 20.3 Documentation-vs-implementation drift in `rss.py`

`docs/SOURCES.md` advertises two behaviours that `src/tools/rss.py` does not implement:

1. **`require_https = true` by default** — advertised but not enforced. The fetcher will happily GET any HTTP URL the operator configures.
2. **Parallel fetch, capped at 8 concurrent** — advertised but not implemented. The fetcher is strictly sequential, single-URL.

Either the docs should be corrected to match the implementation, or the implementation should be brought into compliance. **Not a defect; a known drift.**

### 20.4 Path drift in the specialization's own docs

`OVERLAY.md`, `README.md`, and `SPEC.md` reference the path `use-cases/research-digest/`. The actual on-disk tree lives at `specializations/research-digest/`. The pytest commands in those docs will not work without path adjustment.

### 20.5 `uv sync` may time out in some VMs

Documented in `HEALTH.md`. PyPI metadata fetches can time out via `uv`'s internal transport; direct `curl` to PyPI works in 2–7s. Workaround: use `--no-binary :all:` or copy deps via `pip download`. Not blocking the workflow but documented.

### 20.6 `httpx` declared but unused by specialization

Root `pyproject.toml:14` declares `httpx>=0.27`. The specialization's `rss.py` uses stdlib `urllib.request` instead. Trimming `httpx` from base would not affect the specialization.

### 20.7 GitHub Actions security boundary (recap)

`GITHUB_TOKEN` cannot push workflow-file changes. The fork uses `SYNC_TOKEN` (PAT with `workflow` scope) to work around this. See § 10.1.

### 20.8 `tomli` fallback is conditionally declared

`tests/test_recipe_loads.py` falls back to `tomli` on Python <3.11. The declaration is in the root `pyproject.toml` as `tomli>=2.0; python_version < '3.11'`. If the specialization is extracted to a standalone package, copy this declaration explicitly.

### 20.9 Floating-version Docker and Action tags

Dockerfiles use `node:22-slim`, `python:3.12-slim` (floating major tags). Actions are pinned to `@v4` / `@v5` etc. (floating major tags). For reproducible builds and higher supply-chain assurance, pin to commit SHAs and image digests. **Not a defect; a soft recommendation.**

## 21. Recovery & Rollback

### 21.1 Reverting a sync PR

If a sync PR has not been merged:
- Close it in the GitHub UI. The bot branch can be left or deleted manually.

If a sync PR has been merged and broke something:
- `git revert <merge-sha>` on `main`.
- Or use the GitHub UI's "Revert" button.

### 21.2 Re-running the sync

Manual dispatch via `Actions → Sync upstream → Run workflow → force: true`. The bot will re-detect upstream HEAD and open a fresh PR.

### 21.3 Recovering from a bot-branch mess

If multiple `upstream-sync/*` branches accumulate:
- The cleanup workflow handles post-merge cleanup automatically.
- For stranded branches (no associated PR), use the GitHub UI's branch delete or:
  ```bash
  curl -X DELETE -H "Authorization: token $SYNC_TOKEN" \
    https://api.github.com/repos/emmanuel-a-otchere/AmamooIntelligence/git/refs/heads/upstream-sync/<sha>
  ```

### 21.4 Token rotation

If `SYNC_TOKEN` expires or loses scope:
1. Generate a new PAT at https://github.com/settings/tokens (needs `repo` + `workflow` scope).
2. Update the secret: `PUT /repos/emmanuel-a-otchere/AmamooIntelligence/actions/secrets/SYNC_TOKEN` with the new value (libsodium sealed-box encrypted).
3. The next sync run uses the new token automatically.

## 22. Monitoring & Observability

### 22.1 What to watch

| Signal | Where | What it tells you |
|---|---|---|
| Sync workflow runs | `Actions → Sync upstream` | Weekly health of the fork-upstream relationship |
| Sync PR age | GitHub notifications | If unmerged > 7 days, may need attention |
| Open PRs | `https://github.com/emmanuel-a-otchere/AmamooIntelligence/pulls` | Outstanding work |
| Branch count | `GET /repos/.../branches?per_page=100` | Should be ≤3 (`main`, `usecase/research-digest`, possibly one straggler) |
| Bot activity | `git log --author=upstream-sync-bot` | Sync cadence |
| Specialization tests | `pytest tests/` (manual or CI) | Specialization contract |

### 22.2 What there isn't

- No Prometheus metrics endpoint.
- No structured logs shipped to a central store.
- No alerting on sync failure (GitHub's default email notification is the only signal).
- No uptime monitoring for the specialization's RSS sources.

## 23. Future Work / Non-Goals

### 23.1 Planned for next minor versions

| Item | Target version | Notes |
|---|---|---|
| Promote `rss_fetch` upstream | 1.1.0 | `OVERLAY.md` calls for PR'ing `src/tools/rss.py` back to base once validated |
| Wire `_invoke_orchestrator` to a real orchestrator | 1.1.0 | Either upstream `OrchestratorAgent` or a deployer-provided alternative |
| Add tests for `ResearchDigestAgent.run()` and `should_run()` | 1.1.0 | Currently uncovered |
| Resolve docs-vs-code drift in `rss.py` (`require_https`, parallel fetch) | 1.1.0 | Either implement or correct docs |
| Fix path drift in specialization docs | 1.1.0 | `use-cases/research-digest/` → `specializations/research-digest/` |
| Add a worked example of branching (`git checkout -b specializations/<slug>`) | 1.1.0 | Currently only documented |
| Pin Docker base images and Actions to SHAs | 1.1.0 | Soft hardening |

### 23.2 Explicit non-goals

| Non-goal | Why |
|---|---|
| Real-time streaming briefings | Out of scope per `SPEC.md` |
| Personal email/calendar integration | Privacy + scope creep |
| Multi-language briefings | English-only for v1 per `SPEC.md` |
| Mobile app delivery | Out of scope per `SPEC.md` |
| Upstreaming the specialization to `open-jarvis/OpenJarvis` directly | The fork exists precisely so we don't have to wait for upstream acceptance |

---

# Appendix A — Source File Inventory

## A.1 Fork infrastructure files (on `main`)

| Path | Purpose | LoC (approx) |
|---|---|---|
| `.github/workflows/upstream-sync.yml` | Weekly sync workflow | 132 |
| `.github/workflows/cleanup-bot-branches.yml` | Post-merge bot-branch cleanup | 62 |
| `ATTRIBUTION.md` | Upstream credit | short |
| `HEALTH.md` | Known VM-side issues | short |
| `README.md` | Fork banner + identity header | medium |
| `docs/UPSTREAM-SYNC.md` | Sync playbook | medium |
| `docs/SPECIALIZING.md` | Specialization playbook | medium |
| `use-cases/README.md` | Specialization registry | short |
| `use-cases/_template/SPEC.md` | New specialization spec template | short |
| `use-cases/_template/README.md` | New specialization README template | short |
| `docs/REQUIREMENTS.md` | This document | long |

## A.2 Specialization files (on branch `usecase/research-digest`)

| Path | Purpose | LoC (approx) |
|---|---|---|
| `specializations/research-digest/OVERLAY.md` | Delta manifest | medium |
| `specializations/research-digest/README.md` | Specialization landing page | medium |
| `specializations/research-digest/SPEC.md` | Use-case specification | medium |
| `specializations/research-digest/configs/research-digest.toml` | Recipe (declarative orchestration) | 65 |
| `specializations/research-digest/conftest.py` | Root pytest conftest | short |
| `specializations/research-digest/docs/SOURCES.md` | Operator-facing source guide | medium |
| `specializations/research-digest/pyrightconfig.json` | Pyright config | short |
| `specializations/research-digest/pytest.ini` | Pytest config | short |
| `specializations/research-digest/src/__init__.py` | Package marker | 0 |
| `specializations/research-digest/src/agents/__init__.py` | Package marker | 0 |
| `specializations/research-digest/src/agents/research_digest.py` | Stateful scheduled agent | ~150 |
| `specializations/research-digest/src/tools/__init__.py` | Package marker | 0 |
| `specializations/research-digest/src/tools/rss.py` | RSS/Atom fetcher | ~150 |
| `specializations/research-digest/tests/conftest.py` | Tests conftest | short |
| `specializations/research-digest/tests/fixtures/sample_briefing.md` | Test fixture | short |
| `specializations/research-digest/tests/test_recipe_loads.py` | Recipe smoke test | 11 tests |
| `specializations/research-digest/tests/test_rss_fetch.py` | RSS fetcher robustness | 4 tests |
| `specializations/research-digest/tests/test_url_sanity.py` | URL hallucination check | 1 test |

**Total LoC added by specialization: ~600** (excluding tests and docs).

# Appendix B — Test Coverage Snapshot

## B.1 Live test run — 2026-06-28

```
$ cd ~/projects/AmamooIntelligence && git checkout usecase/research-digest
$ cd specializations/research-digest && uv run --no-sync pytest -v

collected 16 items

tests/test_recipe_loads.py::test_recipe_file_exists PASSED               [  6%]
tests/test_recipe_loads.py::test_recipe_parses PASSED                    [ 12%]
tests/test_recipe_loads.py::test_recipe_tools_are_known PASSED           [ 18%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[rss_fetch] PASSED [ 25%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[web_search] PASSED [ 31%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[http_request] PASSED [ 37%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[memory_store] PASSED [ 43%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[memory_search] PASSED [ 50%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[think] PASSED     [ 56%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[file_write] PASSED [ 62%]
tests/test_recipe_loads.py::test_each_tool_is_a_string[tts] PASSED       [ 68%]
tests/test_rss_fetch.py::test_parses_valid_rss PASSED                    [ 75%]
tests/test_rss_fetch.py::test_parses_atom PASSED                         [ 81%]
tests/test_rss_fetch.py::test_malformed_returns_empty PASSED             [ 87%]
tests/test_rss_fetch.py::test_fetch_failure_returns_empty PASSED         [ 93%]
tests/test_url_sanity.py::test_every_url_returns_2xx PASSED              [100%]

============================== 16 passed in 7.36s ==============================
```

**Result: 16/16 passing.**

## B.2 Coverage by file

| File | Tests | Status |
|---|---|---|
| `test_recipe_loads.py` | 11 (1 parametrized × 8) | All passing |
| `test_rss_fetch.py` | 4 | All passing |
| `test_url_sanity.py` | 1 (network marker) | Passing |

## B.3 Test gap analysis

| Component | Tested? | Reason |
|---|---|---|
| `RecipeTOML.load()` | ✅ | `test_recipe_parses` |
| `FeedItem` dataclass | ✅ | Implicitly via RSS tests |
| `rss.fetch_feed()` — happy path | ✅ | `test_parses_valid_rss`, `test_parses_atom` |
| `rss.fetch_feed()` — error paths | ✅ | `test_malformed_returns_empty`, `test_fetch_failure_returns_empty` |
| `rss._fetch()` — timeout/oversize | ❌ | No direct test |
| `rss._parse_dt()` — all formats | ❌ | Implicit via happy-path tests |
| `DigestRun.to_dict()` | ❌ | No test |
| `ResearchDigestAgent.__init__()` | ❌ | No test |
| `ResearchDigestAgent.should_run()` | ❌ | No test |
| `ResearchDigestAgent.run()` | ❌ | No test (and the stub means it wouldn't exercise real logic anyway) |
| `ResearchDigestAgent._invoke_orchestrator()` | ❌ | No test (and it's a stub) |
| State persistence (`_save_state`, `_load_state`) | ❌ | No test |

## B.4 What SPEC.md promises vs. what tests cover

| SPEC.md success criterion | Automated test? |
|---|---|
| Briefing delivered every weekday morning at 07:00 | ❌ — requires scheduler wiring |
| Cites ≥ 3 sources per theme | ❌ — requires orchestrator |
| Cites at least one arXiv paper per science briefing | ❌ — requires orchestrator |
| Total runtime ≤ 10 minutes | ❌ — requires orchestrator |
| Audio version under 8 minutes | ❌ — requires orchestrator + TTS |
| No fabricated URLs | ✅ — `test_url_sanity.py` |

**Net: 1 of 6 success criteria is covered by automated tests.**

# Appendix C — Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-06-28 | `@emmanuel-a-otchere` | Initial document. Covers the fork as it exists on `main` (HEAD `01432a7`) and the research-digest specialization on branch `usecase/research-digest` (HEAD `52fcd15`). |

### Change log conventions

- **MAJOR** version bump when scope, license, or architectural principles change incompatibly.
- **MINOR** version bump when new features, specializations, dependencies, or capabilities are added in a backward-compatible way.
- **PATCH** version bump for clarifications, typo fixes, version-number updates.

Each entry must reference the commit SHA(s) that introduced the change.

---

*End of document.*