# Verifikation — echte Laeufe (Stand 2026-11-21)

Ziel: `corpora/verify/Vulnerable.sol` — Vault mit Reentrancy, `tx.origin`-Sweep und unchecked Low-Level-Call.
Kein `--help`-Test, sondern Findings an einem Programm mit bekannten Fehlern.

| Layer | Werkzeug | Ergebnis |
|---|---|---|
| L1 | `solc-select` / `crytic-compile` | solc **0.8.28** gepinnt, AST/ABI gebaut |
| L1 | `surya` | Contract-Map erzeugt (deposit, withdraw, sweep, forceSend) |
| L2 | `slither` | `reentrancy-eth` in `Vault.withdraw()` + Arbitrary-Send in `Vault.sweep()` |
| L4 | `mythril` | SWC-115 *Dependence on tx.origin* in `Vault` |
| L3 | `echidna` | Counterexample: `deposit → sweep` bricht `echidna_solvent` (Reason `ReturnFalse`) |
| L3 | `medusa` | 36.995 Calls, Coverage-Report erzeugt — flaggt die Invariante **nicht** |
| PoC | `forge` | 3/3 Tests grün: Invariante hält anfangs, Sweep bricht sie, Reentrancy drainiert den Vault |

## Divergenz-Befund (Emergenz-Regel 3)

Echidna findet den Bruch, Medusa nicht — bei identischer Quelle und identischen Sendern.
Damit ist belegt, warum ein einzelnes Tool kein „sauber" liefern darf: Medusa allein hätte hier
einen Fehlalarm-negativen Befund produziert. Die Regel „zwei Signale aus verschiedenen Schichten"
ist damit empirisch, nicht nur behauptet.

## Was zusätzlich nachgewiesen wurde

- `forge test` läuft ohne forge-std (eigene `Vm`-Interface-Deklaration für `prank(sender, origin)`).
- Reentrancy-Test korrigiert: die Solvenz-Invariante bleibt scheinbar wahr, weil `totalDeposits`
  mit sinkt — der Diebstahl zeigt sich nur am Guthaben (`balance <= 1 ether`). Genau diese
  Falle ist der Grund, warum Counterexample + PoC zusammen geprüft werden müssen.
- `exploitdb`: GitHub-Repo ist **archiviert und geleert** (nur noch README); Daten kommen vom
  offiziellen Nachfolger `gitlab.com/exploit-database/exploitdb` — 10,2 MB Exploit-CSV + 220 KB Shellcodes.

## Grenzen (ehrlich, nicht behoben)

| Skill | Grund |
|---|---|
| `cryo` | `openssl-sys` braucht `libssl-dev` (Root); kein Release-Asset vorhanden |
| `diffusc` | hängt an einem git-Fork von slither; `git` fehlt, Elevation nicht bestätigt |
| `daedaluzz` | ist **Go** (nicht Python); keine Go-Toolchain installiert |
| `attacknet`, `eth-security-toolbox`, `cloudexec`, `paradigm-ctf-infra` | brauchen Docker; Rezepte liegen in `recipes/` |
| `ida-evm`, `ethersplay` | IDA nicht installiert; Bytecode-Schicht läuft über `etheno`/`evmasm`/`evm-cfg-builder` |
| Repo-Versionierung | kein `git` → Updates über `python3 bin/fetch` (authentifizierte Tarballs) |
