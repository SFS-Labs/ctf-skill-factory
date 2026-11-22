# Freebuff V8 Runtime-Abnahme — Skill-Kollision und echter Toolaufruf

Stand: 2026-11-22. **Status: CODE_PREPARED / LIVE_RUNTIME_NOT_VERIFIED.**
Diese Datei ist ein Abnahmeverfahren, kein Beleg fuer einen bereits ausgefuehrten Desktop-Test.

## Technische Diagnose

- Freebuff-Quelle `sdk/src/skills/load-skills.ts`: projektlokales `.agents/skills/` hat
  Vorrang vor den globalen Skill-Verzeichnissen; ein Skill wird nur geladen,
  wenn Verzeichnis und `name` im YAML-Frontmatter uebereinstimmen.
- Freebuff-Quelle `packages/agent-runtime/src/tools/handlers/tool/skill.ts`: der
  `skill`-Toolaufruf bevorzugt die Projektdatei vor dem Sitzungs-Cache.
- Der vorherige `cloud_read_skill`-Readback war fuer den Account-Skill nicht
  beweiskraeftig (V7-Bundled-Shadow / Account-Only-Lookup).
- Der eigenstaendige Name `ctf-skill-index-v8` vermeidet diese
  Namenskollision, **erzwingt aber nicht automatisch Modellaktivierung**.
- Die Freebuff-Cloud-Sitzung muss wirklich mit Projektroot `~/ctf-skills`
  beziehungsweise dem Checkout mit diesem Skill gestartet werden.

## Repository- und Dateiabnahme

```bash
cd ~/ctf-skills
python3 -m unittest discover -s tests
python3 bin/skill-orchestrator.py selfcheck
bash -n install-freebuff.sh
bash install-freebuff.sh           # nur Vorschau
bash install-freebuff.sh --apply   # nur nach Kontrolle von Quelle und Ziel
sed -n '1,6p' .agents/skills/ctf-skill-index-v8/SKILL.md
```

Erwartet: `name: ctf-skill-index-v8`, `name` passt zum Verzeichnis,
`ctf-skill-index` bleibt unveraendert beziehungsweise nur mit bestehender V8-Bruecke,
und der Orchestrator ist ausfuehrbar. Tests auf dem *echten Node* erneut ausfuehren;
GitHub-Datei-Readbacks sind keine lokalen Testnachweise.

## Echte Runtime-Abnahme (neue Freebuff-Sitzung)

1. Eine **neue** Freebuff-Desktop-Sitzung mit dem Projektverzeichnis starten.
   Eine laufende alte Sitzung beweist keine neue `AGENTS.md`-/Skill-Discovery.
2. Benutzerauftrag ohne explizite Skill-Nennung:
   > Audit the authorized local Solidity Vault in corpora/verify for withdraw
   > reentrancy; verify with a reproducible local test and negative control.
3. Im Agenten-Toolprotokoll muss ein echter `skill`-Aufruf mit
   `name=ctf-skill-index-v8` erscheinen; Skill-Antwort muss die V8-Orchestrierung
   enthalten. Ein `cloud_read_skill`-Readback oder die bloße Skill-Liste genuegt nicht.
4. Im selben Agentenlauf muss ein **tatsaechlicher** Prozessaufruf
   `python3 bin/skill-orchestrator.py run ... --allow-exec` protokolliert sein,
   mit lokalem autorisiertem Ziel, Exit-Code und erzeugtem `evidence-report.json`.
5. `verify --report ...` ausfuehren; Counterexample, Negativkontrolle und
   Tool-Receipts anhand der Artefakte pruefen. Der Agentenbericht allein ist
   keine unabhaengige Evidenz.
6. Negativkontrolle: Neue, sachfremde Anfrage (z. B. Marketingtext) darf
   V8 nicht ohne fachlichen Anlass aktivieren.
7. Umgebungsgrenzen ausdruecklich pruefen: Wenn die Freebuff-Cloud den
   `~/ctf-skills`-Node nicht erreicht, keine lokale Toolausfuehrung vortaeuschen.

## Maschinenlesbare Abnahme

Nur nach beobachtetem Lauf im existierenden `VERIFICATION.md` oder unter
`logs/v8/runtime-acceptance-<timestamp>.json` festhalten:

```json
{
  "skill_name": "ctf-skill-index-v8",
  "skill_tool_invoked": false,
  "skill_body_confirmed": false,
  "orchestrator_run_invoked": false,
  "report_verified": false,
  "negative_activation_test": "NOT_RUN",
  "status": "RUNTIME_UNVERIFIED"
}
```

Die obigen `false`-Werte sind Ausgangszustand, keine Testresultate.

Status nur bei belegter Evidenz hochstufen: `SKILL_LOADED` nach echtem
`skill`-Aufruf, `ORCHESTRATOR_EXECUTED` nach realem `run`,
`RUNTIME_VERIFIED` erst bei belastbarem End-to-End-Nachweis einschließlich
negativer Aktivierungskontrolle.

## GitHub- und Copilot-Abgrenzung

- Runtime-Fix erfolgt auf dem bestehenden Draft-PR #6, Branch
  `v9/copilot-delegation-integration` gegen `main`.
- Historischen Branch `v8/adaptive-orchestrator` nicht aendern und nichts mergen.
- Copilot-Credits aufgebraucht: keine kostenpflichtige Delegation.
- Ein normaler GitHub-Commit beweist keine Copilot-Proficiency-Aktivitaet.
- Vor anschliessendem Bug-Bounty-Einsatz: konkretes Programm und dessen Scope,
  erlaubte Testmethoden, Disclosure-Regeln und Reproduzierbarkeit pruefen.

Quellen: `CodebuffAI/freebuff` SDK-Skill-Loader und Skill-Handler; bestehende
SFS-Labs-Dokumentation und Projektdateien.
