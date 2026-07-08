# Theorem Audit — Paper 2 (`pa_core_exact`)

Purpose: reconcile what each theorem **claims** with what the empirical code
**actually does**, and assign KEEP / REVISE / DROP for the exact-core PA restructure.
Written after reading the theory section and the empirical pipeline
(`e12_ess_decline.py`, `e26_wvs_deconsolidation.py`, `decline_certify.py`,
`design_aware.py`). Reruns require the licensed microdata (not in this repo), so the
empirical numbers below are from the code's *method*, not a fresh run — verify on rerun.

---

## 0. THE MOST IMPORTANT FINDING — the headline engine is not any of the theorems

The ESS "only Greece" and WVS "2.6–6.5×" headlines are produced by
**`certify_decline_differences`**, which is:

- a **within-country** test on consecutive CDF differences `D_r(t) = F_{r+1}(t) − F_r(t)`
  (the country effect cancels → **no cross-country exchangeability, no transport**);
- a **studentized (percentile-t) one-sided simultaneous band** on a **design bootstrap**
  (ESS: stratified-PSU Rao–Wu; WVS: weights-only respondent bootstrap);
- valid **asymptotically** (bootstrap consistency in respondents/PSUs), **NOT
  finite-sample exact, NOT conformal**.

Implications:
1. **Good:** the headline does **not** depend on country exchangeability — it defuses the
   single biggest reviewer worry. State this loudly.
2. **Correction to the restructure premise:** "re-run the headline with the exact
   unstudentized clustered band" is a *method change*, not a rerun. Within-country there is
   no exchangeable cluster to exploit, so the design bootstrap is the natural tool. The
   clustered conformal band (Thm `thm:exact`) answers a **different** question
   (predict an unseen country's trajectory / transport).
3. **Framing debt:** the paper advertises "finite-sample exact clustered conformal" as its
   instrument, but the headline is an asymptotic design bootstrap. Stop letting "exact"
   describe the headline. The paper has **two instruments**; name them separately.

**Action:** the PA empirical engine is (A) within-country design-aware simultaneous
decline certification (asymptotic, design-based, exchangeability-free). Add an explicit
validity statement for it (percentile-t simultaneous one-sided band → bootstrap
consistency), and present (B) the clustered conformal exact band as the trajectory-
prediction contribution. Do not conflate their guarantees.

---

## Audit table

| # | Label | Target | Key assumption | Exact vs asymptotic | Actual implementation | Status |
|---|-------|--------|----------------|---------------------|-----------------------|--------|
| — | `certify_decline_differences` (headline engine) | within-country survey estimate (differences) | design bootstrap consistency | **asymptotic** | studentized percentile-t band on design bootstrap; no exchangeability | **KEEP + give it a validity statement; stop calling it "exact"** |
| 1 | `thm:impossible` | latent pop. (score level) | `R̃=R+ξ`, `R⊥ξ` at **score** level | exact (non-identification) | convolution contract test | **REVISE → curve level** |
| 2a | `thm:oracle`(a) | survey estimate | exchangeability only | exact | clustered band | **KEEP** |
| 2b | `thm:oracle`(b) | latent pop. | **symmetric** design law | exact-ish | oracle (true scale), never deployed | **REVISE** (add unimodality/peakedness; demote deconv part) |
| 3 | `thm:exact` | survey estimate `F̃_new` (transport) | exchangeability only | **finite-sample exact, any K** | `clustered_band.py` unstudentized; tests confirm | **KEEP (core theorem)** — but note it does not produce the headline |
| 4 | `thm:estimated` | latent pop. via estimated law | estimated design bootstrap | asymptotic (`ε_{K,B}`) | deconvolution branch — **never fires on real data** | **DEMOTE → supplement / scope** |
| 5 | `thm:safe` | deployed pipeline | selector calibration-measurable | finite `(K,B)` w/ `δ` | mixture argument under-justified; selector never picks deconv on real data | **DROP from main → supplement (safe path)** |
| P | `prop:unreach` | scope boundary | distribution-free `ρ`, `K≥94` | exact bound | `_gate_probe` computes it; neither gate opens | **KEEP (as the scope result that justifies demotion)** |

---

## Per-item detail

### Thm 1 — `thm:impossible` (Non-identification): **REVISE**
- Claim: with `R̃=R+ξ`, `R⊥ξ`, (i) `L_R` not identified from `L_{R̃}`; (ii) no observed-score
  band beats the plug-in for the latent target across all admissible laws.
- Problem (reviewer-confirmed): the additive-**independent** structure is natural at the
  **curve** level `F̃=F+S`, but after the sup/abs score `R=max_t|E_c(t)|` it does not follow;
  and `ξ:=R̃−R` is not generally independent of `R`. Survey-CDF sampling variance is
  heteroskedastic (`F(1−F)`).
- Fix: prove non-identification at the **curve** level; make the score-level corollary
  conditional on stated assumptions, or weaken to: *"without information on the design-noise
  law, no band measurable in the observed survey curves uniformly narrows the latent
  trajectory band."* A precisely-defended weaker theorem beats an over-general one.

### Thm 2 — `thm:oracle`: **(a) KEEP, (b) REVISE**
- (a) clustered band valid for the survey-estimate target using exchangeability only — clean, KEEP.
- (b) "symmetric design law ⇒ conservative for latent target" does not hold for all
  distributions/quantiles of a nonnegative max-abs score; needs unimodality / peakedness /
  stochastic-dominance conditions (reviewer-confirmed). The deconvolution half uses the
  **true** scale (oracle) and is never deployed → move to the scope discussion.

### Thm 3 — `thm:exact` (Exact finite-K unstudentized band): **KEEP**
- The safest result in the paper: order-statistic band on the unstudentized cluster score,
  finite-sample exact at any K, distribution-free, exchangeability only. Studentization is
  correctly shown to break exchangeability (`O(1/K)` self-inclusion deficit).
- Caveat: this is the **transport / unseen-country prediction** instrument. It is **not**
  what certifies "only Greece." Present it as the trajectory-prediction contribution and
  give it its own short self-contained proof + contract test (user Step 3A).

### Thm 4 — `thm:estimated` (Estimated-law deconvolution): **DEMOTE**
- Deconvolution band with estimated design law, `≥1−α−ε_{K,B}`. Legitimate, but the branch
  **never activates** on ESS or WVS (`_gate_probe`: `ρ̂_LCB<0.47`, `K<94`). Empirically inert.
- Move to supplement; in the main, it survives only through `prop:unreach` as a boundary.

### Thm 5 — `thm:safe` (Safe-adaptive selector): **DROP from main**
- Main-text justification: *"Ĵ is calibration-measurable ⇒ coverage is a mixture over
  branches, each valid conditional on being selected."* The **conditional** validity is
  exactly what needs proof and does not follow automatically from target-blindness
  (reviewer-confirmed). Conditioning on a selection event that is a function of the
  calibration scores can distort per-branch coverage.
- Two paths: **safe** — remove the selector from the main contribution, present it as an
  exploratory supplement procedure (recommended, since the branch never fires empirically);
  **ambitious** — split a selection fold from the conformal calibration fold so selection is
  structurally independent, then prove selection-conditional coverage. For PA: safe path.

### Prop — `prop:unreach` (Survey-scale unreachability): **KEEP**
- Proves the need gate (`ρ`) and reliability gate (`K≥94`) cannot both fire at survey scale
  (`ρ` saturates well below `ρ₀`; ESS `K≤33`, WVS weights-only `ρ̂_LCB≤0.09`). This is the
  honest, distribution-free reason deconvolution is demoted — it becomes the spine of the
  "estimated calibration objects as a scope problem" section, not a failure to hide.

---

## Net effect on the paper

- **Core kept (finite-sample-safe):** `thm:exact` (prediction band) + the within-country
  design-aware decline engine (given its own asymptotic validity statement) + `prop:unreach`.
- **Demoted to scope/supplement:** `thm:estimated`, `thm:safe`, deconvolution efficiency
  (AW-1..AW-4), `thm:oracle`(b) deconvolution half.
- **Revised for defensibility:** `thm:impossible` (→ curve level), `thm:oracle`(b) symmetry
  condition.
- **Headlines that must survive the rerun (verify on your machine):** Greece stays under the
  design-aware within-country test **and** after across-country Bonferroni; `trstprl` and
  `stfdem` agree; WVS persistent/plug-in ratio stays ~2.6–6.5×; youth-vs-older split holds.

The paper loses nothing empirical by demoting the selector (it never fires) and gains a
clean, honest two-instrument story with a much smaller exposed surface.
