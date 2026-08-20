# Handoff — where this manuscript stands and what remains

> **2026-08-20 status note (supersedes the item lists below where they
> conflict).** This document is historical; the live state is
> DEVELOPMENT_ROADMAP.md + PA_COMPLIANCE.md. Since 2026-07-27: everything
> merged to `main`; 110 tests; the LOO-validity proposition and the
> LOO-centered deconvolution proposition close the theorem↔deployment seams
> (K/(K−1) inflation is the shipped default); prevalence d=6 landed on real
> data; the AI disclosure below (item 3) is now WRITTEN in main.tex (both
> halves) — author reviews wording at read-through. Remaining author items
> are the four listed in PA_COMPLIANCE.md.

Last updated: 2026-07-27. Branch: `repair/theorem-code-validation` (not yet merged
to `main`, by design — merge once the remaining author items below are done).

> **2026-07-27 session update.** Items A1 and A2 are DONE: the `pcb/data` loaders
> are restored (root cause: an unanchored `data/` .gitignore pattern silently
> excluded them) and DATA_SOURCES/REPRODUCIBILITY now describe THIS project with
> checksums; e13 (ESS) and e26 (WVS) verified to reproduce the committed CSVs
> bit-identically from the licensed microdata; LAPOP CSVs refreshed from current
> code (11/1,119 booleans moved, no claim affected). The theory section was
> restated to carry the T1/T2 target distinction on its face (plus Thm 1(ii),
> Thm 4' A3/rates, calibrated-bound labeling, LOO disclosure). New experiments:
> **e34** per-country WVS flags, **e35** V-Dem cross-tabs (regime refinement in
> §7; predictive null in supplement), **e36 the long window** (rounds 1–11:
> persistence 0/34, net erosion 9, Israel/Italy pairwise-invisible — now the
> abstract/intro co-headline), **e37** Claassen comparison (core not recoverable
> from the pooled latent panel). Supplement bibliography restored (citations were
> rendering as '?'). Word budget: 5,894 body + 114 captions. Items A3 (AI
> disclosure: author will write), B5–B9 (rescaled bootstrap, deff sensitivity,
> mode audit, severity injection, LORO), and the SDDF design-file merge for
> rounds 1–8 remain open.

## Current state (one paragraph)

Theory, code–theory consistency, validation, framing, and PA formatting are at
submission quality. Six theorems + two lemmas are fully proved (no sketches; the one
open item, AW-4, is labeled a conjecture). 57 contract tests pass; the deployed
pipeline was given a fresh sealed validation (E33) after the original holdout was
disclosed as compromised. The manuscript fits PA's Article limit (5,798 words body,
abstract 198). Three mock referee reports (conformal theorist, survey methodologist,
comparative-politics scholar) were synthesized and every actionable point applied;
`docs/REVISION_TRIAGE.md` records the disposition of each. Self-assessment: **~8.5–8.8
as it stands; ~9.0–9.3 once the author-only items below are done**. The single axis
holding it back is real-data reproducibility (the `pcb/data` loaders are absent), and
the single axis with the most upside is the political-science payoff (currently ~6.5).

## A. Author-only items that GATE submission (must do before merge)

These require the licensed microdata and/or author decisions; they cannot be done in
this environment.

1. **Restore the `pcb/data/` loader module.** Every real-data experiment
   (e7–e18, e23, e24, e26) imports `pcb.data.audit_ess/audit_lapop/audit_wvs/
   ess_panel`; none is in the repo. Without them a licensed user cannot reproduce any
   real-data result. This is survey-referee (R2) hard requirement #1. The loaders
   encode the variable recodes, missing-code handling, weight construction
   (`anweight` with `pspwght` fallback), PSU/stratum harmonization, the core-sample
   filter, and the 2021-LAPOP exclusion — code is authoritative and must ship.
2. **Rewrite `docs/DATA_SOURCES.md` and `docs/REPRODUCIBILITY.md`.** They currently
   describe a different (companion) project — World Bank PIP, DrivenData, a Makefile
   that does not exist. Replace with survey-specific retrieval steps, exact file
   editions (ESS integrated file per round; `Trends_VS_1981_2022_Stata_v4_1.dta`;
   LAPOP Grand Merge version), and checksums of the licensed inputs.
3. **Write the AI-use disclosure.** `paper/main.tex` Acknowledgments currently holds
   a stub with a `% NOTE (author to complete...)` comment. Fill per CUP's
   generative-AI policy (tool, version, dates, access interface, scope).
4. **Fill the title page** (`paper/titlepage.tex`) — author, affiliation, ORCID,
   funding statement — and confirm the Competing Interests line in `main.tex`.

## B. Real-data reruns flagged IN THE TEXT (raise reproducibility 6.5 → 9.0)

Each is already promised in the manuscript as "flagged for the archived replication."
The code hooks exist; only the microdata is missing.

5. **Rescaled-bootstrap rerun.** `pcb.inference.design_aware.psu_bootstrap(rescale=
   True)` (Rao–Wu–Yue) already ships. Regenerate every real-data CSV in `results/`
   with it; report how ρ̂ and the certified counts move (both directions are
   disclosed in §6/§7/§8 as pending).
6. **WVS design-effect sensitivity.** Rerun the WVS certification with bootstrap
   variance × {1.5, 2.0}; report how the per-item counts, the 2.6–6.5× ratio, and the
   13-country core change. Promised in §7.
7. **ESS mode/fieldwork audit.** Build the country×round mode table (round-10
   self-completion switches); rerun excluding mode-switching certified pairs; confirm
   Greece's 10→11 pair is mode-constant. Promised in §7 and §8.
8. **Real-data severity injection.** e32 gives the simulation power curve; inject
   known persistent declines into real ESS/WVS data and report detection rates.
   Promised in §5.
9. **Leave-one-region-out exchangeability audit.** Certify each held-out region,
   report empirical coverage. Promised in §2.
10. **SDDF-extended ESS window (optional).** Merge the rounds-1–8 sample-design files
    to extend the trajectory beyond rounds 9–11; would make the persistence rung
    non-degenerate for more countries and address the "single-pair Greece" limitation
    at its root.

## C. Political-science payoff — the highest-upside frontier (6.5 → 8+)

The payoff is currently "confirmation, not discovery." Ranked by leverage:

11. **[TOP, needs microdata] The distributional anatomy of decline.** This is the
    paper's own thesis, underused. Two sub-moves, both requiring the CDFs:
    - *Mean–distribution disagreement*: find countries where the mean/marginal reading
      says "stable" but the distribution-wide band certifies a shift (a mode hollowing
      or tail thickening the mean hides). This flips the tool from "subtracts
      over-claims" to "detects what the mean misses" — the discovery the method is
      uniquely built for.
    - *Shape of certified declines*: for each certified country, classify the decline
      as mode-collapse vs tail-thickening vs uniform-shift (DiMaggio 1996 is already
      cited). "How democracies decline," not just "how many." A new section.
12. **[STRONG, doable now with public data] Downstream predictive validity.** The
    certified-core lists are in `results/certified_core.csv`,
    `ess_country_certification.csv`, `wvs_deconsolidation.csv`; V-Dem is public and
    free. Test whether "persistent distribution-wide deconsolidation" predicts
    subsequent V-Dem backsliding (or electoral/protest outcomes) better than the
    marginal count does. If the honest object is also the more predictive object,
    that is a genuine payoff. N is small (13 core) — present as a suggestive
    cross-tab with exact tests, not a regression.
13. **[MEDIUM, mostly public data] Claassen same-data comparison.** Claassen (2019
    PA; 2020 AJPS) latent-mood estimates are the closest competitor and their
    replication data is public. Show where our finite-sample certification agrees /
    disagrees with his model-based credible intervals, and argue which is right where
    they diverge. Directly answers R3's "what do you add over the existing tool."
14. **[QUICK, public data] Regime-type stratification.** Cross-tab the certified core
    by V-Dem/Polity regime type; stop calling declines in electoral autocracies
    (Rwanda, Uzbekistan, Azerbaijan) "deconsolidation." R3 called this "an afternoon."

## D. Ceiling items (9.3 → 9.5+, post-acceptance, ecosystem not manuscript)

15. **R package (or R wrapper + vignette).** PA's readership is R-first; top-cited
    methods papers are cited through their package, not the article. `dapcb` is a
    clean single-entry API — an R port with a "your survey data → band in 10 lines"
    vignette is the highest-ROI adoption lever.
16. **PyPI release + Dataverse deposit with a version tag** (§3 promises "installable
    package … archived with a version tag on the Dataverse"; `pyproject.toml` now
    exists, so `pip install pcb-conformal` is one release away).
17. **A many-unit real application where deconvolution actually fires** (US
    counties/CCES, schools) — turns E31's simulated positive regime into a real one,
    giving the method a live user base beyond the survey-scale null.

## E. Small open items noted by referees (minor, non-gating)

- Tighten the Th4′ remainder constants C₁, C₂ (currently "obtainable," not displayed).
- Full de-jargonization pass for an outside reader (e28/e30/gate-B/U0/S2 names).
- Same-data Claassen comparison figure (folds into item 13).

## Recommended order

Do A (gates submission) → B5–B7 (the reruns the text already promises) → C12+C14
(payoff wins available from public data, no microdata wait) → then decide whether to
hold for C11 (the distributional-anatomy discovery, which needs the CDFs and is the
real ceiling-raiser) before first submission or save it for the R&R. Merge to `main`
once A and B are done; that makes `main` the submission snapshot.
