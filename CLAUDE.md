## CLAUDE.md

Canonical governance lives in this repo's `AGENTS.md`. Do not duplicate it
here; keep only project-specific provider notes below.

- **Validation:** prefer `make` targets (`make lint` / `make typecheck` /
  `make test`).
- **Tools:** `ast-grep` (`sg`) for structural search; never `rm` / `sed -i`
  (use the Edit tool or `trash-put`).
