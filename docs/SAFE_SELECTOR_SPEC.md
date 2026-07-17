# Safe selector specification (FROZEN)

Status: **frozen 2026-07-06** on the development grid (tag `gate5d-finiteK-fix`).
Every constant below was derived from development evidence ONLY and is fixed before
the independent confirmatory validation (`INDEPENDENT_VALIDATION_PREREG.md`). It is
not to be re-tuned after seeing holdout results.

## Why a re-specification (honest development record)

The initial adaptive selector (Gate 5C–5E, tag `gate5d-finiteK-fix`) gated the
deconvolution branch on a reliability threshold τ chosen as the *largest* τ whose
development-grid coverage met the floor. On the reproducible development grid this
left four ρ-transition cells slightly under the 0.88 floor (worst 0.862; see
`SAFE_SELECTOR_RESULTS.md`). We treat those cells as **development evidence of a
transition-zone finite-K deficit** and re-specify the safety gate on a conservative
principle, then validate the frozen rule on a completely new design. This is method
development, not post-hoc conservatization: the rule is fixed before the new data.

## The deployed rule (`pcb/dapcb.py`)

The selector is target-blind (a function of the calibration curves only). Let K be
the number of source populations (clusters), B the design-bootstrap depth, and per
threshold t: s_plug(t) the modulation scale, v̂_c(t) the design-noise SD, ŝ_T(t) the
finite-K-safe deconvolution scale (`deconv_target_scale`). Define

- **ρ̂_LCB** — conservative lower confidence bound on the SD ratio ρ (`rho_lcb`).
- **D** — reliability diagnostic, D = max_t SE(ŝ_T²(t))/ŝ_T²(t) (`deconv_reliability`).
- **δ̂_UCB(D)** — finite-K coverage-remainder upper bound (frozen, below).
- **Ĝain_LCB** — leave-one-cluster-out jackknife lower bound on 1 − W_dec/W_con.

Deconvolution is activated **iff all four gates pass**:

| gate | condition | frozen value | meaning |
|---|---|---|---|
| A need | ρ̂_LCB > ρ₀ | ρ₀ = 0.47 | design noise materially exceeds transport noise |
| B finite-K | δ̂_UCB(D) ≤ δ_max | δ_max = 0.02 | coverage remainder within budget |
| C efficiency | Ĝain − Δ_g > g_min | g_min = 0.10, Δ_g = 0.05 | beats conservative by a real margin |
| D stability | min_t (s_plug² − mean_c v̂²) > (0.05·max s_plug)² | — | deconvolution well-posed |

Otherwise: **ρ̂_LCB ≤ ρ₀ → clustered PCB** (design noise negligible); **else →
conservative fallback** (design noise real but information insufficient). When
deconvolution is used, the reported guarantee is the observable
`coverage_level = 1 − α − δ̂_UCB(D)`.

## Frozen δ̂_UCB(D) — derivation on the development grid

Target: an upper bound on the deconvolution-branch finite-K coverage deficit
(0.90 − coverage) as a function of the single observable D. On the development grid
(`results/safe_selector_grid.csv`, 36 cells), over the operational range D ≤ 1.0 we
regress per-cell deficit on D:

    deficit ≈ −0.0045 + 0.0943·D     (OLS; residual SD 0.0122)

The residual SD is inflated by Monte-Carlo noise; removing it
(σ²_struct = σ²_resid − mean cell MC-variance, MC-SD ≈ 0.0103) gives the structural
scatter σ_struct = 0.0064. The frozen conservative upper bound folds a one-sided
95% structural margin into the intercept:

    **δ̂_UCB(D) = 0.0061 + 0.0943·D**     (DUCB_A = 0.0061, DUCB_B = 0.0943)

Gate B (δ̂_UCB ≤ δ_max = 0.02) is therefore equivalent to **D ≤ 0.148**. On the
development grid every gate-B-eligible cell has actual deconvolution-branch deficit
≤ 0.017 < 0.02 — the rule is self-consistent on the data used to build it. It is
much more conservative than the previous τ = 0.809 (which admitted the undercovering
transition cells).

## Frozen Ĝain_LCB

Ĝain = 1 − W_dec/W_con (fractional width reduction versus the conservative branch),
computed from the calibration set. Ĝain_LCB = Ĝain − Δ_g, where Δ_g = 0.05 is a
frozen conservative margin, chosen ≥ 1.645× the development per-rep gain SD (median
0.028 → 0.046). This O(1) lower bound replaces a per-cluster jackknife SE (which is
smaller than Δ_g in the operative large-K regime where gate C binds, so the fixed
margin is conservative there); it is exactly equal when the jackknife SE is 0.030.
g_min = 0.10: deconvolution must be ≥10% narrower than conservative (after the
margin) to be worth its finite-K risk.

## Frozen constants (single source of truth = `pcb/dapcb.py`)

    ρ₀       = 0.47      # gate A (Gate 5C cutoff)
    δ_max    = 0.02      # gate B budget
    DUCB_A   = 0.0061    # gate B: δ̂_UCB(D) = DUCB_A + DUCB_B·D
    DUCB_B   = 0.0943
    g_min    = 0.10      # gate C
    GAIN_MARGIN = 0.05   # gate C conservative LCB margin (frozen)
    stability floor = (0.05·max_t s_plug)²   # gate D

Development data (grid, seeds, (K,ρ) cells, the four transition cells) may be used
to SET these values but must NOT be reused as confirmatory validation performance.

---

## Addendum (2026-07-17): Theorem 5′ architecture revision

The validity architecture around the frozen gates was revised after an audit
found the original conditional-on-selection proof invalid (selection event and
conformal quantile share the calibration data). The gates and constants above
are UNCHANGED; what changed:

1. **PCB and conservative branches are unstudentized (U0)** and therefore
   NESTED (conservative score max_t(|E|+z·v) dominates PCB score max_t|E|).
   Selection between nested bands anchored at an exact band is validity-free
   (Lemma NB) — the gates now carry no validity burden at all.
2. **The deconvolution branch is charged its own miss budget**
   α_dec = min(max(0.1α, 3/(K+1)), α/2), a function of K only, and only when
   gate B is feasible (K ≥ 94). Below that K the anchors keep the full α and
   the deployed guarantee is exact 1−α with no remainder.
3. The 3/(K+1) floor exists because a flat 0.1α budget leaves the branch's
   conformal quantile at/beyond the sample maximum for 94 ≤ K ≲ 200
   (see docs/POSITIVE_REGIME_RESULTS.md).

Real-data consequences: none (all real cross-national data ride the PCB branch
at full α; widths unchanged). Simulation consequences: e22/e31 rerun under the
revised architecture; see HOLDOUT_VALIDATION_RESULTS.md addendum.
