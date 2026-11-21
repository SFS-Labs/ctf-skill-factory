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
bin/skill list --layer=L3   # Router
```

`bin/fetch` ist idempotent: vorhandene `vendor/<org>/<repo>/.fetched` werden übersprungen,
`--force` lädt neu. Fehlt der Token, werden öffentliche Quellen anonym geholt; private
(z. B. Teile von `SFS-Labs`) brauchen ihn.

## Secrets

Der GitHub-Token liegt **ausschließlich** unter `~/.config/gh-token` (chmod 600) und wird von
`bin/fetch` / `bin/install_bin` zur Laufzeit gelesen. Er ist in `.gitignore` ausgeschlossen und
steht in keiner getrackten Datei, keinem Log und keiner Commit-Message.

## Arbeitsweise (Kurzform)

Neun Schichten L0–L9 (Scope → Karte → Statik → Dynamik → Symbolik → Bytecode → Diff → Ökonomie →
Wissen → Prozess). Sieben Regeln, u. a.: zwei unabhängige Signale pro Hypothese, Beweiskraft
Counterexample > Pfad > Detektor > Muster, **Divergenz ist das Signal**, Negativraum führen.
Details: `INDEX.md`, `VERIFICATION.md`, Freebuff-Skill `ctf-skill-index`.

## Bekannte Grenzen

`cryo` (openssl-sys/libssl-dev), `diffusc` (braucht git), `daedaluzz` (Go-Toolchain) laufen hier
nicht; Docker-Skills sind Rezepte; IDA-Plugins sind Wissenskarten. Details in `VERIFICATION.md`.
