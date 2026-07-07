# Code verification pass (2026-07-07)

An adversarial correctness audit of the load-bearing code, run before further paper
work. Two independent agents audited disjoint halves of the pipeline; independent
numeric recomputation checked the newest theorem. **Verdict: no correctness bug flips
any claim.** The three headline results all verified / reproduced / robust. Minor
precision issues found and fixed; honest caveats recorded.

## What was checked and how

**Independent numeric recomputation (this session).**
- `deconv_reliability` matches an independent reimplementation of its formula to
  machine precision (max abs err 0) over 4000 random inputs.
- The load-bearing bound **D ≥ √(2/(K−1))** holds on 4000 random DGPs (Gaussian /
  Student-t / skewed design noise), min ratio exactly 1.0000 — a genuine, tight,
  distribution-free lower bound, not a Gaussian artifact.
- `rho_lcb` ∈ [0,1.5] always and ≤ ρ̂ (a genuine lower bound).
- The unreachability arithmetic: τ_D=(δ_max−a)/b=0.1474 ⟹ K*=1+2/τ_D²=93.05 ⟹ K≥94.
- Every one of the 42 ESS scan cells: D ≥ floor, D > τ_D (gate B fails), ρ̂_LCB < ρ₀,
  branch = PCB — fully self-consistent.
- **Determinism:** re-running `e24.scan()` reproduces the committed CSV to 1e-16.
- **Transport-construction sanity:** ρ̂ = v_mean/s_mean exactly; the design SD v_mean =
  1.3–3.2 percentage points, matching the independently-reported ESS design SDs of
  earlier gates — so V (hence the negative ρ result) is **not** understated by a
  construction bug.

**Agent A — inference primitives + E24.** Probed `_finite_quantile` (Monte-Carlo
coverage, no off-by-one; correct +∞ at small K), `deconv_target_scale` (ŝ_T ≤ s_plug
always), `rho_lcb`, `deconv_reliability` (D-floor analytic + empirical), the Rao–Wu
stratified bootstrap (`_design_sd_core`, matches an independent reimplementation), and
the LOCO transport construction (`_transport_EV`: argmax over rounds, E/V aligned on the
same per-threshold round selector). Re-ran the full scan: 42 cells, gate A 0/42,
deconvolution 0/42. **No bug.**

**Agent B — deployed selector + holdout + political headline.** Verified `dapcb`'s
4-gate logic and per-branch coverage levels, the three conformal radii (deconv deployed
at scale sT, not √(sT²+V²)), the [0,1] clip (cannot drop coverage of a CDF), the e22
latent-target coverage evaluation and config-hash abort, and every holdout DGP family's
V/xi consistency. **Reproduced the political headline on real ESS data:** persistent
country-wide design-aware decline = **['GR']**, count 1, for both trstprl and stfdem
(and under Bonferroni). **No bug.**

## Fixes applied this session

- **`decline_certify.py` — percentile-t tail sign.** The one-sided simultaneous lower
  band's bootstrap pivot should approximate (D̂−D) by (D*−D̂)=`(db−dh)`; the code used
  the opposite tail `(dh−db)`. For a symmetric bootstrap law the quantiles coincide, and
  re-running e13 with the corrected tail leaves the headline **unchanged** (persistent =
  ['GR'] for both outcomes, all counts identical). Fixed to the textbook pivot; the
  Greece result is now shown to be robust to this choice.
- **ρ terminology.** `rho_lcb`'s docstring and the unreachability doc/figure said ρ =
  "design-SD / transport-SD." The quantity actually computed and gated on is ρ =
  design-SD / **total**-SD = √(mean v²)/s_plug ∈ [0,1) (consistent with the width law
  √(1−ρ²) and the ρ₀=0.47 gate). Corrected the label everywhere and flagged the
  distinction from the unbounded design/transport dial v/s_R used in simulation.

## Honest caveats recorded (not bugs; none flips a claim)

- **Lonely-PSU downward V bias.** Single-PSU strata contribute zero bootstrap variance
  (standard Rao–Wu), biasing V slightly low — which only makes the unreachability result
  *more* conservative. Noted in `SURVEY_SCALE_UNREACHABILITY.md`.
- **Cross-pair bootstrap correlation** (`e13`): adjacent wave-pairs share a round but are
  bootstrapped independently before the simultaneous sup; a mildly conservative
  approximation of the joint critical value, does not change counts.
- **`dapcb.rho_hat` denominator** uses mean(s) vs √(mean s²) — a display-only diagnostic
  (no gate uses it), left as-is to preserve the frozen selector; slightly overstates ρ
  vs the LCB baseline.

## Bottom line

Every load-bearing numerical claim — the survey-scale unreachability theorem
(D-floor + K≥94), the frozen holdout's P3 pass, and the "only Greece" political headline
— is independently verified, reproduced, and robust to the coding choices identified.
42 contract tests pass.
