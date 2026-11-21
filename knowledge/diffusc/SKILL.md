---
name: diffusc
kind: tool
class: RS
layer: L6
repo: crytic/diffusc
install: "release-binary"
triggers: [diffusc, differential, fuzzing, upgradeable, smart, contract, implementations, setup, running, command, line, arguments]
pairs_with: [oz-upgrades, chainsecurity-deployment-validation, bytecode-verifier, cryo, mev-inspect-py, transaction-decoder, rbuilder]
---

# diffusc — Diff-Fuzzing alter vs. neuer Stand

**Repo:** `crytic/diffusc` · **Layer:** L6 · **Klasse:** RS · **Bezogen:** ja (branch `main`, Lizenz AGPL-3.0)

## Zweck
Diff-Fuzzing alter vs. neuer Stand.

## Wann anwenden
wenn sich Code/Parameter geaendert haben (Upgrade, Deployment, Fork).

## Kommando
`diffusc --help` (Release-Binary in ~/.local/bin, falls vorhanden)

## Deutung der Ausgabe
Counterexample = harter Beweis. Sauberer Lauf = nur so gut wie die formulierte Invariante.

## Blinde Flecken
- schnelle Breite, aber ohne Invarianten findet der Fuzzer nichts.
- findet keine Altlasten, die schon immer da waren.

## Kombination
Zusammen mit: `oz-upgrades`, `chainsecurity-deployment-validation`, `bytecode-verifier`, `cryo`, `mev-inspect-py`, `transaction-decoder`, `rbuilder`.
Nach diesem Skill weiter mit Layer L7.
