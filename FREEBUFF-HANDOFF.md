# FREEBUFF-HANDOFF.md

**Prepared for:** FreeBuff / GPT-5.6 Luna clean-sheet Dashboard experiment

---

## Repository

- **Repository:** andrewdhannah/urban-heat-intelligence
- **Remote:** https://github.com/andrewdhannah/urban-heat-intelligence.git
- **Source branch:** hackathon-expansion
- **Source/base SHA:** `3134f288cc10792c66fa7839d34f1abe63ba0206`
- **Challenger branch:** dashboard-luna-cleansheet
- **Working directory:** `/Users/andrew/Desktop/Freebuff/urban-heat-intelligence`
- **Working-tree status:** Clean

---

## Secrets Policy

No secrets were copied during workspace staging. The `.secrets/` directory, `.env`, `FORTYGUARD_API_KEY`, credentials, tokens, and local secret env files are absent from this checkout. The clean-sheet Dashboard does not require possession of a provider secret for design work.

If Live execution is later required, credentials must be supplied through the existing governed environment mechanism.

---

## Control Implementation

The existing `app/static/` directory contains the current production Dashboard implementation. This serves as the **control** against which Luna's clean-sheet work may be compared.

---

## Instructions for Luna

1. Follow the supplied clean-sheet Dashboard prompt exactly.
2. Do not modify `app/static/` — it is the control implementation.
3. Record the base SHA (`3134f288cc10792c66fa7839d34f1abe63ba0206`) before beginning work.
4. Create an isolated branch for your clean-sheet implementation.
5. Generate qualification evidence comparing your implementation against the control.
6. Do not commit to `main` or `hackathon-expansion`.
7. Do not expand scope beyond the Dashboard experiment.

---

## Verification

All required project content is present:

- `app/` (including `server.py`, `static/index.html`)
- `src/` (including `agent/controller.py`, `agent/brief.py`, `agent/adapter.py`, `agent/time_resolver.py`)
- `tests/` (including `test_s2_browser.py`)
- `fixtures/`
- `docs/`
- `qualification/`
- `project-state/`
- `README.md`
- `PROJECT-IDENTITY.md`
- `SESSION-HANDOFF.md`

Git is functional. The repository can create branches, commit, and generate diffs.
