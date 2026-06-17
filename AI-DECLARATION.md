---
version: "0.1.2"
level: copilot
processes:
  design: none
  implementation: copilot
  testing: auto
  documentation: pair
  review: pair
  deployment: assist
components:
  OrecchietTetris/audio/: auto
  OrecchietTetris/leaderboard/: auto
  OrecchietTetris/model/: pair
  OrecchietTetris/view/: copilot
  tests/: auto
  CLAUDE.md: auto
  AGENTS.md: auto
  README.md: pair
---

## Notes

This project was developed using **Claude Code** (Anthropic) as an AI coding assistant.

**Design (`none`):** All architectural decisions — Observer pattern, interface-first design, import hierarchy, Model-View separation, Singleton pattern — were made independently by the human developer.

**Implementation (`copilot`):** The AI handled whole implementation tasks on request, with the human reviewing and approving each step. The Kivy view layer (`OrecchietTetris/view/`: `copilot`) was largely AI-driven; the model layer (`OrecchietTetris/model/`: `pair`) was developed more collaboratively with the human retaining stronger authorship. Audio and leaderboard subsystems (`OrecchietTetris/audio/`, `OrecchietTetris/leaderboard/`: `auto`) were generated autonomously by the AI, based on detailed instruction given by the human developer.

**Testing (`auto`):** The test suite (`tests/`: `auto`) was generated autonomously by the AI based on the implemented behaviour, following test-driven development approach.

**Documentation (`pair`):** `README.md` and inline documentation were written collaboratively. `CLAUDE.md` and `AGENTS.md` were generated autonomously by the AI (`auto`) based on codebase inspection.

**Review (`pair`):** Code review was conducted jointly — the AI flagged type errors, linting issues, and architectural inconsistencies; the human evaluated and acted on findings.

**Deployment (`assist`):** CI/CD pipeline configuration (semantic-release, commitlint, pre-commit hooks, Poetry packaging, PyPI publish) was set up with AI guidance; the human configured and owns the pipeline.

---

This declaration follows the [AI-DECLARATION.md](https://ai-declaration.md) standard v0.1.2.
