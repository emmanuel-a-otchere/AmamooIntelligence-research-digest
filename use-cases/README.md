# Use Cases

AmamooIntelligence is a **general-purpose base**. Specialized variants for specific domains live in **separate repos** that fork from AmamooIntelligence. This folder is the starting point for scaffolding those specializations.

## Layout

```
use-cases/
├── _template/        # Copy this to scaffold a new specialization
│   ├── SPEC.md       # Fill in: goal, criteria, what stays/changes, sync strategy
│   └── README.md
└── <name>/           # (created per use case, after forking the repo)
    ├── SPEC.md
    ├── OVERLAY.md    # Every file the specialization changes on top of base
    └── tests/        # Use-case-specific tests
```

## Workflow

1. Fork `emmanuel-a-otchere/AmamooIntelligence` to `emmanuel-a-otchere/AmamooIntelligence-<usecase>`.
2. In the new repo, copy `_template/` → `<your-name>/` and fill it in.
3. Build your specialization as a focused layer on top of base.
4. Rebase (or merge) `base/main` weekly to pick up upstream fixes.
5. Promote generally-useful improvements back to AmamooIntelligence via PR.

Full details: [`docs/SPECIALIZING.md`](../docs/SPECIALIZING.md).

## Active specializations

| Repo | One-line summary |
| --- | --- |
| [`AmamooIntelligence-research-digest`](https://github.com/emmanuel-a-otchere/AmamooIntelligence-research-digest) | Scheduled multi-source research digest: gather → cluster → deep-research → synthesize → optional TTS |

When you create a specialized fork, add a row above with a one-line summary.