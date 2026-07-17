# Mock-referee triage (2026-07-17): three reports, disposition of every major point

Three simulated PA referees (conformal theorist R1; survey methodologist R2;
comparative politics R3). All three: **major revision**. Every major point
verified against artifacts before acting. Status: DONE (this branch) /
MICRODATA (requires licensed data; flagged in paper text) / REJECTED (with
reason).

## Convergent points (2+ referees)

| Point | Verified? | Status |
|---|---|---|
| Greece n_pairs=1: persistent rung degenerates to one pair (R2,R3) | ✅ CSV | DONE — disclosed in §8, net rung co-headlined, abstract reframed |
| Power/severity of the persistent rung never shown (R1,R3) | ✅ e32 | DONE — e32: 80% power needs 0.06–0.08 CDF pts/pair; falls with more pairs; net rung 0.02–0.03. Real-data injection: MICRODATA |
| Unreachability is procedure-relative (R1,R2) | ✅ | DONE — scoped to deployed procedure in abstract/intro; calibration-free floor separated |
| WVS K=59–77 vs K≈100 inconsistency (R1,R2) | ✅ CSV | DONE — probe (full sets) vs certification (≥2-wave) denominators separated everywhere |
| Holdout not a valid confirmation of final pipeline (R1,R2) | ✅ | DONE — three-layer validation story + e33 fresh seal (6 unseen families, 120/120, seal-1 generator bug disclosed) |
| Exchangeability discussion decorative (R1,R2) | ✅ | DONE — superpopulation framing; "weaker than iid" deleted; Barber bound demoted to qualitative; LORO audit: MICRODATA |
| Measurement invariance / mode switches unaddressed (R2,R3) | ✅ | DONE — scope condition in Limitations + §8 confound paragraph; per-pair mode audit: MICRODATA |

## R3 (comparative politics)

- M4 Canada/Sweden contradict certified-core claim — ✅ verified in CSV → DONE (text corrected, figure caption fixed)
- M10 top rung ≠ "what casual readings assert" → DONE (reframed; net co-headline)
- M7 Claassen + disillusionment literature → DONE (related work §, 5 new refs); same-data comparison: future work, noted
- M8 regime-type stratification → PARTIAL (autocracy/deconsolidation conceptual split in text; V-Dem cross-tab: future)
- M5 FI/CH within-program audit → MICRODATA (demoted to flagged finding meanwhile)
- M2 within-country sup-t competitor → RESOLVED BY REFRAMING (R2 showed the certification instrument IS the within-country design sup-t; instrument-attribution paragraph added)
- m5 "5977" PDF mangling → REJECTED (en-dashes correct in source; PDF text-extraction artifact)

## R1 (conformal theory)

- Nested lemma prior art (Gupta et al. 2022; Yang & Kuchibhotla) → DONE (cited, novelty claim withdrawn, positioned as architecture)
- Th1(ii) randomization/discreteness gap → DONE (restated)
- Th2(b) O(ρ) unproven → DONE (ρ^{2/3} / ρ·log under sub-Gaussian; independence use stated)
- Th4′ (A1) hidden correlation-profile requirement + "not removable" non sequitur → DONE
- α_dec formula mismatch → DONE (unified with α/2 cap)
- M2 latent-gap sensitivity via inflated band on real data → MICRODATA (tool exists: Th2(b) inflated form; flagged)
- m18 jargon/rewrite for outside readers → PARTIAL (worst offenders fixed; full de-jargonization is an editing pass for the author)

## R2 (survey methodology)

- 2.1 instrument conflation (certification ≠ conformal) — ✅ verified in code → DONE (attribution paragraph; abstract adjusted)
- 2.2 m-of-m bootstrap bias → DONE in code (`psu_bootstrap(rescale=True)`) + direction disclosed in text; rerun of shipped CSVs: MICRODATA
- 2.3 ESS SDDF misstatement → DONE (corrected; window = extract choice)
- 2.4 WVS deff sensitivity → MICRODATA (direction stated in text: counts inflate, ratio is lower bound)
- 2.9 LAPOP semisynthetic saturation = estimator collapse — ✅ verified arithmetic → DONE (reframed in §6/S4; rescaled rerun: MICRODATA)
- M8 WVS across-country FWER → DONE as caveat (expected false certifications noted; full FDR/Bonferroni rerun: MICRODATA)
- 4.x pcb.data module absent; mis-shipped docs (DATA_SOURCES/REPRODUCIBILITY from companion project) → **OPEN — author action required**: ship loaders + survey-specific docs before submission
- m13 window label 2018–2022 → DONE (rounds 9–11, 2018–2024)

## Still open for the author (cannot be done without microdata/author input)

1. Ship `pcb/data/` loaders + rewrite DATA_SOURCES.md / REPRODUCIBILITY.md for the surveys (R2 hard requirement).
2. Rescaled-bootstrap rerun of all real-data CSVs; deff sensitivity for WVS; mode/fieldwork audit; SDDF-extended ESS window; FI/CH within-program audit; real-data severity injection; LORO exchangeability audit.
3. Optional: Claassen same-data comparison; V-Dem regime cross-tab; full de-jargon editing pass.
