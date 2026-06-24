# Specializing AmamooIntelligence

> **AmamooIntelligence is the general-purpose base.** It tracks `upstream/open-jarvis/OpenJarvis` and ships every release unfiltered. Specialized variants live in **separate repos** that fork from AmamooIntelligence and add a single, focused layer on top.

## Why this model

A single fork trying to serve many use cases degrades into a swiss-army knife — every merge conflict, every dependency tradeoff is multiplied. Instead:

| Repo | Role | Lifetime |
| --- | --- | --- |
| `open-jarvis/OpenJarvis` | Upstream source of truth | Maintained by the OpenJarvis team |
| **`emmanuel-a-otchere/AmamooIntelligence`** | **Your general-purpose base. Tracks upstream. Adds no use-case logic.** | **Permanent.** Synced weekly via `git fetch upstream && git merge upstream/main`. |
| `emmanuel-a-otchere/AmamooIntelligence-<usecase>` | Specialized variant. Forks AmamooIntelligence. Adds one focused layer. | Created per use case. Rebased onto AmamooIntelligence `main` to pick up upstream fixes. |

## When to make a specialized fork

Create a new fork when the change you need is:

- **Domain-specific** (e.g., trading desk, clinical assistant, factory floor ops) — affects prompts, tools, models, and tests together.
- **Long-lived enough** to justify its own repo and CI.
- **Independent** of other specializations — a fix in `AmamooIntelligence-trading` should not require changes in `AmamooIntelligence-clinical`.

Do **not** create a specialized fork for:

- A single config tweak → put it in `configs/openjarvis/` and ship in AmamooIntelligence.
- A new tool or skill → add it to `src/openjarvis/tools/` and ship in AmamooIntelligence.
- A bug fix or upstream patch → PR it back to AmamooIntelligence so everyone benefits.

## Creating a specialized fork

### 1. Fork on GitHub
Use the GitHub UI or the API:

```bash
# Requires GITHUB_TOKEN with repo scope
curl -X POST https://api.github.com/repos/emmanuel-a-otchere/AmamooIntelligence/forks \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"name":"AmamooIntelligence-<usecase>"}'
```

Pick a short, kebab-case suffix: `AmamooIntelligence-trading`, `AmamooIntelligence-clinical-notes`, `AmamooIntelligence-home-ops`.

### 2. Clone locally and add the right remotes

```bash
git clone https://github.com/emmanuel-a-otchere/AmamooIntelligence-<usecase>.git
cd AmamooIntelligence-<usecase>

# base = AmamooIntelligence (you specialize on top of this)
git remote rename origin base

# upstream = the OpenJarvis source (for full visibility; optional)
git remote add upstream https://github.com/open-jarvis/OpenJarvis.git

# your working fork (where you push)
git remote add origin https://github.com/emmanuel-a-otchere/AmamooIntelligence-<usecase>.git
```

### 3. Use the scaffold

Copy `use-cases/_template/` to `use-cases/<your-name>/`:

```bash
cp -r use-cases/_template use-cases/<your-name>
```

Edit the `SPEC.md` inside to describe the use case: goal, success criteria, what stays general, what changes. Then commit:

```bash
git add use-cases/<your-name>
git commit -m "feat(usecase): scaffold <your-name>"
git push origin main
```

### 4. Make the specialization layer visible

Specialized forks should make their delta obvious. Recommended:

- A **branch per use case** (`usecase/<name>`) so rebases onto base are clean.
- A `use-cases/<name>/OVERLAY.md` listing every file your fork modifies or adds on top of base, with one-line rationale per file. This is what you diff against `base/main` to produce a release note.
- CI that runs both the base test suite and your use-case tests on every PR.

## Keeping a specialization in sync with base

AmamooIntelligence tracks upstream weekly. Your specialization should rebase (or merge) base regularly:

```bash
git fetch base
git rebase base/main            # if you keep your work as commits on top of base
# OR
git merge base/main             # if you keep your work as a long-lived branch
```

Rebase keeps history linear and makes the OVERLAY diff trivial. Merge keeps things simple if you publish a stable branch per release. Pick one and document it in your use-case `SPEC.md`.

## Promoting a specialization change back to base

If your specialization develops a fix or feature that is generally useful:

1. Open a PR from your use-case branch into `base/main` (i.e., `AmamooIntelligence`).
2. Title it `feat(<area>): [from <usecase>] <description>` so reviewers know the origin.
3. Once merged into AmamooIntelligence, rebase your specialization — the change will arrive automatically.

This keeps AmamooIntelligence as the convergence point: useful improvements made in any specialization can flow back to everyone.

## FAQ

**Q: Can a single use case span multiple forks?**
A: Yes. If `<usecase>` outgrows one repo (e.g., it needs a separate frontend), fork the specialization into `<usecase>-<component>` and depend on it via submodule or separate deployment.

**Q: What if AmamooIntelligence and a specialization diverge on the same file?**
A: Rebases will surface the conflict. Resolve in favor of the specialization's intent and document the rationale in `OVERLAY.md`.

**Q: Can I publish a specialized fork under a non-`AmamooIntelligence-*` name?**
A: Yes — the naming convention is a suggestion, not a rule. The important property is that the repo's README states clearly that it is a specialization of AmamooIntelligence and links back.