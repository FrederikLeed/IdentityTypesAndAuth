---
project: IdentityTypesAndAuth
repo: https://github.com/FrederikLeed/IdentityTypesAndAuth
updated: 2026-04-29
status: active
---

# Identity Types & Authentication

Internal IT-security reference covering identity types and authentication mechanisms across Microsoft Entra ID and on-premises Active Directory. The repo holds the source-of-truth markdown, the decision tree (Mermaid), and a build script that produces DOCX releases.

## What it is

A bilingual (English/Danish) guide for IT-security teams choosing the right identity type for any new workload, human, or device. It ranks 15 identity types from most to least preferred, gives a flowchart for routine decisions, and — crucially — defines mandatory hardening controls for the four "forced-choice" cases where the preferred option is impossible (client secret app reg, standard AD SA, password + MFA cloud user, hybrid Entra Joined device).

## Audience

IT security team. Technical reviewers, architects, and operators making identity-design decisions.

## Recent changes

- Decision tree restructured: workload branch now opens with "Where does it run?" (Azure / external / on-prem) instead of forcing on-prem off the Azure decision
- §5.3 added covering Delegated Managed Service Accounts (dMSA, Server 2025) — was orphaned in the rank table
- `build-docx.py` now renders mermaid blocks to PNG via `mmdc` and embeds them in DOCX (was previously placeholder-only)
- Decision tree pre-rendered to PNG and embedded in README

## How to read it

- **Day-to-day decisions** — open [`identity-decision-tree.md`](identity-decision-tree.md), follow the flowchart
- **Forced-choice exception design** — go to "Forced-Choice Hardening" in the main reference for the mandatory controls
- **Per-identity detail** — main reference is organised by category (Human, Workload, Device, On-prem service) with pros, cons, and protection guidance

## Build & deliver

```bash
python -m venv .venv
.venv/bin/pip install pypandoc pypandoc_binary
.venv/bin/python build-docx.py
```

Output: `release/*.docx`. Requires `mmdc` (mermaid-cli) for diagram rendering — without it, mermaid blocks fall back to placeholders.

## Constraints

- DOCX styling controlled by `reference.docx` (auto-generated on first run, then customise in Word)
- Mermaid → PNG render needs Chrome via Puppeteer; build script auto-detects `~/.cache/puppeteer/` or honours `PUPPETEER_EXECUTABLE_PATH`
- Danish translation must be kept in sync with English when content changes
