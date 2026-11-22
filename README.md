# ctf-skill-factory

Die **Skill-Fabrik**: 134 Security-Skills (EVM/Solidity, Solana, Move, Cairo, Bytecode, MEV, Audit-Wissen)
als abrufbares, komponierbares System — nicht als loses Repo-Verzeichnis.

Home auf dem Arbeitsrechner: `~/ctf-skills/`. Dieses Repo versioniert die **Fabrik selbst**:
Rezepte, Wissenskarten, Router, Manifeste und den Verifikationsnachweis. Die schweren Anteile
(Quellbäume, venvs, Binaries) liegen bewusst **nicht** im Repo.

## Was drin ist

| Pfad | Inhalt |
|---|---|
| `bin/fetch` | holt alle Repos als Tarball nach `vendor/` (authentifiziert, idempotent) |
| `bin/install_bin` | installiert Release-Binaries (echidna, medusa, rbuilder, …) |
| `bin/gen_skills` | erzeugt `knowledge/*/SKILL.md`, `MANIFEST.yaml`, `manifest.json`, `INDEX.md` |
| `bin/doctor` | prüft jedes Binary, schreibt `STATUS.md` |
| `bin/skill` | Router: `list`, `show`, `find`, `plan` |
| `bin/push` | sichert den Stand im privaten Repo: Token nur aus `GH_TOKEN`/`GITHUB_TOKEN`, Ausgabe redigiert |
| `bin/smoke` | wiederholt die drei Beweisläufe (cryo/diffusc/daedaluzz) plus den Redaktions-Selbsttest von `bin/push` und schreibt das Ergebnis nach `STATUS.md` |
| `knowledge/<slug>/SKILL.md` | 134 Karten: Zweck, wann, Kommando, Deutung, blinde Flecken, Kombination |
| `MANIFEST.yaml` / `manifest.json` | Quelle der Wahrheit (Slug, Layer, Trigger, Pairs, Blinds) |
| `INDEX.md` | generierter Index nach Schichten L0–L9 |
| `STATUS.md` | was auf der Maschine wirklich läuft (Wahrheit statt Annahme) |
| `VERIFICATION.md` | Nachweis an echten Findings (Slither/Echidna/Mythril/Forge) |
| `recipes/` | Rezepte für Docker-Skills, die hier nicht laufen |
| `corpora/` | CTF-/PoC-Korpora inkl. `corpora/verify` (Vulnerable.sol + forge-Tests) |
| `repos.tsv` | Liste aller 134 Quellen (slug · repo · Klasse · Layer · Rolle) |

## Was bewusst FEHLT (und warum)

- `vendor/` (~8,6 GB, 134 Quellbäume) — zu groß für Git, jederzeit reproduzierbar.
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
uv tool install --force mythril --with 'setuptools<81'   # pkg_resources
npm install -g surya solhint eth-scribble
python3 bin/install_bin crytic/echidna x86_64-linux tar

# 3. Quellbäume zurueckholen (134 Repos, ~8,6 GB)
export GITHUB_TOKEN=$(cat ~/.config/gh-token)   # optional, nur fuer private Quellen
python3 bin/fetch

# 4. Pruefen
python3 bin/doctor          # Status der Binaries
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

## Arbeitsweise (Kurzform)

Neun Schichten L0–L9 (Scope → Karte → Statik → Dynamik → Symbolik → Bytecode → Diff → Ökonomie →
Wissen → Prozess). Sieben Regeln, u. a.: zwei unabhängige Signale pro Hypothese, Beweiskraft
Counterexample > Pfad > Detektor > Muster, **Divergenz ist das Signal**, Negativraum führen.
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
python3 -m unittest discover -s tests                                # 49 Tests
```

Zustaende: `DISCOVERED · SELECTED · READY · INVOKED · COMPLETED · FAILED · UNAVAILABLE ·
VERIFIED · BLOCKED` (+ `KNOWLEDGE_ONLY`). Erfolg ist der Adaptervertrag, nicht die Zahl 0:
`slither` 255 und `echidna` 1 sind Befunde. Ein Hash beweist Integritaet, nicht Wahrheit;
`verify` prueft Assertion im Testrumpf, Negativkontrolle und State-Delta.

Nachweise, Messwerte und Blocker: `docs/V8-REPORT.md`. Rueckfall: `docs/ROLLBACK.md`.
