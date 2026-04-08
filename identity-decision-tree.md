# Identity Type Decision Tree

```mermaid
flowchart TD
    Start([What needs an identity?]) --> WhoWhat{Human or workload<br/>or device?}

    %% ── WORKLOAD BRANCH ──
    WhoWhat -->|Workload / Service| Azure{Runs in Azure?}

    Azure -->|Yes| MIBlock{Resource supports<br/>Managed Identity?}

    MIBlock -->|No — e.g. legacy<br/>SDK, multi-tenant<br/>app, SAML/OIDC RP| APP_SECRET_AZ[App Registration<br/>with Client Secret<br/>--- forced choice ---<br/>document exception]

    MIBlock -->|Yes| Shared{Shared across<br/>multiple Azure<br/>resources?}
    Shared -->|No| MI_SYS[System-assigned<br/>Managed Identity]
    Shared -->|Yes| MI_USER[User-assigned<br/>Managed Identity]

    Azure -->|No| ExtIdP{Has an external<br/>OIDC provider?<br/>e.g. GitHub Actions,<br/>GCP, AWS, Terraform}
    ExtIdP -->|Yes| WIF[Workload Identity<br/>Federation]
    ExtIdP -->|No| CertOK{Can store &amp;<br/>rotate a<br/>certificate?}
    CertOK -->|Yes| APP_CERT[App Registration<br/>with Certificate]
    CertOK -->|No — e.g. embedded<br/>device, SaaS callback,<br/>no cert infra| APP_SECRET[App Registration<br/>with Client Secret<br/>--- forced choice ---<br/>document exception]

    %% ── ON-PREM SERVICE SUB-BRANCH ──
    Azure -- On-prem service --> OnPremDomain{Host is<br/>domain-joined?}
    OnPremDomain -->|No — Linux host,<br/>workgroup, DMZ| LEGACY_SA_FORCED[Standard AD<br/>Service Account<br/>--- forced choice ---<br/>document exception]
    OnPremDomain -->|Yes| OnPrem{Application<br/>supports gMSA?}
    OnPrem -->|Yes| GMSA[gMSA<br/>Group Managed<br/>Service Account]
    OnPrem -->|No — e.g. legacy app,<br/>hardcoded creds,<br/>third-party agent| LEGACY_SA[Standard AD<br/>Service Account<br/>--- forced choice ---<br/>plan migration to gMSA]

    %% ── HUMAN BRANCH ──
    WhoWhat -->|Human| HumanType{Internal employee<br/>or external?}

    HumanType -->|External partner<br/>/ vendor| GUEST[Guest / B2B<br/>Identity]
    HumanType -->|Customer /<br/>consumer| B2C[B2C / CIAM<br/>Identity]

    HumanType -->|Internal<br/>employee| PwdlessOK{Supports<br/>passwordless?<br/>e.g. FIDO2, WHfB,<br/>Authenticator}
    PwdlessOK -->|No — e.g. shared<br/>kiosk, factory floor,<br/>no biometric HW| CLOUD_PWD[Cloud-only<br/>User Account<br/>+ Password + MFA<br/>--- forced choice ---<br/>document exception]
    PwdlessOK -->|Yes| OnPremNeeded{Needs access to<br/>on-prem AD<br/>resources?}
    OnPremNeeded -->|No| CLOUD[Cloud-only<br/>User Account<br/>+ Passwordless]
    OnPremNeeded -->|Yes| HYBRID[Hybrid /<br/>Synced User<br/>Account + PHS]

    CLOUD --> Priv{Holds privileged<br/>roles?}
    HYBRID --> Priv
    CLOUD_PWD --> Priv

    Priv -->|Yes| PRIV_ACC[Dedicated Admin<br/>Account<br/>+ PIM + PAW<br/>+ Phishing-resistant MFA]

    %% ── DEVICE BRANCH ──
    WhoWhat -->|Device| DevOwner{Corporate-owned<br/>or personal BYOD?}

    DevOwner -->|BYOD / Personal| REGISTERED[Entra Registered<br/>Device<br/>--- Weakest trust ---]

    DevOwner -->|Corporate| DevOnPrem{Needs on-prem AD<br/>computer account?}
    DevOnPrem -->|No| ENTRA_JOIN[Entra Joined<br/>Device]
    DevOnPrem -->|Yes| DevCanMigrate{Can remove<br/>GPO / Kerberos<br/>dependency?}
    DevCanMigrate -->|Yes — plan it| ENTRA_JOIN
    DevCanMigrate -->|No — e.g. legacy LOB<br/>app, NLA/RDP to<br/>on-prem, printer GPO| HYBRID_JOIN[Hybrid Entra<br/>Joined Device<br/>--- forced choice ---<br/>document exception]

    %% ── STYLES ──
    classDef best fill:#1a7a1a,stroke:#0d4d0d,color:#fff
    classDef good fill:#2d8a2d,stroke:#1a5c1a,color:#fff
    classDef ok fill:#b8860b,stroke:#8b6508,color:#fff
    classDef avoid fill:#cc3333,stroke:#8b0000,color:#fff
    classDef transition fill:#cc8800,stroke:#8b5e00,color:#fff
    classDef neutral fill:#336699,stroke:#1a3d5c,color:#fff

    class MI_SYS,MI_USER best
    class WIF,CLOUD good
    class GMSA,APP_CERT,ENTRA_JOIN,PRIV_ACC good
    class HYBRID,GUEST,B2C ok
    class APP_SECRET,LEGACY_SA,LEGACY_SA_FORCED,APP_SECRET_AZ avoid
    class HYBRID_JOIN,REGISTERED,CLOUD_PWD transition
    class Start neutral
```

## How to read this diagram

| Colour | Meaning |
| ------ | ------- |
| **Dark green** | Preferred — zero credentials or strongest posture |
| **Green** | Recommended for the scenario |
| **Gold** | Acceptable — additional controls required |
| **Orange** | Transitional — plan migration away |
| **Red** | Avoid — legacy anti-pattern, migrate ASAP |

## Quick reference

| Decision | Go-to identity |
| -------- | -------------- |
| Azure workload, single resource | System-assigned Managed Identity |
| Azure workload, shared across resources | User-assigned Managed Identity |
| Azure workload, MI not possible (multi-tenant, legacy SDK, SAML RP) | App Reg + Client Secret (document exception) |
| Non-Azure workload, has OIDC provider | Workload Identity Federation |
| Non-Azure workload, can store cert | App Registration + Certificate |
| Non-Azure workload, no cert infra (SaaS, embedded device) | App Reg + Client Secret (document exception) |
| On-prem service, domain-joined, gMSA-capable | gMSA |
| On-prem service, app can't do gMSA (legacy, hardcoded creds) | Standard AD SA (document exception, plan migration) |
| On-prem service, host not domain-joined (Linux, DMZ) | Standard AD SA (document exception) |
| Internal human, passwordless capable | Cloud-only User + Passwordless |
| Internal human, no passwordless HW (kiosk, factory floor) | Cloud-only User + Password + MFA (document exception) |
| Internal human, needs on-prem AD | Synced User + PHS |
| Any admin / privileged role | Dedicated Admin Account + PIM + PAW |
| External partner | Guest / B2B |
| Customer-facing app | B2C / CIAM |
| Corporate device, no on-prem dependency | Entra Joined |
| Corporate device, can't remove GPO/Kerberos (legacy LOB, NLA) | Hybrid Entra Joined (document exception) |
| Personal / BYOD device | Entra Registered |

## Forced-choice hardening

When the decision tree leads to a red or orange node, these mandatory guardrails apply. See the full guidance in [Entra-AD-Identity-Types-and-Authentication.md](Entra-AD-Identity-Types-and-Authentication.md#forced-choice-hardening--when-you-cannot-use-the-preferred-option).

| Forced choice | Key mandatory controls |
| --- | --- |
| **App Reg + Client Secret** | Max 90-day secret lifetime, automated rotation, Key Vault storage only, Conditional Access for workload identities, least-privilege permissions, quarterly review, named owners, migration plan |
| **Standard AD Service Account** | 30+ char random password, deny interactive logon, restrict logon-as-a-service to specific hosts, MDI monitoring, gMSA migration plan |
| **Cloud-only User + Password + MFA** | Authenticator with number matching (no SMS), 14+ char password, banned-password list, require compliant device, sign-in risk policies, passwordless migration plan |
| **Hybrid Entra Joined Device** | Enable Intune co-management, require device compliance (not just join), audit GPOs for Intune equivalents, quarterly migration review |
