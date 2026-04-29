---
project: IdentityTypesAndAuth
repo: https://github.com/FrederikLeed/IdentityTypesAndAuth
updated: 2026-04-29
status: active
---

# Identity Types & Authentication

Bilingual (English / Danish) reference for choosing identity types and authentication mechanisms across Microsoft Entra ID and on-premises Active Directory. Aimed at IT-security teams making identity-design decisions.

## Outputs

Three formats from one source:

- **Web site** — <https://frederikleed.github.io/IdentityTypesAndAuth/> — MkDocs Material, EN + DA, searchable, mermaid renders live
- **Full PDF** — `release/identity-types(.da).pdf` — full reference with per-category sub-trees inline (no unified tree — too dense for print)
- **One-page handout** — `release/identity-types-handout(.da).pdf` — lookup table + forced-choice controls; printable for operators

CI builds the site on every push to main, builds PDFs on every release tag.

## What's covered

15 identity types ranked by security posture:

- Managed Identity (system / user-assigned)
- Workload Identity Federation
- Cloud-only / Hybrid users (passwordless or password+MFA)
- gMSA / dMSA / sMSA / Standard AD service accounts
- App Registrations (cert / secret / federated)
- Entra Joined / Hybrid Joined / Registered devices
- Guest / B2B / B2C identities

Each type gets: auth mechanisms, resource access, validation/protection guidance, pros, cons.

Plus mandatory hardening tables for the four forced-choice cases (App Reg + Client Secret, Standard AD SA, Cloud-only user with password+MFA, Hybrid Entra Joined Device).

## Architecture decisions

- **Source format:** Markdown in `docs/` with `.md` (EN) and `.da.md` (DA) sibling pairs — lets MkDocs i18n suffix mode handle language switching cleanly.
- **Diagrams:** Mermaid is editable source. PNG renders are committed for the PDF pipeline (which doesn't pre-process mermaid). Sub-trees are split into Workload / Human / Device — the unified tree is too dense for print but works on the web where users can zoom.
- **PDF engine:** weasyprint (HTML/CSS), not LaTeX. Easier styling, no TeX dependency, better table rendering. Custom CSS in `build/pdf.css`.
- **No DOCX:** Was previously generated; dropped because customers want PDF (final, printable) or web (searchable) — DOCX adds maintenance with no audience benefit.

## Recent changes

- Restructured into `docs/` for MkDocs (April 2026)
- Split decision tree into Workload / Human / Device sub-trees
- Replaced unified mermaid in main reference with text pointer (sub-trees inline per section)
- Added `build-pdf.py` (replaces `build-docx.py`)
- Added GH Actions workflow: site → Pages, PDFs → release artifacts

## Known gotchas

- MkDocs slugify strips Danish characters (æ → empty, å → a) — internal anchor links to `.da.md` headings must use the stripped form
- weasyprint binary needs to be on `PATH` at build time (`PATH=".venv/bin:$PATH"`)
- The `pypandoc_binary` package bundles pandoc — no system pandoc install required
