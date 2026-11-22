# AGENTS.md - SFS-Labs Arbeitsregeln

## GitHub-Entwicklungsaufgaben

Bei jeder Aufgabe, die GitHub, ein SFS-Labs-Repository, Code, PRs, Issues, CI,
Reviews oder Dokumentation betrifft - auch wenn GitHub nicht ausdruecklich genannt
wird - gilt automatisch:

1. **Standard laden.** `docs/COPILOT_PROFICIENCY_OPERATING_STANDARD.md`
   (verbatim) und `docs/COPILOT-PROFICIENCY-STANDARD.md` (lokale
   Betriebsergaenzung) lesen. Der Code versucht den Remote-Abruf und nutzt sonst
   die hashgepruefte vendorte Fassung; der PAT-Status wird separat
   ausgewiesen.
2. **Preflight.** `python3 bin/copilot-delegate.py preflight --repo <owner/repo>`
   ausfuehren. Nur Lesezugriffe. Ergebnis und Blocker beachten.
3. **Teilaufgabe pruefen.** `detect` nur fuer klar abgegrenzte, unabhaengig
   pruefbare Aufgaben mit Ziel, Pfaden, Abnahme und Tests. Keine kuenstlichen
   Aufgaben zur Proficiency-Steigerung.
4. **Gate respektieren.** Delegation nur bei verfuegbarer Route **und** offenem
   Kontingent-Gate (`paid_delegation_allowed=true`, `credits_exhausted=false`,
   `--execute --allow-paid`). Sonst selbst weiterarbeiten.
5. **Nicht delegieren:** Secrets, Deployments, Publikationen, Live-Transaktionen,
   Infrastruktur-/Desktop-Einstellungen, Auto-Merge, Force-Push,
   Repo-Administration.
6. **Ergebnis pruefen.** PR, exakten Head-SHA, CI und Diff lesen; Scope,
   Secret-Scan und Reviewergebnis pruefen. Fehler selbst beheben oder gezielt
   nachfordern. Kein Merge, keine Veroeffentlichung ohne menschliche Freigabe.
7. **Evidenz.** Nur beobachtete Copilot-Aktivitaet zaehlt. Ein Assignment ist
   kein Nachweis; Simulationen werden ausgeschlossen. Keine Aussage ueber ein
   GitHub-Proficiency-Level.

Freebuff bleibt die einzige Benutzeroberflaeche und der fuehrende Orchestrator.
Copilot ist ein optionaler Executor. Wenn Copilot nicht verfuegbar ist, wird die
Aufgabe ohne Copilot-Behauptung fortgefuehrt.

## Verifikation

- Vor Erfolgsmeldungen die betroffenen Tests und den Build ausfuehren.
- Simulationen und echte Laeufe getrennt kennzeichnen.
- Blockierte Pruefungen als blockiert melden, nie als bestanden.
