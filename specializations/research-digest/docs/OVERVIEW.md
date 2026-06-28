# research-digest — Specialization Overview

> **The operator's manual for the research-digest specialization.**
> Read [`SPEC.md`](SPEC.md) for the design intent, [`OVERLAY.md`](OVERLAY.md) for the file-by-file delta over AmamooIntelligence base, and the parent [`docs/REQUIREMENTS.md`](../../docs/REQUIREMENTS.md) for fork-level requirements.

| | |
|---|---|
| **Document version** | 1.0.0 |
| **Document date** | 2026-06-28 |
| **Specialization version** | 0.1.0 (recipe) |
| **Branch** | `usecase/research-digest` |
| **Maintainer** | `@emmanuel-a-otchere` |

---

## 1. What this specialization is

**research-digest** is a scheduled, multi-source research digest built on the [AmamooIntelligence](../../) personal-AI platform. It runs every weekday morning, fetches items from RSS/Atom feeds you configure, identifies themes worth deeper research, runs short deep-research passes on each theme, synthesizes the results into a single Markdown briefing, and optionally speaks it aloud.

It is the first worked example of the **specialization pattern** — a thin, declarative layer over the upstream framework that lets you build focused vertical use cases without forking the base platform. The pattern is documented in [`../../docs/SPECIALIZING.md`](../../docs/SPECIALIZING.md); this specialization is the canonical demonstration of that pattern.

### 1.1 What problem it solves

Most personal-AI platforms give you primitives — agents, tools, memory, workflows — but don't ship end-to-end "morning briefing" recipes. The upstream framework has a `morning_digest` agent (see `src/openjarvis/agents/morning_digest.py`) but it's a thin preset.

research-digest goes further: it composes a multi-stage workflow (gather → cluster → deep-research → sanity-check → synthesize → audio) using upstream's `deep-researcher` template, with explicit success criteria and a test suite.

### 1.2 What it produces

Every weekday morning at 07:00 local time (configurable), the system produces:

- **Markdown briefing** — `briefings/{date}.md` containing 2–4 themes, each with ≥3 real citations.
- **Audio briefing** (optional) — `briefings/{date}.mp3` using the configured TTS voice (default: Microsoft Edge TTS).
- **State sidecar** — `{state_dir}/research_digest_state.json` recording the run for idempotency and audit.

### 1.3 What it doesn't do

| Out of scope | Reason |
|---|---|
| Real-time streaming | Scheduled digests only |
| Personal email/calendar integration | That's upstream's `morning_digest` agent — use that instead |
| Multi-language briefings | English only for v1 |
| Mobile app delivery | Markdown + audio are the v1 surfaces |

---

## 2. Architecture

### 2.1 Three layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer A — Recipe (declarative orchestration)               │
│  configs/research-digest.toml                               │
│  • Defines schedule, sources, model, agent type, prompt     │
│  • Consumed by the upstream orchestrator agent               │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ loaded at runtime
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer B — State + lifecycle (this specialization)          │
│  src/agents/research_digest.py                              │
│  • ResearchDigestAgent — owns state, idempotency, lifecycle │
│  • DigestRun — the per-run record persisted to disk         │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ uses for I/O
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer C — RSS/Atom fetcher (this specialization)           │
│  src/tools/rss.py                                           │
│  • fetch_feed(url) → list[FeedItem]                         │
│  • Stdlib-only, fails soft, bounded size, 15s timeout       │
└─────────────────────────────────────────────────────────────┘
```

The **upstream orchestrator agent** (out of this specialization) drives the actual gather → cluster → deep-research → synthesize workflow using these three layers as building blocks.

### 2.2 Module responsibilities

| Module | Layer | Responsibility | Public API |
|---|---|---|---|
| `configs/research-digest.toml` | A | Declarative orchestration spec | (consumed by upstream orchestrator) |
| `src/agents/research_digest.py` | B | Owns lifecycle, idempotency, persistence | `DigestRun`, `ResearchDigestAgent` |
| `src/tools/rss.py` | C | RSS/Atom fetching and parsing | `FeedItem`, `fetch_feed` |
| `tests/test_recipe_loads.py` | — | Smoke tests the recipe | 11 tests |
| `tests/test_rss_fetch.py` | — | Fetcher robustness | 4 tests |
| `tests/test_url_sanity.py` | — | URL hallucination detection (network marker) | 1 test |

### 2.3 Reused unchanged from upstream

- `src/openjarvis/templates/data/deep-researcher.toml` — used as the deep-research agent template.
- `src/openjarvis/tools/tts.py` — used for the optional audio briefing.
- `src/openjarvis/tools/web_search.py`, `http_request.py` — used by the gather and citation steps.
- All of `src/openjarvis/core/` — the agent loop is reused as-is.

---

## 3. Configuration schema

The recipe is a single TOML file: `configs/research-digest.toml`.

### 3.1 Full schema (verified at commit `52fcd15`)

```toml
[recipe]
name        = "research_digest"          # slug; must match directory name
description = "..."                       # human-readable
version     = "0.1.0"                     # semver
parent_template = "deep-researcher"       # upstream template this extends

[intelligence]
model = "qwen3:8b"                        # model identifier for the inference engine

[engine]
key  = "ollama"                           # inference engine key (resolved by upstream)

[schedule]
cron     = "0 7 * * 1-5"                  # Vixie cron (5 fields)
timezone = "local"                        # "local" or IANA tz (e.g. "America/New_York")

[gather]
sources             = [...]               # list of feed URLs (HTTPS recommended)
max_items_per_source = 25                 # cap items pulled per source

[cluster]
agent_template = "deep-researcher"        # upstream template
max_themes      = 4                       # cap themes to identify

[deep_research]
agent_template        = "deep-researcher"
max_turns_per_theme   = 8
min_citations_per_theme = 3

[synthesize]
output_path    = "briefings/{date}.md"    # {date} substituted at run time
agent_template = "deep-researcher"

[audio]
enabled        = true
voice_provider = "edge"                   # upstream TTS provider
max_minutes    = 8
output_path    = "briefings/{date}.mp3"

[agent]
type          = "orchestrator"            # upstream agent type
max_turns     = 60
temperature   = 0.4
tools         = [...]                     # list of tool identifiers
system_prompt = """..."""                 # multi-line
```

### 3.2 Recipe tools referenced (8 total)

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

### 3.3 Default source bundle

```toml
[gather]
sources = [
  "https://news.ycombinator.com/rss",
  "https://arxiv.org/rss/cs.AI",
  "https://arxiv.org/rss/cs.CL",
  "https://www.technologyreview.com/feed/",
]
```

### 3.4 Suggested source bundles (from `docs/SOURCES.md`)

| Bundle | Feeds |
|---|---|
| **AI / ML** | `arxiv.org/rss/cs.AI`, `arxiv.org/rss/cs.CL`, `arxiv.org/rss/cs.LG`, `huggingface.co/blog/feed.xml` |
| **Tech news** | `news.ycombinator.com/rss`, `technologyreview.com/feed/`, `feeds.arstechnica.com/arstechnica/index` |
| **Security** | `schneier.com/feed/atom/`, `krebsonsecurity.com/feed/`, `feeds.feedburner.com/TheHackersNews` |
| **Science** | `nature.com/nature.rss`, `sciencemag.org/rss/news_current.xml`, `arxiv.org/rss/` |

---

## 4. Runtime behavior

### 4.1 What happens at 07:00 on a weekday

```
1.  Trigger (cron, systemd timer, or `jarvis run --recipe ... --once`)
        │
        ▼
2.  Load recipe (configs/research-digest.toml)
        │
        ▼
3.  Construct ResearchDigestAgent(recipe_path, state_dir)
        │
        ▼
4.  should_run(now)? — idempotency check
        │ (returns false if last finished_at was today)
        ▼
5.  run(now)
        │
        ├── _invoke_orchestrator(run)   ← STUB (deployer wires this)
        │       │
        │       ▼
        │   [Orchestrator follows recipe's system prompt:]
        │       GATHER → CLUSTER → DEEP-RESEARCH → SANITY-CHECK → SYNTHESIZE → AUDIO
        │       (see § 4.2 for what this should do)
        │
        ▼
6.  _save_state(run) — write {state_dir}/research_digest_state.json
        │
        ▼
7.  Return run record (caller can inspect themes, citations, errors)
```

### 4.2 What the orchestrator is expected to do

Per the recipe's `[agent].system_prompt`, the orchestrator must run a six-step workflow. The specialization ships the **contract** but the **implementation** is delegated to the upstream orchestrator agent.

#### Step 1: GATHER

For each URL in `gather.sources`:
- Call `fetch_feed(url)` (from `src/tools/rss.py`).
- Receive a flat list of `FeedItem` (title, link, published, summary, source).
- Truncate to `gather.max_items_per_source` (default 25) per source.

#### Step 2: CLUSTER

Across all gathered items, identify 2–4 recurring themes. Use the upstream `deep-researcher` template as the reasoning engine. Cap at `cluster.max_themes` (default 4).

#### Step 3: DEEP-RESEARCH

For each theme:
- Run a focused deep-research pass using `deep-researcher` template.
- Cap at `deep_research.max_turns_per_theme` (default 8) turns.
- Require ≥`deep_research.min_citations_per_theme` (default 3) real citations.

#### Step 4: SANITY-CHECK

Before writing, verify every URL the synthesizer will reference returns 2xx. If any don't:
- Drop them and replace with `web_search` results, OR
- Remove the affected sentence and re-synthesize, OR
- Record the failure in the briefing as "[source unavailable]".

This step mirrors `tests/test_url_sanity.py` — same URL regex, same HEAD-with-fallback strategy.

#### Step 5: SYNTHESIZE

Combine all theme briefs into a single Markdown briefing at `synthesize.output_path` (substituting `{date}` for today's date in `YYYY-MM-DD`).

Example structure:

```markdown
# Research Digest — 2026-06-28

## Theme 1: {theme name}
{2-3 paragraphs summarizing the theme}

Sources:
- [{source title}]({url})
- [{source title}]({url})
- [{source title}]({url})

## Theme 2: {theme name}
...

---
*Generated by research-digest v0.1.0. Runtime: {minutes} min. Citations: {n}.*
```

#### Step 6: AUDIO (optional)

If `audio.enabled = true`:
- Call upstream `tts` tool with the synthesized briefing text.
- Cap audio length at `audio.max_minutes` (default 8) minutes.
- Write to `audio.output_path` (substituting `{date}`).

### 4.3 Idempotency

`should_run(now)` returns `False` if the last `finished_at` is the same calendar day as `now`. This means:

- A double-triggered cron doesn't run twice in one day.
- A manual `jarvis run --once` invocation is a no-op if today's digest already ran.
- The state sidecar is the single source of truth — no clock drift, no flag files.

Day granularity means a run that started at 23:59 yesterday and finished at 00:01 today would not re-run today. This is intentional — it matches the "one briefing per day" mental model.

### 4.4 Failure semantics

| Failure | What happens |
|---|---|
| Per-source fetch failure (4xx, 5xx, timeout, oversize) | Logged at WARN, source is skipped, other sources continue |
| Per-item parse failure (malformed XML, missing link, bad date) | Logged at WARN, item is skipped, other items continue |
| Orchestrator exception | Caught at `agent.run()`, logged, `str(exc)` stored in `run.errors`, state is still saved, `DigestRun` returned |
| State-load corruption (JSON decode error, missing key) | Caught, logged at WARN, treated as fresh state |
| State-save failure | Not caught — will raise (state persistence is essential) |
| TTS failure | Not handled at this layer — upstream `tts` tool's behavior |

---

## 5. Operator controls

### 5.1 Change the source list

Edit `configs/research-digest.toml` → `[gather].sources`. See § 3.4 for suggested bundles. After editing, restart any running scheduler.

### 5.2 Change the schedule

Edit `[schedule].cron` and `[schedule].timezone`. The recipe defaults to `0 7 * * 1-5` (weekdays at 07:00 local). Examples:

| Cron | Meaning |
|---|---|
| `0 7 * * 1-5` | Weekdays at 07:00 (default) |
| `0 8 * * *` | Daily at 08:00 |
| `*/30 9-17 * * 1-5` | Every 30 min during business hours, weekdays |
| `0 6 * * 0` | Sundays at 06:00 (weekly recap) |

The `[schedule].timezone` accepts `"local"` (system local time) or an IANA name like `"America/New_York"`.

### 5.3 Swap the LLM

Edit `[intelligence].model`. The recipe defaults to `qwen3:8b` running via Ollama (`[engine].key = "ollama"`). To use a different model:

```bash
# Pull the new model in Ollama
ollama pull llama3.1:8b

# Update the recipe
# [intelligence]
# model = "llama3.1:8b"
```

### 5.4 Swap the inference engine

Edit `[engine].key`. The specialization has been tested with `ollama` only. Upstream supports other engines (`vllm`, `mlx`, `anthropic`, `openai`, `google-genai`, etc.) — change the key and ensure the corresponding environment variables are set.

### 5.5 Disable audio

Set `[audio].enabled = false`. This skips the TTS step entirely.

### 5.6 Change the audio voice

Edit `[audio].voice_provider`. Currently supports `"edge"` (Microsoft Edge TTS). Other providers may be available via upstream — see upstream TTS tool docs.

### 5.7 Customize the orchestrator prompt

Edit `[agent].system_prompt`. This is a multi-line TOML string. Useful changes:

- **Tone** — change "Distinguish established facts from speculation" → "Be concise; prioritize actionable insights".
- **Citation rules** — add "Every theme must cite at least one arXiv paper".
- **Output format** — change the briefing structure (add sections, change ordering).

### 5.8 Override via environment variables

The upstream framework supports environment-variable overrides for many config keys. See upstream config docs for the exact naming convention. As of v0.1.0 of this specialization, the recipe itself doesn't declare env-var overrides.

---

## 6. Output structure

### 6.1 File layout per deployment

```
{deployment_root}/
├── configs/
│   └── research-digest.toml             # recipe
├── briefings/
│   ├── 2026-06-23.md                    # generated Markdown briefing
│   ├── 2026-06-23.mp3                   # generated audio (if enabled)
│   ├── 2026-06-24.md
│   ├── 2026-06-24.mp3
│   └── ...
└── {state_dir}/
    └── research_digest_state.json       # last-run record (overwritten)
```

### 6.2 State sidecar — `research_digest_state.json`

```json
{
  "started_at": "2026-06-28T07:00:00-04:00",
  "finished_at": "2026-06-28T07:08:42-04:00",
  "themes": ["theme 1", "theme 2", "theme 3"],
  "citations_total": 12,
  "output_markdown": "briefings/2026-06-28.md",
  "output_audio": "briefings/2026-06-28.mp3",
  "errors": []
}
```

Persistence rules:
- One file per `state_dir`, overwritten on each run.
- Write happens even on orchestrator failure (errors are captured in `errors[]`).
- State-load is fault-tolerant — corrupted state is logged and treated as fresh.

### 6.3 Markdown briefing format

The synthesizer (upstream orchestrator) is responsible for the format. The recommended structure (used by `tests/fixtures/sample_briefing.md`) is:

```markdown
# Research Digest — {YYYY-MM-DD}

## Theme 1: {theme name}
{summary}

Sources:
- [{title}]({url})
- [{title}]({url})

## Theme 2: {theme name}
...

---
*Generated by research-digest v0.1.0. Runtime: {n} min. Citations: {n}.*
```

---

## 7. Testing

### 7.1 Live test run

```
$ cd specializations/research-digest
$ uv run --no-sync pytest -v

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

### 7.2 What the tests assert

| File | Tests | What they assert |
|---|---|---|
| `test_recipe_loads.py` | 11 | Recipe file exists; recipe parses; recipe.name == "research_digest"; schedule.cron == "0 7 * * 1-5"; gather.sources is a non-empty list; all tools referenced are in the known prefix set; each of the 8 known tools appears in `agent.tools` |
| `test_rss_fetch.py` | 4 | Valid RSS parses with correct fields, missing `<link>` items are dropped, garbage dates become `None`; valid Atom parses correctly; malformed XML returns `[]`; network failure returns `[]` |
| `test_url_sanity.py` | 1 | Every URL in `tests/fixtures/sample_briefing.md` returns 2xx via HEAD request (network marker — skipped in offline CI) |

### 7.3 Running tests

```bash
# All tests
uv run --no-sync pytest -v

# Skip the network test (offline CI)
uv run --no-sync pytest -v -m "not network"

# Just the recipe tests
uv run --no-sync pytest tests/test_recipe_loads.py -v

# Just the fetcher tests
uv run --no-sync pytest tests/test_rss_fetch.py -v
```

### 7.4 Test gap analysis

The following components are **not yet covered** by automated tests:

| Component | Tested? | Why it's a gap |
|---|---|---|
| `DigestRun.to_dict()` | ❌ | No test |
| `ResearchDigestAgent.__init__()` | ❌ | No test |
| `ResearchDigestAgent.should_run()` | ❌ | Critical for idempotency — needs tests |
| `ResearchDigestAgent.run()` | ❌ | Critical for the daily pipeline — needs tests |
| `ResearchDigestAgent._invoke_orchestrator()` | ❌ | Stub; test will need a mock orchestrator |
| State persistence (`_save_state`, `_load_state`) | ❌ | Critical for resilience — needs tests |
| Configuration TOML schema validation (max_themes, cron format, etc.) | Partial | `test_recipe_parses` checks 3 keys, not all |

These gaps are tracked in `docs/REQUIREMENTS.md` § 20.1 and § 23.1 (planned for v1.1.0).

---

## 8. Extension points

These are the changes you can make **without breaking the contract** that other specializations or downstream forks depend on.

### 8.1 Safe to change (data only)

| Change | Where | Effect |
|---|---|---|
| Add/remove/reorder sources | `[gather].sources` | More or fewer themes, different mix |
| Change the cron | `[schedule].cron` | Different schedule |
| Change the model | `[intelligence].model` | Different LLM behavior |
| Change audio provider | `[audio].voice_provider` | Different voice |
| Customize the prompt | `[agent].system_prompt` | Different briefing style |
| Disable audio | `[audio].enabled = false` | Skip TTS |
| Change max themes | `[cluster].max_themes` | More or fewer themes |
| Change min citations | `[deep_research].min_citations_per_theme` | Stricter or looser citation rule |

### 8.2 Safe to change (small code changes)

| Change | Where | Effect |
|---|---|---|
| Add a new tool to the recipe | `src/tools/<new>.py` + `[agent].tools` | New capability in the orchestrator |
| Change `_parse_dt` to support more formats | `src/tools/rss.py` | Better date handling for weird feeds |
| Change `_MAX_BYTES` to allow larger feeds | `src/tools/rss.py` | Lifted cap (use with caution) |
| Add a sanity-checker for citations | `src/agents/research_digest.py` | Stronger URL validation |
| Add structured logging | anywhere | Better observability |
| Override `_invoke_orchestrator()` in a subclass | `src/agents/research_digest.py` | Plug in a different orchestrator |

### 8.3 NOT safe to change (breaks contract)

| Change | Why |
|---|---|
| Remove `DigestRun` fields | Breaks `to_dict()` shape and any external consumer that reads `research_digest_state.json` |
| Change `FeedItem` fields | Breaks the rss_fetch tool contract |
| Rename the tool from `rss_fetch` to something else | Breaks the recipe (`test_recipe_loads` will fail) |
| Move files out of `src/tools/` or `src/agents/` | Breaks `conftest.py` `sys.path` injection |
| Rename `ResearchDigestAgent` | Breaks any external instantiation |

---

## 9. Failure modes and recovery

### 9.1 Common operational issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Briefing doesn't run at scheduled time | Cron/timer not installed | See § 10 — install scheduler |
| Briefing runs but themes are empty | Orchestrator stubbed (current state) | Implement `_invoke_orchestrator()` |
| Briefing runs but URLs are 404 | Source changed | Update `[gather].sources` |
| Briefing runs but very slow (>10 min) | Too many sources, slow model | Reduce `gather.sources`, switch to faster model |
| Audio file is empty or missing | TTS provider failed | Check upstream `tts` tool config; check voice_provider |
| `research_digest_state.json` is corrupted | Disk failure mid-write | Delete file — next run will start fresh |
| All feeds fail with timeout | Network issue | Check upstream connectivity; check Ollama is running |

### 9.2 Recovery procedures

**Re-run today's briefing:**

```python
# Force a re-run by clearing the state's finished_at:
# (Edit research_digest_state.json, set "finished_at" to null, save.)
# Next invocation of ResearchDigestAgent.run() will proceed.
```

**Run a specific date manually:**

```bash
# Modify the recipe's output_path template to include a date suffix,
# or pass an explicit date to the orchestrator (if your deployment supports it).
```

**Reset to a clean state:**

```bash
# Remove the state sidecar
rm {state_dir}/research_digest_state.json
```

---

## 10. Deployment checklist

A production deployment requires:

- [ ] **Ollama installed** with `qwen3:8b` (or your preferred model) pulled
- [ ] **uv installed** and `uv sync` run from the repo root
- [ ] **The specialization's deps available** (pytest, etc. for tests; the recipe is consumed by the upstream orchestrator at runtime)
- [ ] **The orchestrator wired** — `ResearchDigestAgent._invoke_orchestrator()` overridden to call upstream's `OrchestratorAgent` (or your alternative)
- [ ] **A scheduler** — systemd timer / launchd plist / cron / upstream `jarvis scheduler start` — that calls `jarvis run --recipe configs/research-digest.toml --once` on the configured schedule
- [ ] **State directory writable** — wherever you point `state_dir`, the process must be able to create `research_digest_state.json`
- [ ] **Output directory writable** — wherever `synthesize.output_path` resolves to, the process must be able to write `{date}.md`
- [ ] **Sources reachable** — from the deployment host, every URL in `[gather].sources` must be fetchable
- [ ] **TTS reachable** (if audio enabled) — Edge TTS endpoint must be reachable from the deployment host

---

## 11. File reference

| Path | LoC | Purpose |
|---|---|---|
| `OVERVIEW.md` (this file) | — | Operator's manual |
| `README.md` | 43 | Quick start + layout |
| `SPEC.md` | 69 | Use-case design + success criteria |
| `OVERLAY.md` | 45 | File-by-file delta over base |
| `configs/research-digest.toml` | 74 | Recipe definition |
| `src/agents/research_digest.py` | 119 | Stateful scheduled agent |
| `src/tools/rss.py` | 151 | RSS/Atom fetcher |
| `tests/test_recipe_loads.py` | 50 | Recipe smoke test (11 invocations) |
| `tests/test_rss_fetch.py` | 81 | Fetcher robustness (4 tests) |
| `tests/test_url_sanity.py` | 51 | URL hallucination check (1 test, network marker) |
| `tests/conftest.py` | 8 | Test path injection |
| `conftest.py` | 9 | Root path injection |
| `pytest.ini` | 4 | Pytest config |
| `pyrightconfig.json` | 4 | Pyright config |
| `docs/SOURCES.md` | 44 | Per-deployment source list docs |
| `tests/fixtures/sample_briefing.md` | 16 | Sample briefing for URL sanity test |

**Total LoC (this specialization):** ~715

---

## 12. What's next

This specialization is currently a **pattern demo** — the orchestrator handoff is a stub. See `docs/REQUIREMENTS.md` § 20.1 for the limitation.

**To productionize**, the next tasks (tracked separately) are:

1. Wire `_invoke_orchestrator()` to upstream's `OrchestratorAgent`.
2. Ship a scheduler config (systemd timer, launchd plist, or shell wrapper).
3. Add tests for `should_run()`, `run()`, and `_invoke_orchestrator()` (with a mock).
4. Resolve the docs-vs-code drift in `rss.py` (`require_https`, parallel fetch).
5. Fix the path drift in `README.md`, `SPEC.md`, `OVERLAY.md` (currently reference `use-cases/research-digest/` but the actual tree is at `specializations/research-digest/`).

Once those are done, the specialization will be a fully runnable end-to-end pipeline.

---

*End of document.*