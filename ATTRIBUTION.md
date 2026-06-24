# Attribution

This project, **AmamooIntelligence**, is a fork of [**OpenJarvis**](https://github.com/open-jarvis/OpenJarvis).

## Original work

- **Project:** OpenJarvis — *Personal AI, On Personal Devices*
- **Upstream repository:** <https://github.com/open-jarvis/OpenJarvis>
- **Organization:** OpenJarvis Project (<https://github.com/open-jarvis>)
- **Maintainers:** Jon Saad-Falcon and the OpenJarvis contributors — see the [contributors graph](https://github.com/open-jarvis/OpenJarvis/graphs/contributors)
- **License:** [Apache License 2.0](https://github.com/open-jarvis/OpenJarvis/blob/main/LICENSE)
- **Original description:** A composable, programmable framework for on-device, personal AI, built around shared primitives, evaluations that treat energy/FLOPs/latency/cost as first-class constraints, and a local learning loop.

We are grateful to the OpenJarvis team and contributors for releasing their work under Apache 2.0 and for the research and engineering investment that made this fork possible.

## What this fork adds

AmamooIntelligence tracks upstream `open-jarvis/OpenJarvis` and serves as the **general-purpose base** for specialized forks aimed at specific use cases. The fork layer consists only of:

- `docs/SPECIALIZING.md` — how to fork and maintain a specialization.
- `docs/UPSTREAM-SYNC.md` — playbook for weekly merges from upstream.
- `use-cases/` — scaffold for new use-case specializations.
- `.github/workflows/upstream-sync.yml` — automated weekly upstream sync.
- A banner in `README.md` identifying this repo as a fork.

No upstream source code is modified by this fork's own commits.

## License

AmamooIntelligence is distributed under the **Apache License 2.0**, the same license as the upstream project. The full license text is in [`LICENSE`](LICENSE) and is inherited from the upstream OpenJarvis project.

Per the Apache 2.0 terms:

- You may use, modify, and distribute this software.
- You must include the copyright notice and license in any copy you distribute.
- You must indicate any changes you make.
- You may not use the names of the upstream contributors to endorse derivative products without permission.

## How to credit upstream

If you fork or build on AmamooIntelligence, please preserve the chain of attribution:

1. Keep this `ATTRIBUTION.md` in your fork (or an equivalent notice crediting OpenJarvis).
2. Link back to <https://github.com/open-jarvis/OpenJarvis> in your README.
3. If your fork specializes AmamooIntelligence for a specific use case, mention that in your repo description and link to <https://github.com/emmanuel-a-otchere/AmamooIntelligence> as the base.

## Contact

- **AmamooIntelligence maintainer:** [@emmanuel-a-otchere](https://github.com/emmanuel-a-otchere)
- **Upstream OpenJarvis:** [jonsaadfalcon@gmail.com](mailto:jonsaadfalcon@gmail.com) or the [OpenJarvis Discord](https://discord.gg/wfXEkpPX)