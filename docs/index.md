# Identity Types & Authentication

Guidance for picking the right identity type and authentication mechanism across Microsoft Entra ID and Active Directory. Ranked by security posture and modern alignment, with mandatory hardening when constraints force a less-preferred option.

## Quick reference

Pick the row that matches your scenario, use the identity in the right column. Forced-choice rows require a documented exception — see [Forced-choice hardening](#forced-choice-hardening) below and the [full reference](full-reference.md#forced-choice-hardening-when-you-cannot-use-the-preferred-option).

| Scenario | Go-to identity |
| --- | --- |
| Azure workload, single resource | System-assigned Managed Identity |
| Azure workload, shared across resources | User-assigned Managed Identity |
| Azure workload, MI not possible (multi-tenant, legacy SDK, SAML RP) | App Reg + Client Secret *(forced — document exception)* |
| Non-Azure workload, has OIDC provider | Workload Identity Federation |
| Non-Azure workload, can store cert | App Registration + Certificate |
| Non-Azure workload, no cert infra (SaaS, embedded device) | App Reg + Client Secret *(forced — document exception)* |
| On-prem service, domain-joined, gMSA-capable | gMSA / dMSA |
| On-prem service, app can't do gMSA (legacy, hardcoded creds) | Standard AD SA *(forced — plan migration)* |
| On-prem service, host not domain-joined (Linux, DMZ) | Standard AD SA *(forced — document exception)* |
| Internal human, passwordless capable | Cloud-only User + Passwordless |
| Internal human, no passwordless HW (kiosk, factory floor) | Cloud-only User + Password + MFA *(forced — document exception)* |
| Internal human, needs on-prem AD | Synced User + PHS + Passwordless |
| Any admin / privileged role | Dedicated Admin Account + PIM + PAW |
| External partner | Guest / B2B |
| Customer-facing app | B2C / CIAM |
| Corporate device, no on-prem dependency | Entra Joined |
| Corporate device, can't remove GPO/Kerberos (legacy LOB, NLA) | Hybrid Entra Joined *(forced — document exception)* |
| Personal / BYOD device | Entra Registered |

## Forced-choice hardening

When the table forces a less-preferred option, these mandatory controls apply. Every forced choice must have a named owner, a documented exception, and a migration plan.

| Forced choice | Key mandatory controls |
| --- | --- |
| **App Reg + Client Secret** | Max 90-day secret lifetime, automated rotation, Key Vault storage only, Conditional Access for workload identities, least-privilege permissions, quarterly review, named owners, migration plan |
| **Standard AD Service Account** | 30+ char random password, deny interactive logon, restrict logon-as-a-service to specific hosts, MDI monitoring, gMSA / dMSA migration plan |
| **Cloud-only User + Password + MFA** | Authenticator with number matching (no SMS), 14+ char password, banned-password list, require compliant device, sign-in risk policies, passwordless migration plan |
| **Hybrid Entra Joined Device** | Enable Intune co-management, require device compliance (not just join), audit GPOs for Intune equivalents, quarterly migration review |

Full hardening detail per forced choice: [`full-reference.md`](full-reference.md#forced-choice-hardening-when-you-cannot-use-the-preferred-option)

## Key principles

- **Prefer managed/secretless identities** — Managed Identity and Workload Identity Federation eliminate credentials entirely
- **Document exceptions** — when constraints force a less-preferred choice, record why, who owns it, and the migration plan
- **Plan migration** — forced choices are accepted today, not endorsed forever; review quarterly

## Decision tree

If you prefer working through a flowchart, the [Decision tree](decision-tree.md) page renders the full unified tree. The full reference also has per-category sub-trees.

## Where to dig deeper

- [Decision tree](decision-tree.md) — full unified flowchart
- [Full reference](full-reference.md) — every identity type with auth mechanisms, pros, cons, and protection guidance
