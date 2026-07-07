# Clustered PCB: estimands, exact construction, finite-sample validity (E9)

Status: gate-3 lock-in, 2026-07-06. Code: `pcb/inference/clustered_curve_band.py`,
`pcb/inference/fixed_trajectory_band.py`. Per-target audit:
`results/ess_cluster_exact_audit.csv`. Gate-3 discovery record (frozen, not
edited): `results/ess_cluster_audit.csv`, `docs/ESS_CLUSTER_VALIDITY.md`.

## 1. Setup and units

Repeated cross-national survey: country trajectories
`(E_{c,1}, …, E_{c,R_c})` of transport-error curves over T thresholds. Two
layers of exchangeable unit — respondent → country-round population (the
original PCB layer) and country-round → country cluster (this layer);
threshold and round are *simultaneity dimensions*, not units. Predictor here
is LOCF (**temporal transport**; unseen-country transport is a separate,
upcoming design). LOCF fits nothing, so country-blocked out-of-fold errors
hold structurally; fitted predictors must use a leave-one-country-out OOF
error tensor.

## 2. Two estimands (never conflated)

**A. Single-round curve.**  Claim: `θ_{c*,r*}(t) ∈ B(t) ∀t` for ONE round of
a held-out country. Calibration: exactly one error curve per country (fixed
a-priori rule: most recent round). Reduces numerically to the original PCB
on the selected (K, T) matrix (`tests/test_single_round_reduces_to_pcb.py`).

**B. Fixed-length trajectory (main specification, L = 4).**  Claim: all of a
held-out country's most recent L rounds, all thresholds, simultaneously:

    R_c = max_{j≤L} max_t |E_{c,j}(t)| / s_j(t),
    q̂ = R_(m),  m = ⌈(1−α)(K+1)⌉  (exact order statistic; K countries),
    B_j(t) = θ̂_{c*,j}(t) ± q̂·s_j(t),  isotonic-tightened per round.

**Theorem (finite-sample trajectory validity).** If the L-round country
trajectories `(E_{c,1..L})` for c = 1..K+1 are exchangeable and the
modulation s is constructed independently of the scored errors, then

    Pr[ max_{j≤L,t} |E_{K+1,j}(t)|/s_j(t) ≤ q̂ ] ≥ 1 − α .

*Proof sketch:* conditional on s, the scores R_1,…,R_{K+1} are exchangeable
scalars; the rank of R_{K+1} is uniform on {1,…,K+1}; the covered event is
exactly {R_{K+1} ≤ R_(m)}, of probability ≥ m/(K+1) ≥ 1−α. Ties have measure
zero under continuity. With L = 1 the statement is the original PCB
proposition; L > 1 adds nothing but a larger index set for the sup. ∎

Variable-length all-round scores are NOT used as a method: a longer
trajectory has more chances to throw one extreme error, so scores are not
comparable across countries with different R_c. All-round results are
retained as a sensitivity (`S_allround`).

## 3. ESS results (LOCF, α = .10; exact counts, Wilson CIs in the CSV)

| estimand | outcome | covered | coverage | attainable | mean width |
|---|---|---|---|---|---|
| A curve (K=34) | trstprl | 31/35 | .886 | .914 | .322 |
| A curve | stfdem | 30/35 | .857 | .914 | .359 |
| **B traj L=4 (K=29)** | **trstprl** | **27/30** | **.900** | .900 | .426 |
| **B traj L=4** | **stfdem** | **27/30** | **.900** | .900 | .443 |
| S all-round | trstprl | 31/35 | .886 | .914 | .584 |
| S all-round | stfdem | 31/35 | .886 | .914 | .494 |

Countries dropped from B (fewer than 4 LOCF rounds): LU, LV, ME, RS, TR.
A-curve counts are within binomial noise of the attainable level
(P(X ≤ 30 | n=35, p=.914) ≈ .16). The trajectory guarantee costs ×1.45 width
over the single-round guarantee — users pick the band matching their claim.

## 4. Modulation audit (new finding)

The theorem requires s independent of the scored errors. The practical
in-sample variant is not innocent at K ≈ 30:

- per-slot modulation (s_j from 29 curves; each country contributes 1/29 of
  the scale that studentises its own score): trstprl **22/30 = .733** —
  material undercoverage from in-sample shrinkage;
- pooled modulation (one s(t) from all K·L curves; self-fraction 1/(K·L)):
  **27/30 = .900** on both outcomes.

Main specification therefore uses POOLED modulation
(`trajectory_modulation(kind="pooled")`); per-slot is retained as a
sensitivity; the exact split-modulation version is the theorem's form. This
mirrors, and sharpens, the in-sample-modulation remark of the original paper:
at population-level K ≈ 100+ the effect was negligible; at country-level
K ≈ 30 it is not, when the modulation is sliced too finely.

## 5. Audit of the gate-3 all-round 31/35

- Conformal quantile: exact order statistic m = ⌈(1−α)(K+1)⌉ everywhere; no
  interpolation quantiles (`tests/test_cluster_quantile_order.py`).
- Binomial consistency: P(X ≤ 31 | n=35, p=.914) = .355 — no anomaly to
  explain.
- Missed countries: GR, IS, RS, TR — mean trajectory length 3.2 vs 7.6 for
  covered. The direction is the OPPOSITE of length-inflation: misses are
  short-trajectory, substantively volatile countries (Greek debt crisis,
  Icelandic crash, short RS/TR participation), i.e. genuine tail
  trajectories, not a score artifact.
- Modulation: fixed-global-s diagnostic gives 32/35 (exactly the attainable
  count); per-target modulation costs ≈ 1 country.
- Prediction refitting: none exists under LOCF.

## 6. Reporting discipline

Every coverage figure states: the exchangeable unit, effective K, the order
index m, the attainable level m/(K+1), exact covered counts, and a Wilson
interval. With K ≈ 30–34 the quantile granularity is ~3%: decimal-point
coverage comparisons are meaningless and are not made.
