# Identity Types & Authentication — Microsoft Entra ID and Active Directory

Source for the bilingual (English / Danish) identity-selection guide. Covers identity types and authentication mechanisms across Microsoft Entra ID and Active Directory, with mandatory hardening for forced-choice exceptions.

> **Read it on the web:** <https://frederikleed.github.io/IdentityTypesAndAuth/>
> **Download as PDF:** see the [latest release](https://github.com/FrederikLeed/IdentityTypesAndAuth/releases/latest)

## What's published

| Format | Audience | Source |
| --- | --- | --- |
| Web site (EN + DA) | Anyone — searchable, navigable, mermaid renders inline | `docs/` → MkDocs Material → GitHub Pages |
| Full PDF (EN + DA) | Reference doc for IT-security teams | `docs/index.md` + `docs/full-reference.md` |
| One-page handout (EN + DA) | Printable lookup card for operators | `docs/index.md` only |

Built automatically on every push (site) and every release (PDFs) via [`.github/workflows/build.yml`](.github/workflows/build.yml).

## Repository layout

```
docs/                            # MkDocs source — every page is bilingual via .da.md suffix
├── index.md                     # Lookup table + key principles + forced-choice summary
├── decision-tree.md             # Full unified decision tree (web only)
├── full-reference.md            # Per-type reference with category sub-trees inline
└── diagrams/
    ├── decision-tree.{mmd,png}  # Unified tree
    └── tree-{workload,human,device}.{mmd,png}  # Category sub-trees (PDF + reference)

mkdocs.yml                       # MkDocs Material + i18n (EN/DA suffix mode)
build-pdf.py                     # Builds 4 PDFs via pandoc + weasyprint
build/pdf.css                    # Print stylesheet (page setup, table styling, headings)
.github/workflows/build.yml      # Site → Pages on push; PDFs → release artifacts on tag
```

## Local development

```bash
python -m venv .venv
.venv/bin/pip install mkdocs-material 'mkdocs-static-i18n[material]' weasyprint pypandoc_binary

# Serve site with live reload
.venv/bin/mkdocs serve

# Build static site to site/
.venv/bin/mkdocs build --strict

# Build PDFs to release/
PATH=".venv/bin:$PATH" .venv/bin/python build-pdf.py
```

## Diagrams

Mermaid is the source of truth for all decision trees. Pre-rendered PNGs live in `docs/diagrams/` for the PDF build (mermaid blocks aren't pre-processed during PDF build — sub-trees referenced as images are fine, the unified tree is only on the web).

Re-render after editing a `.mmd` file:

```bash
mmdc -p ../docs-toolbox/scripts/puppeteer-config.json \
  -i docs/diagrams/tree-workload.mmd \
  -o docs/diagrams/tree-workload.png \
  -w 1200 --scale 2 -b transparent
```

## Releasing

Tag and publish a release on GitHub. The workflow attaches all four PDFs to the release as downloads.

```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
gh release create v1.0.0 --generate-notes
```
