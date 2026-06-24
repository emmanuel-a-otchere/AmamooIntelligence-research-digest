# Upstream Sync Procedure

AmamooIntelligence tracks [`open-jarvis/OpenJarvis`](https://github.com/open-jarvis/OpenJarvis). This document is the playbook for keeping the fork in sync without breaking downstream specializations.

## Cadence

- **Weekly** minimum: `git fetch upstream && git merge upstream/main` (or rebase, if you prefer linear history).
- **Immediately** for any tagged release on upstream: `git fetch upstream --tags && git merge <tag>`.
- **Security-relevant** upstream commits: sync same day.

## Standard sync

```bash
# 1. Make sure your main is clean
git checkout main
git status    # should be clean

# 2. Fetch upstream
git fetch upstream

# 3. Merge (or rebase) upstream/main into your main
git merge upstream/main          # produces a merge commit; safe for forks with downstream consumers
# OR
git rebase upstream/main         # linear history; use only if no downstream forks have committed on top of your main

# 4. Resolve any conflicts (rare — AmamooIntelligence adds few files on top of upstream)

# 5. Run the test suite
uv run pytest tests/             # or: pytest tests/

# 6. Push
git push origin main
```

## What to merge without review

- Upstream patches to files AmamooIntelligence does **not** modify (i.e., anything under `src/openjarvis/core/`, `desktop/`, `frontend/`, etc., outside the use-cases scaffold). These cannot conflict.

## What needs a careful look

- Upstream changes to `configs/openjarvis/` — confirm new presets do not overlap with future specialization plans.
- Upstream changes to `pyproject.toml` / `uv.lock` — accept upstream's lockfile unless you have an unmerged local dep change.
- Upstream changes to `docs/` — accept, then re-apply any AmamooIntelligence-specific docs (`SPECIALIZING.md`, `UPSTREAM-SYNC.md`).

## Specializations tracking this repo

When you push a sync commit that changes behavior, notify downstream specialization owners:

| Specialization | Owner | Notify via |
| --- | --- | --- |
| _(none yet)_ | _(add when created)_ | _(e.g., GitHub issue, Discord, email)_ |

Downstream forks pull from AmamooIntelligence `main`, not from upstream, so this sync is the contract.

## Conflict resolution principles

If upstream changes a file AmamooIntelligence also touched (currently only `docs/SPECIALIZING.md`, `docs/UPSTREAM-SYNC.md`, and `use-cases/`):

1. Keep AmamooIntelligence-specific intent (this fork exists to be a specialization base).
2. If upstream adds new functionality relevant to specialization, port it in.
3. Document any deviation in the merge commit body so downstream consumers know what changed.