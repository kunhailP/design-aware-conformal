# Modulation validity for clustered trajectory bands (Gate 4A, E10)

Status: completed 2026-07-06. Code: `pcb/experiments/e10_modulation_validity.py`,
figures `pcb/figures/fig_modulation.py`. Data:
`results/modulation_validity_ess.csv`, `results/modulation_simulation.csv`.
Gate-3 files are frozen and untouched.

## 0. Naming discipline (binding for all code, docs, paper text)

| tag | construction | status |
|---|---|---|
| U0 | unstudentized, `R_c = max_{r,t}|E|` | **finite-sample exact** (no scale estimated) |
| S1 | independent split modulation: `s_j(t)` from a disjoint modulation-country set, fixed for calibration and target | **finite-sample exact studentized** |
| S2 | pooled in-sample modulation (one s(t) from all K·L calibration curves) | EMPIRICAL variant — never described as exact-valid |
| S3 | slotwise in-sample modulation | EMPIRICAL variant — **fails at small K**, sensitivity only |

Using an exact order statistic m = ⌈(1−α)(K+1)⌉ does not make a procedure
exact; U0 and S1 are exact because their scores are exchangeable with the
target's, which S2/S3 break by letting each calibration country co-estimate
the scale that studentises its own score.

## 1. ESS, L = 4 trajectories (30 countries, LOCO; nominal 90%, attainable .900)

| method | trstprl cov | stfdem cov | width trstprl | width stfdem | eff. K |
|---|---|---|---|---|---|
| U0 | **27/30 = .900** | **27/30 = .900** | **0.397** | 0.446 | 29 |
| S1 (20 random splits) | .900 | .903 | 0.604 | 0.780 | 20 |
| S2 | 27/30 = .900 | 27/30 = .900 | 0.426 | 0.443 | 29 |
| S3 | 22/30 = .733 | 26/30 = .867 | 0.367 | 0.420 | 29 |

**The headline surprise: U0 wins on ESS.** Exact validity, the weakest
assumptions, and a band as narrow as or narrower than S2 (trust-CDF error
scales are nearly homogeneous across thresholds, so studentization buys
nothing here and estimated scale only adds noise). S1 is exact but pays
double at K = 30: a coarser quantile (eff. K 20) and a noisy split scale.
S3's narrow width is what undercoverage looks like.

## 2. Simulation: self-inclusion over K × L (E = a_c + b_cr + u_crt, T = 10)

Grid K ∈ {20,30,50,100} × L ∈ {1,2,4,8} × {homo, heteroskedastic}, 1000
reps/cell. Figures: `figures/coverage_by_K_L.png`,
`figures/modulation_score_shrinkage.png`.

- **S3 undercovers exactly as diagnosed**: coverage .77–.85 at K = 20–30 and
  the gap GROWS with L (more slots = finer slicing = larger self-share); the
  calibration/target score ratio falls to .88–.91 at K = 20 and approaches 1
  only as K → 100.
- **S2's recovery is real, not ESS luck**: its self-share is 1/(K·L), the
  score ratio stays ≥ .97 everywhere, and coverage tracks nominal to within
  ~1–2pp — from below at moderate K (e.g. .879 at K = 30, L = 2; .888 at
  K = 30, L = 4). A small negative bias exists; hence "empirical variant".
- **U0 and S1 sit at their attainable levels across the whole grid**,
  including heavy heteroskedasticity; two-sided exactness is enforced by
  `tests/test_split_modulation_exact.py` and
  `tests/test_unstudentized_exchangeability.py` (the latter under t3 tails).
- **The width cost of dropping studentization is small even when it should
  matter**: under engineered 4× threshold heteroskedasticity, U0 is only
  ~4–5% wider than S2 (e.g. .2196 vs .2101 at K = 30, L = 4); S1 pays
  15–40% at split-feasible K.

## 3. Recommendation for the paper

Main method: **U0 for the ESS application** (exact, assumption-minimal,
narrowest-or-tied in this data). S2 reported as the empirical studentized
variant (matching numbers, .900 on both outcomes); S1 as the exact
studentized option when thresholds are strongly heteroskedastic AND K
permits a split; S3 only as the cautionary sensitivity. This upgrades the
original repo's "in-sample modulation is empirically indistinguishable"
remark: true at population-level K ≈ 100+, false under fine slicing at
country-level K ≈ 30 (the E9 finding), and the safe default is to not
studentise at all unless the data demand it.

## 4. Single-round estimand redefined (A2) and the old misses explained

Old design (E9 "A_curve": each country's latest available round) mixed
horizons and calendar periods — not one estimand. Redefined as
**one-step-ahead onto a common target round r\***: predict round r\* from
r\*−1, countries lacking either round excluded.

| estimand | outcome | U0 | S2 | attainable |
|---|---|---|---|---|
| A2 r\*=10 (K=27) | trstprl | **26/28 = .929** | 24/28 | .929 |
| A2 r\*=11 (K=28) | trstprl | **27/29 = .931** | 25/29 | .931 |
| A2 r\*=10 | stfdem | **26/28 = .929** | 26/28 | .929 |
| A2 r\*=11 | stfdem | **27/29 = .931** | 26/29 | .931 |

U0 lands exactly on the attainable count in all four cells. The old stfdem
30/35 decomposes accordingly: LU (target round 2) and TR (round 4, gap 2)
are pre-2012 exits scored against decade-old horizons; UA has gap 5 (LOCF
across ~10 years); FI and PL are round-11 near-misses (scores 3.08/4.17 vs
critical ≈ 2.91). Heterogeneous horizons, not a method failure.

## 5. Open items carried to Gate 4B/4C

- Gate 4B hierarchical simulation extends the DGP with heavy tails,
  directional bias, within-country round correlation knobs, and the
  round-cal-vs-cluster-cal decomposition (Prop 1 empirics).
- Gate 4C: Prop 1 (curve validity ≠ trajectory validity), Prop 2 (exact
  clustered validity, = the U0/S1 theorem), Prop 3 (self-inclusion breaks
  rank symmetry — formal counterexample + the simulation characterization
  here; a general theorem is optional).
- Literature check before claiming Prop 3 as novel: the split requirement is
  consistent with how functional conformal bands justify estimated
  modulation (Diquigiovanni et al.); verify no prior result already
  quantifies in-sample modulation undercoverage at small K.
