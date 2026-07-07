# Survey-scale unreachability of design-aware deconvolution (E24)

**Note on ρ.** Throughout, ρ = design-SD / **total**-SD = √(mean v²)/s_plug with
s_plug² = s_R² + mean v², so ρ ∈ [0,1) and the ρ₀=0.47 gate and the width law
W_dec/W_pcb=√(1−ρ²) are on this ratio. It is *not* the unbounded design/transport dial
v/s_R used to generate the simulation grids (there ρ ranges to 1.8). Design/total 0.47
corresponds to design/transport ≈ 0.53.

**Question.** The design-preserving stress test (E18) showed the country-level
design/total SD-ratio ρ saturates near 0.23 on real surveys. But the paper's biggest liability is that the
design-aware deconvolution branch never *activates* on real data — a referee will ask
"then why should I care?" So we asked the sharper question: **is there ANY real
subpopulation or estimand where the deployed selector rides deconvolution?** If yes,
the method has a real-data win. If no, we want to know *why*, precisely enough to turn
the inertness into a theorem.

**Answer: no — and for two independent, quantifiable, structural reasons.** Neither is
an accident of the ESS sample; both are binding at survey scale. The selector's
constant abstention is therefore *provably correct*, not a shortcoming.

The scan (`pcb/experiments/e24_subgroup_rho_scan.py`, `results/ess_subgroup_rho_scan.csv`,
`figures/unreachability.png`) builds the LOCO cross-country transport E/V (as in E16)
*within* seven ESS age-band subpopulations × two outcomes × three min-cell floors
(80/120/200), and reports the full ρ̂ distribution and the selector's route for every
cell, exactly as produced. 42 cells. **Deconvolution activates in 0 of 42.**

## Barrier 1 — Gate A: ρ̂ saturates far below ρ₀

Narrowing the subpopulation *does* raise the design noise: the full-sample ρ̂≈0.078
rises to **ρ̂=0.288** in the narrowest youth band (18–24) — a ~3.7× increase. But it
plateaus far below ρ₀=0.47:

| statistic | value | where |
|---|---|---|
| max ρ̂ | **0.288** | youth 18–24, trstprl, K=4 |
| max ρ̂ lower-CB | **0.146** | youth 18–24, trstprl |
| cells with ρ̂_LCB > ρ₀ | **0 / 42** | — |

**Why it saturates.** With `s_plug² = s_R² + v̄²`, ρ̂² = v̄²/(s_R² + v̄²). Pushing ρ̂ up
requires v̄ (design noise) to rival s_R (the genuine between-country transport spread).
For high-salience political outcomes, between-country differences are *large* (Greece
vs. Denmark are genuinely far apart), so s_R is large and v̄/s_R stays small until cells
are so tiny that K collapses. This is a real tension: **deconvolution helps only when
countries are nearly identical (small s_R) — but then there is nothing worth
certifying.** The design noise you need to dominate is exactly the political signal you
need to survive.

## Barrier 2 — Gate B: the finite-K reliability floor needs K ≥ 94

This is the *binding* barrier, and it is distribution-free. The reliability diagnostic
is `D = maxₜ SE(ŝ_T²)/ŝ_T²` with
`SE(ŝ_T²) = √(2 s_plug⁴/(K−1) + (SDₖ(v²)/√K)²)`. Since `ŝ_T ≤ s_plug` for every t,

> **D ≥ √(2/(K−1))**  — a distribution-free lower bound on the relative uncertainty of
> the deconvolved transport scale.

It is essentially achieved on real data: across all 42 cells D/√(2/(K−1)) ∈ [1.007,
1.061] (median 1.020) — the ESS cells sit *on* the floor curve
(`figures/unreachability.png`, right). At ESS's largest K=33, D ≥ 0.25.

The safety gate B is `δ̂_UCB(D)=a+bD ≤ δ_max` with the frozen a=0.0061, b=0.0943,
δ_max=0.02, i.e. **D ≤ τ_D = (δ_max−a)/b = 0.147**. Combining with the floor:

> gate B feasible ⟹ √(2/(K−1)) ≤ τ_D ⟹ **K ≥ 1 + 2/τ_D² ≈ 94** exchangeable populations.

Repeated cross-national surveys do not have 94 countries: ESS ≤ 33, LAPOP ~20–28,
Afrobarometer ~30–40, Eurobarometer ~30. **The gate-B feasible region is empty at
survey scale**, regardless of ρ — so even if gate A were somehow passed, deconvolution
would still be blocked.

## Honest caveats (what is fundamental vs. calibration-dependent)

1. **The D ≥ √(2/(K−1)) floor is fundamental** — it is just the sampling error of a
   variance estimated from K clusters, distribution-free. At K≈30 the deconvolved
   scale has ≥25% relative standard error. That is the real, gate-independent obstacle,
   and it is *why* naive deconvolution undercovers (see `theory_coverage.png`).
2. **The exact K*≈94 depends on the frozen gate-B constants** (a, b, δ_max), which were
   calibrated conservatively on the development grid. A less conservative δ_max would
   lower K*. So K*≈94 is the threshold *for the deployed gate*; the load-bearing,
   calibration-free statement is the √(2/(K−1)) floor and the resulting ≥25% relative
   SE at survey K.
3. **V is a conservative (slightly low) design-noise estimate.** Single-PSU ("lonely")
   strata contribute zero bootstrap variance under the standard Rao–Wu convention, and
   ~28% of strata are lonely in a typical youth cell. This biases the design SD V
   *downward*, which pushes ρ̂ *down* — i.e. it can only make the negative result more
   conservative, never manufacture a false one. The true design noise is if anything a
   little larger than measured, and still nowhere near enough to reach ρ₀.
4. **The method is NOT dead in general — only for cross-national comparison.** K ≥ 94 is
   routinely available in *many-unit* settings: subnational areas (US counties ≈ 3000),
   schools, firms, clinics. There the reliability floor drops below τ_D and the branch
   can activate. The unreachability result is specifically about the *cross-national*
   application, where the number of countries is the binding constraint.

## What this means for the paper

This converts the "empirically inert" weakness into a **characterized scope theorem**:
we prove, on two independent axes and confirm on real ESS data, that valid design-aware
deconvolution is unreachable at cross-national survey scale, and that the selector's
constant abstention (to clustered PCB at low ρ, to conservative when information is
insufficient) is the theoretically correct response. The empirical payoff of the paper
is then honestly located where it actually lives:

- the **impossibility / non-identification** result (T0),
- the **safe selector** as the procedure that recognizes the unreachable regime and
  stays valid (now with a hard K-threshold showing the abstention is not conservatism
  but necessity),
- the **political reanalysis**, which runs on the clustered-PCB / conservative branch
  that the theory says is the correct one at K≈30.

It does **not** manufacture a real-data efficiency win — that regime is proved out of
reach for cross-national surveys, and we say so.
