# Identitetstyper og autentificering

Vejledning til valg af den rigtige identitetstype og autentificeringsmekanisme i Microsoft Entra ID og Active Directory. Rangeret efter sikkerhedsniveau og moderne tilpasning, med obligatorisk hærdning når begrænsninger tvinger et mindre foretrukket valg.

## Hurtig reference

Vælg den række der matcher dit scenarie, og brug identiteten i højre kolonne. Tvungne rækker kræver en dokumenteret undtagelse — se [Hærdning ved tvungne valg](#hrdning-ved-tvungne-valg) nedenfor og den [fulde reference](full-reference.md#hrdning-ved-tvungne-valg-nar-den-foretrukne-mulighed-ikke-kan-anvendes).

| Scenarie | Anbefalet identitet |
| --- | --- |
| Azure-workload, enkelt ressource | Systemtildelt Managed Identity |
| Azure-workload, delt på tværs af ressourcer | Brugertildelt Managed Identity |
| Azure-workload, MI ikke mulig (multi-tenant, legacy SDK, SAML RP) | App Reg + Client Secret *(tvunget — dokumentér undtagelse)* |
| Ikke-Azure-workload, har OIDC-udbyder | Workload Identity Federation |
| Ikke-Azure-workload, kan opbevare cert | App Registration + Certifikat |
| Ikke-Azure-workload, ingen cert-infra (SaaS, embedded enhed) | App Reg + Client Secret *(tvunget — dokumentér undtagelse)* |
| On-prem tjeneste, domænetilsluttet, gMSA-kompatibel | gMSA / dMSA |
| On-prem tjeneste, app understøtter ikke gMSA (legacy, hardkodede creds) | Standard AD SA *(tvunget — planlæg migration)* |
| On-prem tjeneste, host ikke domænetilsluttet (Linux, DMZ) | Standard AD SA *(tvunget — dokumentér undtagelse)* |
| Intern medarbejder, passwordless-kompatibel | Cloud-only bruger + Passwordless |
| Intern medarbejder, ingen passwordless-HW (kiosk, fabriksgulv) | Cloud-only bruger + adgangskode + MFA *(tvunget — dokumentér undtagelse)* |
| Intern medarbejder, behøver on-prem AD | Synkroniseret bruger + PHS + Passwordless |
| Enhver admin / privilegeret rolle | Dedikeret admin-konto + PIM + PAW |
| Ekstern partner | Guest / B2B |
| Kundevendt applikation | B2C / CIAM |
| Virksomhedsenhed, ingen on-prem-afhængighed | Entra Joined |
| Virksomhedsenhed, kan ikke fjerne GPO/Kerberos (legacy LOB, NLA) | Hybrid Entra Joined *(tvunget — dokumentér undtagelse)* |
| Personlig / BYOD-enhed | Entra Registered |

## Hærdning ved tvungne valg

Når tabellen tvinger et mindre foretrukket valg, gælder disse obligatoriske kontroller. Hvert tvunget valg skal have en navngiven ejer, en dokumenteret undtagelse og en migreringsplan.

| Tvungent valg | Centrale obligatoriske kontroller |
| --- | --- |
| **App Reg + Client Secret** | Maks. 90 dages levetid for secret, automatiseret rotation, kun opbevaring i Key Vault, Conditional Access for workload-identiteter, mindste privilegium, kvartalsvis gennemgang, navngivne ejere, migreringsplan |
| **Standard AD-tjenestekonto** | 30+ tegn tilfældig adgangskode, nægt interaktivt logon, begræns logon-as-a-service til specifikke hosts, MDI-overvågning, migreringsplan til gMSA / dMSA |
| **Cloud-only bruger + adgangskode + MFA** | Authenticator med nummermatch (ingen SMS), 14+ tegn adgangskode, liste over forbudte adgangskoder, kræv kompatibel enhed, login-risikopolitikker, migreringsplan til passwordless |
| **Hybrid Entra Joined-enhed** | Aktivér Intune co-management, kræv enhedsoverensstemmelse (ikke kun join), auditér GPO'er for Intune-ækvivalenter, kvartalsvis migreringsgennemgang |

Fuld hærdningsdetaljer per tvunget valg: [`full-reference.md`](full-reference.md#hrdning-ved-tvungne-valg-nar-den-foretrukne-mulighed-ikke-kan-anvendes)

## Centrale principper

- **Foretræk managed/hemmeligheds-frie identiteter** — Managed Identity og Workload Identity Federation eliminerer legitimationsoplysninger fuldstændigt
- **Dokumentér undtagelser** — når begrænsninger tvinger et mindre foretrukket valg, registrér hvorfor, hvem der ejer det, og migreringsplanen
- **Planlæg migration** — tvungne valg accepteres i dag, men de er ikke endorseret for evigt; gennemgå kvartalsvis

## Beslutningstræ

Hvis du foretrækker at arbejde via et flowchart, viser [Beslutningstræ](decision-tree.md)-siden det fulde forenede træ. Den fulde reference har også del-træer per kategori.

## Hvor du kan grave dybere

- [Beslutningstræ](decision-tree.md) — fuldt forenet flowchart
- [Fuld reference](full-reference.md) — hver identitetstype med autentificeringsmekanismer, fordele, ulemper og beskyttelsesvejledning
