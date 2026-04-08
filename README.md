# Identity Types & Authentication — Microsoft Entra ID and Active Directory

Guidelines for choosing the right identity type and authentication mechanism across Azure, on-premises, and hybrid environments.

## Documents

| Document | Description |
| --- | --- |
| [Entra-AD-Identity-Types-and-Authentication.md](Entra-AD-Identity-Types-and-Authentication.md) | Full reference — preferred ranking, decision tree, universal protections, and detailed sections per identity type with authentication mechanisms and hardening guidance |
| [identity-decision-tree.md](identity-decision-tree.md) | Standalone decision tree — flowchart for picking the right identity type, including forced-choice gates for scenarios where the preferred option isn't possible |

## Key principles

- **Prefer managed/secretless identities** — Managed Identity and Workload Identity Federation eliminate credentials entirely
- **Document exceptions** — when constraints force a less-preferred choice (client secret, standard SA, password + MFA), record why
- **Plan migration** — forced choices are accepted today, not endorsed forever
