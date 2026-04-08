# Identity Types & Authentication — Microsoft Entra ID and Active Directory

Guidelines for choosing the right identity type and authentication mechanism across Azure, on-premises, and hybrid environments.

## Documents

| Document | Language | Description |
| --- | --- | --- |
| [Entra-AD-Identity-Types-and-Authentication.md](Entra-AD-Identity-Types-and-Authentication.md) | English | Full reference — preferred ranking, decision tree, universal protections, and detailed sections per identity type with authentication mechanisms and hardening guidance |
| [Entra-AD-Identity-Types-and-Authentication.da.md](Entra-AD-Identity-Types-and-Authentication.da.md) | Dansk | Samme dokument oversat til dansk |
| [identity-decision-tree.md](identity-decision-tree.md) | English | Standalone decision tree — flowchart for picking the right identity type, including forced-choice gates for scenarios where the preferred option isn't possible |
| [identity-decision-tree.da.md](identity-decision-tree.da.md) | Dansk | Beslutningstræ oversat til dansk |

## Key principles

- **Prefer managed/secretless identities** — Managed Identity and Workload Identity Federation eliminate credentials entirely
- **Document exceptions** — when constraints force a less-preferred choice (client secret, standard SA, password + MFA), record why
- **Plan migration** — forced choices are accepted today, not endorsed forever

## Building DOCX releases

A Python script converts all documents (except README) to `.docx` for distribution:

```bash
pip install pypandoc pypandoc_binary
python build-docx.py
```

Output goes to `release/`. On first run a `reference.docx` template is generated — open it in Word to customise styles (fonts, colours, headers), then re-run to apply your branding to all exports.
