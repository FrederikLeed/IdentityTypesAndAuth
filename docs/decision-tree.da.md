# Beslutningstræ for identitetstyper

![Beslutningstræ for identitet](diagrams/decision-tree.da.png)

<details><summary>Mermaid-kilde</summary>

```mermaid
flowchart TD
    Start([Hvad har brug for en identitet?]) --> Type{Menneske, workload<br/>eller enhed?}

    %% ============ WORKLOAD ============
    Type -->|Workload / Tjeneste| WLoc{Hvor kører<br/>den?}

    WLoc -->|Azure| MIBlock{Understøtter ressourcen<br/>Managed Identity?}
    MIBlock -->|Ja| Shared{Deles på tværs af<br/>flere ressourcer?}
    Shared -->|Nej| MI_SYS[Systemtildelt<br/>Managed Identity]
    Shared -->|Ja| MI_USER[Brugertildelt<br/>Managed Identity]
    MIBlock -->|Nej — legacy SDK,<br/>multi-tenant app,<br/>SAML/OIDC RP| APP_SEC_AZ[App Reg + Client Secret<br/>TVUNGET — dokumentér undtagelse]

    WLoc -->|Ekstern / CI-CD<br/>med OIDC-udbyder| WIF[Workload Identity<br/>Federation]

    WLoc -->|Ekstern /<br/>uden OIDC-udbyder| CertOK{Kan opbevare og<br/>rotere et certifikat?}
    CertOK -->|Ja| APP_CERT[App Reg + Certifikat]
    CertOK -->|Nej — embedded enhed,<br/>SaaS-callback,<br/>ingen cert-infra| APP_SEC[App Reg + Client Secret<br/>TVUNGET — dokumentér undtagelse]

    WLoc -->|On-prem tjeneste| OPDom{Er hosten<br/>domænetilsluttet?}
    OPDom -->|Ja| GMSAOK{App understøtter<br/>gMSA / dMSA?}
    GMSAOK -->|Ja| GMSA[gMSA / dMSA]
    GMSAOK -->|Nej — legacy-app,<br/>hardkodede creds,<br/>tredjeparts-agent| LSA[Standard AD SA<br/>TVUNGET — planlæg gMSA-migrering]
    OPDom -->|Nej — Linux-host,<br/>workgroup, DMZ| LSA_F[Standard AD SA<br/>TVUNGET — dokumentér undtagelse]

    %% ============ MENNESKE ============
    Type -->|Menneske| Who{Intern medarbejder,<br/>partner eller kunde?}
    Who -->|Kunde / forbruger| B2C[B2C / CIAM]
    Who -->|Ekstern partner /<br/>leverandør| GUEST[Guest / B2B]
    Who -->|Intern medarbejder| PWless{Understøtter passwordless?<br/>FIDO2, WHfB,<br/>Authenticator}

    PWless -->|Ja| OnPremNeed{Behøver on-prem<br/>AD-ressourcer?}
    OnPremNeed -->|Nej| CLOUD[Cloud-only bruger<br/>+ Passwordless]
    OnPremNeed -->|Ja| HYBRID[Hybridbruger + PHS<br/>+ Passwordless]
    PWless -->|Nej — delt kiosk,<br/>fabriksgulv,<br/>ingen biometrisk HW| CLOUD_PWD[Cloud-only bruger<br/>+ adgangskode + MFA<br/>TVUNGET — dokumentér undtagelse]

    CLOUD --> Priv{Har privilegerede<br/>roller?}
    HYBRID --> Priv
    CLOUD_PWD --> Priv
    Priv -->|Ja — overlay| PRIV[Dedikeret admin-konto<br/>+ PIM + PAW<br/>+ phishing-resistent MFA]
    Priv -->|Nej| Std([Brug som den er])

    %% ============ ENHED ============
    Type -->|Enhed| DOwn{Virksomhedsejet<br/>eller BYOD?}
    DOwn -->|BYOD / Personlig| REG[Entra Registered enhed<br/>SVAGESTE tillid]
    DOwn -->|Virksomhed| DOnPrem{Behøver on-prem AD-<br/>computerkonto?}
    DOnPrem -->|Nej| EJ[Entra Joined enhed]
    DOnPrem -->|Ja| Migrate{Kan GPO-/<br/>Kerberos-afhængighed<br/>fjernes?}
    Migrate -->|Ja — planlæg det| EJ
    Migrate -->|Nej — legacy LOB,<br/>NLA/RDP,<br/>printer-GPO| HJ[Hybrid Entra Joined enhed<br/>TVUNGET — dokumentér undtagelse]

    %% ── STILARTER ──
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

Når beslutningstræet fører til en rød eller orange node, gælder disse obligatoriske sikkerhedsforanstaltninger. Se den fulde vejledning i [Fuld reference](full-reference.md#hrdning-ved-tvungne-valg-nar-den-foretrukne-mulighed-ikke-kan-anvendes).

| Tvungent valg | Centrale obligatoriske kontroller |
| --- | --- |
| **App Reg + Client Secret** | Maks. 90 dages levetid for secret, automatiseret rotation, kun opbevaring i Key Vault, Conditional Access for workload-identiteter, mindste privilegium, kvartalsvis gennemgang, navngivne ejere, migreringsplan |
| **Standard AD Service Account** | 30+ tegn tilfældig adgangskode, nægt interaktivt logon, begræns logon-as-a-service til specifikke hosts, MDI-overvågning, migreringsplan til gMSA |
| **Cloud-only bruger + adgangskode + MFA** | Authenticator med nummermatch (ingen SMS), 14+ tegn adgangskode, liste over forbudte adgangskoder, kræv kompatibel enhed, login-risikopolitikker, migreringsplan til passwordless |
| **Hybrid Entra Joined enhed** | Aktivér Intune co-management, kræv enhedsoverensstemmelse (ikke kun join), auditér GPO'er for Intune-ækvivalenter, kvartalsvis migreringsgennemgang |
