# ctf-skill-factory

Die **Skill-Fabrik**: 133 Security-Skills (EVM/Solidity, Solana, Move, Cairo, Bytecode, MEV, Audit-Wissen)
als abrufbares, komponierbares System — nicht als loses Repo-Verzeichnis. Geholt wurden 134 Quellen;
`NethermindEth/EVMYulLean` hat denselben Baum wie `paradigmxyz/evmyullean` und liegt deshalb nur
als Alias vor. Der Beweis steht gepinnt in `repos.tsv` (`tree_sha256`, `files`) und wird von
`bin/doctor` bei jedem Lauf sowie von `bin/alias-check` gegen den Remote nachgerechnet.

Home auf dem Arbeitsrechner: `~/ctf-skills/`. Dieses Repo versioniert die **Fabrik selbst**:
Rezepte, Wissenskarten, Router, Manifeste und den Verifikationsnachweis. Die schweren Anteile
(Quellbäume, venvs, Binaries) liegen bewusst **nicht** im Repo.

## Was drin ist

| Pfad | Inhalt |
|---|---|
| `bin/fetch` | holt alle Repos als Tarball nach `vendor/` (authentifiziert, idempotent) |
| `bin/install_bin` | installiert Release-Binaries (echidna, medusa, rbuilder, …) |
| `bin/gen_skills` | erzeugt `knowledge/*/SKILL.md`, `MANIFEST.yaml`, `manifest.json`, `INDEX.md` |
| `bin/doctor` | misst alle 51 Werkzeug-Einträge, 133 Vendor-Bäume, 133 Karten, die Alias-Beweise und die Wrapper; schreibt `STATUS.md` + Befund-Block in `INDEX.md`, Exit 1 bei jeder Lücke |
| `bin/alias-check` | rechnet jeden Alias-Beweis lokal gegen `vendor/` und anonym gegen den Remote; `--update` pinnt den Digest nach erfolgreichem Vergleich neu |
| `bin/tool_matrix.py` | eine Klassifikation für beide Seiten: `PROBE` (Binary muss antworten), `LIB` (Bibliothek), `REF` (nur Referenz, mit Grund) — `doctor` misst danach, `gen_skills` schreibt danach die Karte |
| `bin/token` | nimmt den GitHub-Token unsichtbar an (kein `--token`, kein Echo), legt ihn 0600 nach `~/.config/gh-token` und prüft per `--check` |
| `bin/skill` | Router: `list`, `show`, `find`, `plan` |
| `bin/push` | sichert den Stand im privaten Repo: Token nur aus `GH_TOKEN`/`GITHUB_TOKEN`, Ausgabe redigiert |
| `bin/smoke` | wiederholt die drei Beweisläufe (cryo/diffusc/daedaluzz) plus den Redaktions-Selbsttest von `bin/push` und schreibt das Ergebnis nach `STATUS.md` |
| `knowledge/<slug>/SKILL.md` | 133 Karten: Zweck, wann, Kommando, Deutung, blinde Flecken, Kombination (pairs_with); Nicht-Lauffähiges trägt oben ein `Referenzkarte`-/`Bibliothek`-Banner mit Grund |
| `MANIFEST.yaml` / `manifest.json` | Quelle der Wahrheit (Slug, Layer, Trigger, Pairs, Blinds) plus `status`/`status_reason` je Eintrag (`binary`, `bibliothek`, `referenz`, `wissen`, `korpus`, `quelle`) |
| `INDEX.md` | generierter Index nach Schichten L0–L9 |
| `STATUS.md` | was auf der Maschine wirklich läuft (Wahrheit statt Annahme) |
| `VERIFICATION.md` | Nachweis an echten Findings (Slither/Echidna/Mythril/Forge) |
| `skill/` | die effektive Definition des Freebuff-Skills `ctf-skill-index` (versioniert) plus Sicherung der Vorgaenger-Version; geladen wird der Account-Skill, **nicht** diese Datei |
| `recipes/` | Rezepte: Docker-Skills (hier nicht lauffähig) und `slither-vendor.sh` (End-to-End gegen einen geholten Skill) |
| `corpora/` | CTF-/PoC-Korpora inkl. `corpora/verify` (Vulnerable.sol + forge-Tests) |
| `repos.tsv` | Liste aller 134 Quellen (slug · repo · Klasse · Layer · Rolle); `alias_of=<slug>; tree_sha256=<digest>; files=<n>` in Spalte 6 belegt einen Alias, der nicht als zweiter Klon geholt wird |

## Was bewusst FEHLT (und warum)

- `vendor/` (~8,6 GB, 133 Quellbäume aus 134 Quellen) — zu groß für Git, jederzeit reproduzierbar.
- `venvs/`, `tools/`, `logs/` — maschinenlokal, kein versionierbarer Inhalt.
- Forge-/crytic-Artefakte (`out/`, `cache/`, `crytic-export/`).

## Wiederherstellung eines vollständigen Stands

```bash
# 1. Fabrik klonen
git clone https://github.com/SFS-Labs/ctf-skill-factory.git ~/ctf-skills
cd ~/ctf-skills

# 2. Werkzeuge (ohne Root)
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -L https://foundry.paradigm.xyz | bash
uv tool install slither-analyzer crytic-compile solc-select pyevmasm evm-cfg-builder
uv tool install --force mythril --with 'setuptools<81'   # pkg_resources (setuptools>=81 hat es entfernt)
uv tool install --force --python 3.10 --with 'setuptools<81' etheno      # pysha3 baut auf 3.12 nicht
uv tool install --force --python 3.9  --with 'setuptools<81' legions     # nubia nutzt find_module
uv tool install --force --with 'setuptools<81' --with sqlalchemy --with psycopg2-binary \
  ./vendor/flashbots/mev-inspect-py                                      # 2021er Code, py3.10
npm install -g surya solhint eth-scribble
python3 bin/install_bin crytic/echidna x86_64-linux tar

# 3. Quellbaeume zurueckholen (134 Quellen -> 133 Baeume; Alias-Zeilen brauchen keinen Klon)
export GITHUB_TOKEN=$(cat ~/.config/gh-token)   # optional, nur fuer private Quellen
python3 bin/fetch

# 4. Pruefen
bin/alias-check             # Alias-Beweis lokal + gegen den Remote
python3 bin/doctor          # Status der Binaries und der Alias-Pins
bin/smoke                   # echte Beweislaeufe, Ergebnis landet in STATUS.md
bin/skill list --layer=L3   # Router
```

`bin/fetch` ist idempotent: vorhandene `vendor/<org>/<repo>/.fetched` werden übersprungen,
`--force` lädt neu. Fehlt der Token, werden öffentliche Quellen anonym geholt; private
(z. B. Teile von `SFS-Labs`) brauchen ihn.

## Secrets

Der GitHub-Token liegt **ausschließlich** unter `~/.config/gh-token` (chmod 600) und wird von
`bin/fetch` / `bin/install_bin` zur Laufzeit gelesen. Er ist in `.gitignore` ausgeschlossen und
steht in keiner getrackten Datei, keinem Log und keiner Commit-Message.

`bin/push` ist strenger: es liest den Token **nicht** aus der Datei, sondern nur aus `GH_TOKEN`
bzw. `GITHUB_TOKEN` der Umgebung, legt ihn nie in `argv` (sonst via `ps` sichtbar) und schickt jede
Ausgabe — auch die stderr des Push-Workers — durch einen Redactor. `bin/push --selftest` prüft
das gegen synthetische Lecks.

### Token eingeben — der einzige sichere Weg

Nicht in den Chat, nicht in die Freebuff-Terminalpane, nicht als Argument und nicht in ein
Skript. Sondern in einem eigenen Terminalfenster der Sitzung (Ctrl+Alt+T):

```
ctf-token
```

Erst wenn `Token einfuegen (unsichtbar), dann Enter:` steht, den Token einfügen und Enter
drücken. Gemessen (PTY-Test): eine Eingabe, die **vor** dem Prompt ankommt, wird vom TTY noch
gespiegelt und steht im Scrollback; nach dem Prompt bleibt sie unsichtbar. Danach zeigt
`ctf-token --show` nur Klasse und letzte vier Zeichen, `bin/push --check` prüft den Token
read-only gegen GitHub, und jede weitere Nutzung läuft ohne erneute Eingabe über
`export GH_TOKEN=$(cat ~/.config/gh-token)`.

## Arbeitsweise (Kurzform)

Zehn Schichten L0–L9 (Scope → Karte → Statik → Dynamik → Symbolik → Bytecode → Diff → Ökonomie →
Wissen → Prozess). Sieben Regeln, u. a.: zwei unabhängige Signale bestätigen eine Hypothese,
sind aber keine Explorationsbedingung; Beweiskraft Counterexample > Pfad > Detektor > Muster;
**Divergenz ist das Signal**; Negativraum führen.
Details: `INDEX.md`, `VERIFICATION.md`, Freebuff-Skill `ctf-skill-index`.

## Nachgezogene Werkzeuge (2026-11-21)

Alle drei ehemals offenen Werkzeuge laufen jetzt ohne Root:

| Werkzeug | Zustand | Rezept |
|---|---|---|
| `cryo` | laeuft (Selbstbau; Releases-API hat kein Asset) | `recipes/cryo-build.sh` |
| `diffusc` | laeuft (kein git noetig; Slither-Fork als Tarball + 2 Patches) | `recipes/diffusc-setup.sh` |
| `daedaluzz` | laeuft (ist Go, nicht Python; Userspace-Go 1.23.4) | `recipes/daedaluzz-build.sh` |

Beweis-Laeufe und die genauen Ursachen stehen in `VERIFICATION.md`.

## Bekannte Grenzen

Docker-Skills (`attacknet`, `eth-security-toolbox`, `cloudexec`, `paradigm-ctf-infra`) sind Rezepte,
IDA-Plugins (`ida-evm`, `ethersplay`) Wissenskarten — beides Plan-Entscheidung, keine Baustelle.
Systemweit fehlt `git`; committet/gepusht wird ueber `dulwich`.

Zehn Release-Binaries haben kein vorgebautes Linux-Artefakt (gemessen per Release-API) und
bleiben Referenz, bis jemand `cargo build`/`go build` im `vendor/`-Baum fährt; die genauen
Gründe je Slug stehen in `STATUS.md`. Der hinterlegte GitHub-Token ist seit dem 2026-11-22
wieder **lesbar (200)**, aber als Fine-grained-Token begrenzt: Issues-API und
Agent-Tasks-Repo antworten mit **403**. Für die Copilot-Delegation sind damit beide
Schreibpfade zu; private Quellen bleiben lesbar.

## V8 — ausfuehrender Orchestrator (2026-11-22)

V7 bleibt unveraendert. Neu ist `bin/skill-orchestrator.py`: Auswahl aus dem echten Katalog,
ausfuehrbarer Graph, echte Werkzeugaufrufe, inhaltliche Evidenzpruefung und adaptive Recovery.

```bash
python3 bin/skill-orchestrator.py route  --task "<Aufgabe>"          # Kandidaten + DAG, keine Ausfuehrung
python3 bin/skill-orchestrator.py plan   --task "<Aufgabe>" --target <datei.sol> [--project <dir>]
python3 bin/skill-orchestrator.py run    --task "<Aufgabe>" --target <datei.sol> \
        --project <dir> --out <evidenz> --allow-exec                  # echte Adapter, Receipts
python3 bin/skill-orchestrator.py verify --report <evidenz>/evidence-report.json
python3 bin/skill-orchestrator.py selfcheck                          # Katalog + Adapter + Negativproben
python3 bin/compare-v7-v8                                            # reproduzierbarer V7/V8-Vergleich
python3 -m unittest discover -s tests                                # 84 Tests (49 V8 + 35 V9)
```

Zustaende: `DISCOVERED · SELECTED · READY · INVOKED · COMPLETED · FAILED · UNAVAILABLE ·
VERIFIED · BLOCKED` (+ `KNOWLEDGE_ONLY`). Erfolg ist der Adaptervertrag, nicht die Zahl 0:
`slither` 255 und `echidna` 1 sind Befunde. Ein Hash beweist Integritaet, nicht Wahrheit;
`verify` prueft Assertion im Testrumpf, Negativkontrolle und State-Delta.

Nachweise, Messwerte und Blocker: `docs/V8-REPORT.md`. Rueckfall: `docs/ROLLBACK.md`.

## V9 — Copilot-Delegation (2026-11-22, lokal getestet)

Freebuff bleibt die einzige Oberflaeche und der fuehrende Orchestrator. `bin/copilot-delegate.py`
delegiert klar abgegrenzte Teilaufgaben ueber die GitHub-Issue-API an
`copilot-swe-agent[bot]` oder - falls berechtigt - ueber die Agent Tasks API, beobachtet
Task, Branch, PR und CI und prueft den Diff unabhaengig. Der Einstieg laeuft auch ueber
`bin/skill-orchestrator.py copilot ...`; `AGENTS.md` triggert die Pruefung automatisch.

```bash
python3 bin/copilot-delegate.py preflight                 # nur Lesen, keine Kosten
python3 bin/copilot-delegate.py detect --task "..." --path src/foo.py --out brief.json
python3 bin/copilot-delegate.py delegate --brief brief.json          # dry-run, kein Schreibzugriff
python3 bin/copilot-delegate.py watch --id <id> --follow
python3 bin/copilot-delegate.py review --id <id>
python3 bin/copilot-delegate.py proficiency --markdown
python3 bin/copilot-delegate.py selftest                  # 8 Mock-Szenarien, 0 EUR
```

**Status:** lokal getestet, **keine echte Copilot-Delegation**. Der Preflight vom 2026-11-22
zeigt: Auth und Copilot-Actor sind vorhanden, aber `ctf-skill-factory` hat Issues deaktiviert,
die Issues-API liefert 403, die Agent-Tasks-Repo-API 403, und die Credits sind aufgebraucht.
Das kostenpflichtige Gate ist standardmaessig geschlossen (`paid_delegation_allowed=false`,
`credits_exhausted=true`); ohne `policy`-Freigabe **und** `--allow-paid` wird nichts gesendet.
Kein Auto-Merge, keine Veroeffentlichung. Details und Evidenz:
`docs/COPILOT-DELEGATION.md`, Standard: `docs/COPILOT_PROFICIENCY_OPERATING_STANDARD.md`
(verbatim) plus `docs/COPILOT-PROFICIENCY-STANDARD.md` (lokale Ergaenzung).
