# Identity Type Decision Tree

![Identity decision tree](diagrams/decision-tree.png)

<details><summary>Mermaid source</summary>

```mermaid
flowchart TD
    Start([What needs an identity?]) --> Type{Human, Workload,<br/>or Device?}

    %% ============ WORKLOAD ============
    Type -->|Workload / Service| WLoc{Where does<br/>it run?}

    WLoc -->|Azure| MIBlock{Resource supports<br/>Managed Identity?}
    MIBlock -->|Yes| Shared{Shared across<br/>multiple resources?}
    Shared -->|No| MI_SYS[System-assigned<br/>Managed Identity]
    Shared -->|Yes| MI_USER[User-assigned<br/>Managed Identity]
    MIBlock -->|No — legacy SDK,<br/>multi-tenant app,<br/>SAML/OIDC RP| APP_SEC_AZ[App Reg + Client Secret<br/>FORCED — document exception]

    WLoc -->|External / CI-CD<br/>with OIDC provider| WIF[Workload Identity<br/>Federation]

    WLoc -->|External /<br/>no OIDC provider| CertOK{Can store &amp;<br/>rotate a cert?}
    CertOK -->|Yes| APP_CERT[App Reg + Certificate]
    CertOK -->|No — embedded device,<br/>SaaS callback,<br/>no cert infra| APP_SEC[App Reg + Client Secret<br/>FORCED — document exception]

    WLoc -->|On-prem service| OPDom{Host is<br/>domain-joined?}
    OPDom -->|Yes| GMSAOK{App supports<br/>gMSA / dMSA?}
    GMSAOK -->|Yes| GMSA[gMSA / dMSA]
    GMSAOK -->|No — legacy app,<br/>hardcoded creds,<br/>third-party agent| LSA[Standard AD SA<br/>FORCED — plan gMSA migration]
    OPDom -->|No — Linux host,<br/>workgroup, DMZ| LSA_F[Standard AD SA<br/>FORCED — document exception]

    %% ============ HUMAN ============
    Type -->|Human| Who{Internal employee,<br/>partner, or customer?}
    Who -->|Customer / consumer| B2C[B2C / CIAM]
    Who -->|External partner /<br/>vendor| GUEST[Guest / B2B]
    Who -->|Internal employee| PWless{Supports passwordless?<br/>FIDO2, WHfB,<br/>Authenticator}

    PWless -->|Yes| OnPremNeed{Needs on-prem<br/>AD resources?}
    OnPremNeed -->|No| CLOUD[Cloud-only User<br/>+ Passwordless]
    OnPremNeed -->|Yes| HYBRID[Hybrid User + PHS<br/>+ Passwordless]
    PWless -->|No — shared kiosk,<br/>factory floor,<br/>no biometric HW| CLOUD_PWD[Cloud-only User<br/>+ Password + MFA<br/>FORCED — document exception]

    CLOUD --> Priv{Holds privileged<br/>roles?}
    HYBRID --> Priv
    CLOUD_PWD --> Priv
    Priv -->|Yes — overlay| PRIV[Dedicated Admin Account<br/>+ PIM + PAW<br/>+ Phishing-resistant MFA]
    Priv -->|No| Std([Use as-is])

    %% ============ DEVICE ============
    Type -->|Device| DOwn{Corporate-owned<br/>or BYOD?}
    DOwn -->|BYOD / Personal| REG[Entra Registered Device<br/>WEAKEST trust]
    DOwn -->|Corporate| DOnPrem{Needs on-prem AD<br/>computer account?}
    DOnPrem -->|No| EJ[Entra Joined Device]
    DOnPrem -->|Yes| Migrate{Can remove<br/>GPO / Kerberos<br/>dependency?}
    Migrate -->|Yes — plan it| EJ
    Migrate -->|No — legacy LOB,<br/>NLA/RDP,<br/>printer GPO| HJ[Hybrid Entra Joined Device<br/>FORCED — document exception]

    %% ── STYLES ──
    classDef best fill:#1a7a1a,stroke:#0d4d0d,color:#fff
    classDef good fill:#2d8a2d,stroke:#1a5c1a,color:#fff
    classDef ok fill:#b8860b,stroke:#8b6508,color:#fff
    classDef avoid fill:#cc3333,stroke:#8b0000,color:#fff
    classDef transition fill:#cc8800,stroke:#8b5e00,color:#fff
    classDef neutral fill:#336699,stroke:#1a3d5c,color:#fff

    class MI_SYS,MI_USER best
    class WIF,CLOUD,GMSA,APP_CERT,EJ,PRIV good
    class HYBRID,GUEST,B2C ok
    class APP_SEC,APP_SEC_AZ,LSA,LSA_F avoid
    class HJ,REG,CLOUD_PWD transition
    class Start,Std neutral
```

</details>

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

When the decision tree leads to a red or orange node, these mandatory guardrails apply. See the full guidance in [Full reference](full-reference.md#forced-choice-hardening-when-you-cannot-use-the-preferred-option).

| Forced choice | Key mandatory controls |
| --- | --- |
| **App Reg + Client Secret** | Max 90-day secret lifetime, automated rotation, Key Vault storage only, Conditional Access for workload identities, least-privilege permissions, quarterly review, named owners, migration plan |
| **Standard AD Service Account** | 30+ char random password, deny interactive logon, restrict logon-as-a-service to specific hosts, MDI monitoring, gMSA migration plan |
| **Cloud-only User + Password + MFA** | Authenticator with number matching (no SMS), 14+ char password, banned-password list, require compliant device, sign-in risk policies, passwordless migration plan |
| **Hybrid Entra Joined Device** | Enable Intune co-management, require device compliance (not just join), audit GPOs for Intune equivalents, quarterly migration review |
