# PA revision plan (2026-08-20): external review triage, verified against the manuscript

> **2026-08-20 update:** direction confirmed — restructure to four contributions
> ("more fundamental, not more quantitative"). The three technical workstreams
> (exactness closure, feasibility frontier, prevalence inference) now live in
> `DEVELOPMENT_ROADMAP.md`; Phase 2/3 below are superseded by it. This file
> keeps the verification ledger and the framing/mechanical items.

An external editorial review (2026-08-20) assessed the submission-ready PDF
against PA's current author instructions and recent published work. Verdict:
PA potential ~8.5/10, submission readiness ~6.5–7/10; the binding constraint is
**contribution dilution** (three papers in one) plus visible seams between the
guarantee language and the empirical targets. This file records which of its
claims were verified against the repo, which were refuted, and the resulting
work plan. Companion to `REVISION_TRIAGE.md` (the 2026-07 mock-referee round).

## Verification ledger

| Review claim | Verified? | Evidence |
|---|---|---|
| `texttte30` string leaks into PDF p.22 | ✅ CONFIRMED | `sections/07_political.tex:194` had `\\texttt{e30}` — **FIXED 2026-08-20**, recompiled clean |
| Figure 4 (certified core) lands on p.32, after References (p.27) | ✅ CONFIRMED | float never flushed — **FIXED** via `\clearpage` before `\appendix` in `main.tex`; now p.26, References p.28 |
| "exact at any K" (abstract/intro/discussion) vs LOO-center O(1/K²) asymmetry "bounded only heuristically" (§4) | ✅ CONFIRMED | abstract l.46; `01_intro.tex:47`; `08_discussion.tex:8` vs `04_theory.tex:108-109` — OPEN, see item 2 |
| Companion paper shares the clustered construction, blurring Theorem 3's novelty | ✅ CONFIRMED | `09_related.tex:10` (`park2026poverty`); supplement:1245 — OPEN, see item 3 |
| No across-country familywise control on the headline country counts | ✅ CONFIRMED (and already disclosed) | `07_political.tex:186` — upgrade opportunity, see item 4 |
| Manuscript is ~8,000 words, needs a 20–25% cut | ❌ REFUTED | PDF text extraction inflates (math, heads). Per-section body count ≈5.7–5.9k; titlepage states ~5,950 vs the 6,000 cap. No cut required; trimming still buys room for item 4 |
| PDF is single-spaced, PA wants 12pt double-spaced | ❌ REFUTED | `main.tex:1,13`: `12pt` + `\doublespacing` since the PA-structure commit |
| "over-counts 2.6–6.5×" reads as an apples-to-apples Foa–Mounk replication | ⚠️ PARTIALLY ADDRESSED | §7 already decomposes: rung-only 1.7–4.8× (plug-in) / 1.9–4.8× (design-aware); abstract uses 1.9–4.8×. Remaining: audit every "over-count" phrasing, see item 7 |
| AI disclosure should split code assistance (methods section) from prose/proof revision (acknowledgments) per CUP policy | ✅ POLICY-ACCURATE | current single stub at `main.tex:88-95` — author item, see item 8 |
| Noisy-calibration related work should distinguish 2025 measurement-error conformal (Singer/Williams/Ghosh, MNRAS) | ⏳ TO CHECK | not in `refs.bib`; verify the reference exists before citing, then add to §Related |

## The one-sentence contribution (item 1 — governs everything else)

Adopt the review's framing: **uncertainty must attach to the same unit as the
substantive claim; repeated cross-national surveys violate this twice — at the
claim level (wave-pair ≠ trajectory) and at the calibration level (estimate ≠
latent).** The claim-unit problem is the first contribution; the
estimated-calibration boundary is its second manifestation. Conformal and the
design-based sup-t are then tools for two different uncertainty layers, not two
competing methods — which pre-answers the editor's "why does a conformal paper's
main application use a non-conformal procedure?"

Candidate title: *The Wrong Unit of Uncertainty: Simultaneous Inference for
Repeated Cross-National Surveys* (drop "Conformal" so §7's design-based results
are not mis-advertised). Decision: AUTHOR.

## Work items (ordered)

### Phase 0 — mechanical (DONE 2026-08-20)
- [x] Fix `\\texttt{e30}` leak (`07_political.tex:194`).
- [x] Flush Figure 4 before the back matter (`main.tex` `\clearpage`); verified
      by clean recompile: 32 pp, 0 undefined citations, fig on p.26.
- [ ] Enlarge Figure 2 axes/annotations (review: legibility on small screens).

### Phase 1 — paper identity (no new computation)
1. **Rewrite abstract + intro around the single-sentence contribution.**
   Structure: wrong unit twice → instrument for each layer → boundary result →
   substantive payoff. Keep Figure 1 as the near-first exhibit ("Figure 1 = paper").
2. **Target table.** One table early in §2: five columns
   `procedure → target → randomness → assumptions → guarantee`, four rows (PCB /
   latent PCB / deconvolution / substantive sup-t). Kills the five-page
   target-switching complaint; the T1/T2 machinery already exists in §2.
3. **Companion-paper novelty boundary.** Demote Theorem 3 to a base result
   imported from `park2026poverty`; state this paper's new results explicitly
   (non-identification, finite-K design-noise correction, safe selector
   architecture, claim-unit consequences). Add one cover-letter paragraph
   listing overlapping vs non-overlapping theorems.
4. **Selector simplification.** Main text keeps the (K,ρ) regime figure
   (Figure 2 nearly is it) + 1–2 sentences on the validation history; gate
   derivations, frozen constants, scorer-bug audit → supplement. Frees words
   for the country-count result.
5. **Terminology pass:** "response-distribution trajectory" everywhere the
   guarantee lives; "attitude trajectory" only under a stated measurement-
   invariance condition. Sell the ordinal-scale (monotone-recoding) invariance
   of the CDF object as a positive feature — currently unsold.
6. **WVS phrasing audit** (finish the partially-done reframe): every
   "over-count" sentence becomes "applying a trajectory-persistence criterion
   to the same battery"; keep the 1.9–4.8× decomposition. Ground the ×1.5/×2
   variance multipliers in the empirical design-effect distribution observed
   in ESS/LAPOP (computable from shipped results; if not, microdata item).

### Phase 2 — close the exactness seam (code + possible rerun)
7. **Either** rerun all headline results with a split-fold/symmetric center and
   claim exactness cleanly, **or** downgrade "exact at any K" to the estimated-
   trajectory statement Theorem 3 actually licenses. Inventory first: which of
   e13/e26/e36/e50 pass through the LOO center (`pcb/inference/`), what moves
   under split-fold on simulation, then decide. The abstract/intro/discussion
   language and §4's admission must end up consistent either way.

### Phase 3 — the new methodological result (highest upside)
8. **Simultaneous lower confidence bound on the number of true country-level
   discoveries** (Goeman–Solari closed testing / Katsevich–Ramdas style, both
   already cited at `07_political.tex:41`). Target statement: "with 90%
   confidence, at least m of the 33 countries satisfy net decline." Completes
   the wrong-unit ladder: threshold → wave → trajectory → country family.
   Plan: per-country certification p-values (or e-values) from the existing
   band machinery → closed-testing lower bound; simulation contract test; one
   paragraph + one number in §7. New experiment id: e56.

### Phase 4 — author-only / microdata (unchanged from HANDOFF §A–B)
9. AI disclosure: split per CUP policy — code/data-analysis assistance described
   in the methods/replication text, prose+proof revision in Acknowledgments
   (replaces the `main.tex:89` stub). AUTHOR.
10. Cover letter: masthead check, add the novelty-boundary paragraph (item 3),
    delete the draft note. AUTHOR.
11. Microdata reruns (HANDOFF B5–B9) once licensed files are placed per
    `DATA_SOURCES.md`.

## Anticipated referee questions the revision must pre-answer

- *Method:* estimated vs latent targets in one table (item 2 → Phase 1.2); the
  centering exactness closed (Phase 2).
- *Political methodology:* country counts get a simultaneous true-discovery
  bound (Phase 3).
- *Survey:* sampling ≠ measurement invariance; response-distribution language
  (Phase 1.5).
- *Editor:* novelty vs companion paper stated in manuscript + cover letter
  (Phase 1.3); conformal/sup-t division of labour stated up front (Phase 1.1).

## Build note

The paper now compiles in this environment: `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-science` (algorithm2e), `texlive-bibtex-extra`
(chicago.bst); `pdflatex → bibtex → pdflatex ×2`.
