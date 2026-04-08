# Beslutningstræ for identitetstyper

```mermaid
flowchart TD
    Start([Hvad har brug for en identitet?]) --> WhoWhat{Menneske, workload<br/>eller enhed?}

    %% ── WORKLOAD-GREN ──
    WhoWhat -->|Workload / Tjeneste| Azure{Kører i Azure?}

    Azure -->|Ja| MIBlock{Understøtter ressourcen<br/>Managed Identity?}

    MIBlock -->|Nej — f.eks. legacy<br/>SDK, multi-tenant<br/>app, SAML/OIDC RP| APP_SECRET_AZ[App Registration<br/>med Client Secret<br/>--- tvungent valg ---<br/>dokumentér undtagelse]

    MIBlock -->|Ja| Shared{Deles på tværs af<br/>flere Azure-<br/>ressourcer?}
    Shared -->|Nej| MI_SYS[Systemtildelt<br/>Managed Identity]
    Shared -->|Ja| MI_USER[Brugertildelt<br/>Managed Identity]

    Azure -->|Nej| ExtIdP{Har en ekstern<br/>OIDC-udbyder?<br/>f.eks. GitHub Actions,<br/>GCP, AWS, Terraform}
    ExtIdP -->|Ja| WIF[Workload Identity<br/>Federation]
    ExtIdP -->|Nej| CertOK{Kan opbevare og<br/>rotere et<br/>certifikat?}
    CertOK -->|Ja| APP_CERT[App Registration<br/>med certifikat]
    CertOK -->|Nej — f.eks. embedded<br/>enhed, SaaS-callback,<br/>ingen cert-infra| APP_SECRET[App Registration<br/>med Client Secret<br/>--- tvungent valg ---<br/>dokumentér undtagelse]

    %% ── ON-PREM TJENESTE-UNDERGREN ──
    Azure -- On-prem tjeneste --> OnPremDomain{Er hosten<br/>domænetilsluttet?}
    OnPremDomain -->|Nej — Linux-host,<br/>workgroup, DMZ| LEGACY_SA_FORCED[Standard AD<br/>Service Account<br/>--- tvungent valg ---<br/>dokumentér undtagelse]
    OnPremDomain -->|Ja| OnPrem{Understøtter<br/>applikationen gMSA?}
    OnPrem -->|Ja| GMSA[gMSA<br/>Group Managed<br/>Service Account]
    OnPrem -->|Nej — f.eks. legacy-app,<br/>hardkodede credentials,<br/>tredjeparts-agent| LEGACY_SA[Standard AD<br/>Service Account<br/>--- tvungent valg ---<br/>planlæg migrering til gMSA]

    %% ── MENNESKE-GREN ──
    WhoWhat -->|Menneske| HumanType{Intern medarbejder<br/>eller ekstern?}

    HumanType -->|Ekstern partner<br/>/ leverandør| GUEST[Guest / B2B<br/>Identitet]
    HumanType -->|Kunde /<br/>forbruger| B2C[B2C / CIAM<br/>Identitet]

    HumanType -->|Intern<br/>medarbejder| PwdlessOK{Understøtter<br/>passwordless?<br/>f.eks. FIDO2, WHfB,<br/>Authenticator}
    PwdlessOK -->|Nej — f.eks. delt<br/>kiosk, fabriksgulv,<br/>ingen biometrisk HW| CLOUD_PWD[Cloud-only<br/>brugerkonto<br/>+ adgangskode + MFA<br/>--- tvungent valg ---<br/>dokumentér undtagelse]
    PwdlessOK -->|Ja| OnPremNeeded{Behøver adgang til<br/>on-prem AD-<br/>ressourcer?}
    OnPremNeeded -->|Nej| CLOUD[Cloud-only<br/>brugerkonto<br/>+ Passwordless]
    OnPremNeeded -->|Ja| HYBRID[Hybrid /<br/>synkroniseret<br/>brugerkonto + PHS]

    CLOUD --> Priv{Har privilegerede<br/>roller?}
    HYBRID --> Priv
    CLOUD_PWD --> Priv

    Priv -->|Ja| PRIV_ACC[Dedikeret admin-<br/>konto<br/>+ PIM + PAW<br/>+ phishing-resistent MFA]

    %% ── ENHEDS-GREN ──
    WhoWhat -->|Enhed| DevOwner{Virksomhedsejet<br/>eller personlig BYOD?}

    DevOwner -->|BYOD / Personlig| REGISTERED[Entra Registered<br/>enhed<br/>--- Svageste tillid ---]

    DevOwner -->|Virksomhed| DevOnPrem{Behøver on-prem AD-<br/>computerkonto?}
    DevOnPrem -->|Nej| ENTRA_JOIN[Entra Joined<br/>enhed]
    DevOnPrem -->|Ja| DevCanMigrate{Kan GPO-/<br/>Kerberos-afhængighed<br/>fjernes?}
    DevCanMigrate -->|Ja — planlæg det| ENTRA_JOIN
    DevCanMigrate -->|Nej — f.eks. legacy LOB-<br/>app, NLA/RDP til<br/>on-prem, printer-GPO| HYBRID_JOIN[Hybrid Entra<br/>Joined enhed<br/>--- tvungent valg ---<br/>dokumentér undtagelse]

    %% ── STILARTER ──
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

## Sådan læses diagrammet

| Farve | Betydning |
| ------ | ------- |
| **Mørkegrøn** | Foretrukken — ingen credentials eller stærkeste sikkerhedsstilling |
| **Grøn** | Anbefalet til scenariet |
| **Guld** | Acceptabel — yderligere kontroller påkrævet |
| **Orange** | Overgangsløsning — planlæg migrering væk |
| **Rød** | Undgå — legacy-antimønster, migrér hurtigst muligt |

## Hurtig reference

| Beslutning | Anbefalet identitet |
| -------- | -------------- |
| Azure-workload, enkelt ressource | Systemtildelt Managed Identity |
| Azure-workload, delt på tværs af ressourcer | Brugertildelt Managed Identity |
| Azure-workload, Managed Identity ikke mulig (multi-tenant, legacy SDK, SAML RP) | App Reg + Client Secret (dokumentér undtagelse) |
| Ikke-Azure-workload, har OIDC-udbyder | Workload Identity Federation |
| Ikke-Azure-workload, kan opbevare certifikat | App Registration + certifikat |
| Ikke-Azure-workload, ingen cert-infra (SaaS, embedded enhed) | App Reg + Client Secret (dokumentér undtagelse) |
| On-prem tjeneste, domænetilsluttet, gMSA-kompatibel | gMSA |
| On-prem tjeneste, app understøtter ikke gMSA (legacy, hardkodede credentials) | Standard AD SA (dokumentér undtagelse, planlæg migrering) |
| On-prem tjeneste, host ikke domænetilsluttet (Linux, DMZ) | Standard AD SA (dokumentér undtagelse) |
| Intern medarbejder, passwordless-kompatibel | Cloud-only bruger + Passwordless |
| Intern medarbejder, ingen passwordless HW (kiosk, fabriksgulv) | Cloud-only bruger + adgangskode + MFA (dokumentér undtagelse) |
| Intern medarbejder, behøver on-prem AD | Synkroniseret bruger + PHS |
| Enhver admin / privilegeret rolle | Dedikeret admin-konto + PIM + PAW |
| Ekstern partner | Guest / B2B |
| Kundevendt applikation | B2C / CIAM |
| Virksomhedsenhed, ingen on-prem-afhængighed | Entra Joined |
| Virksomhedsenhed, kan ikke fjerne GPO/Kerberos (legacy LOB, NLA) | Hybrid Entra Joined (dokumentér undtagelse) |
| Personlig / BYOD-enhed | Entra Registered |

## Hærdning ved tvungne valg

Når beslutningstræet fører til en rød eller orange node, gælder disse obligatoriske sikkerhedsforanstaltninger. Se den fulde vejledning i [Entra-AD-Identity-Types-and-Authentication.md](Entra-AD-Identity-Types-and-Authentication.md#forced-choice-hardening--when-you-cannot-use-the-preferred-option).

| Tvungent valg | Centrale obligatoriske kontroller |
| --- | --- |
| **App Reg + Client Secret** | Maks. 90 dages levetid for secret, automatiseret rotation, kun opbevaring i Key Vault, Conditional Access for workload-identiteter, mindste privilegium, kvartalsvis gennemgang, navngivne ejere, migreringsplan |
| **Standard AD Service Account** | 30+ tegn tilfældig adgangskode, nægt interaktivt logon, begræns logon-as-a-service til specifikke hosts, MDI-overvågning, migreringsplan til gMSA |
| **Cloud-only bruger + adgangskode + MFA** | Authenticator med nummermatch (ingen SMS), 14+ tegn adgangskode, liste over forbudte adgangskoder, kræv kompatibel enhed, login-risikopolitikker, migreringsplan til passwordless |
| **Hybrid Entra Joined enhed** | Aktivér Intune co-management, kræv enhedsoverensstemmelse (ikke kun join), auditér GPO'er for Intune-ækvivalenter, kvartalsvis migreringsgennemgang |
