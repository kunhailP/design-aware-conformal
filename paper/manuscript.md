# The Wrong Unit of Uncertainty: Adaptive Design-Aware Conformal Inference for Repeated Cross-National Surveys

**Skeleton — 2026-07-06.** Structure fixed; results filled from the gate docs;
prose marked `[WRITE]`. Target ≤6,000 words. Numbers here are load-bearing and
traceable to `docs/*` and `results/*` (cited inline). Convert to LaTeX at the end.

---

## Abstract [WRITE ~150w]

Repeated cross-national surveys are increasingly used to track distributions of
political attitudes, and to *transport* them — predicting one country's trajectory
from others. We show the uncertainty in these exercises is attached to the wrong
unit. The calibration objects themselves — other countries' attitude
distributions — are not observed but estimated through complex samples, and
standard practice treats these noisy estimates as truth. We prove (Thm 0) that
without design information the latent transport uncertainty is *unidentified*: no
band can be both honest and narrower than a conservative plug-in. We give a **safe
adaptive procedure** that uses replicate-weight/design-bootstrap information to
deconvolve survey noise when it can do so reliably, reduces to ordinary clustered
conformal inference when design noise is small, and abstains conservatively
otherwise — with a finite-sample coverage guarantee for the *deployed* pipeline.
Applied to the European Social Survey and the AmericasBarometer, the method shows
that cross-national attitude inference is universally a *low-noise* regime, and
that once survey design and the whole within-country trajectory are jointly
controlled, a persistent distribution-wide decline in political trust is certified
in **only one** of ~30 democracies (Greece), against ~20 flagged by marginal
wave-by-wave analysis.

---

## 1. Introduction (~800) [WRITE]

Beats to hit:
- Repeated cross-national surveys (ESS, WVS, AmericasBarometer) → tracking &
  transporting attitude distributions; conformal/prediction bands increasingly used.
- **The missing layer:** conformal inference is calibrated on *observed outcomes*;
  here the calibration objects are *latent population functions observed through
  complex samples*. Standard practice treats survey estimates as truth. [identity
  sentence]
- Two conflated errors: cross-country transport error + within-survey design
  error (Eq. 1).
- Contributions: (i) an impossibility result pinning what design information is
  necessary; (ii) a safe adaptive procedure with finite-K deployed validity;
  (iii) a substantive reanalysis overturning the "widespread trust decline"
  reading.
- One-paragraph roadmap.

Identity sentence (use verbatim): *Conformal inference is usually calibrated on
observed outcomes; repeated cross-national surveys require calibration on latent
population functions observed only through complex samples.*

## 2. Setup and impossibility (~800)

- **2.1 Objects.** Country c has a latent CDF trajectory F_{c,r}(t) over rounds r,
  threshold t; observed as F̃_{c,r}=F_{c,r}+S_{c,r} via a stratified/clustered
  design (weights, PSU, strata). Transport center μ; transport score
  R_c = max_{r,t}|F_{c,r}−μ|/σ; contaminated observed score R̃_c = R_c + ξ_c,
  design variance v_c² from a stratified-PSU bootstrap. ρ = design-SD/transport-SD.
- **2.2 Decomposition (Eq. 1):** F̃−F = [transport error] + [design error].
- **2.3 Theorem 0 (necessity/impossibility).** [state] Without the ξ-law, the
  latent quantile is unidentified (convolution non-invertibility) and no
  observed-score-measurable band below the plug-in radius is valid for all laws
  (conformal converse under ξ≡0). ⇒ the design bootstrap is the *identifying
  information*, not a convenience. Proof → App. A / `THEORY_MAIN.md`,
  `test_theorem0.py`.
- Reader takeaway: the standard practice is not merely inefficient — it is the
  only honest option *until* design information is supplied.

## 3. Safe adaptive method (~1,300)

- **3.1 Three branches.** PCB (clustered conformal on observed scores; exact for
  the survey-estimate target, conservative for the latent one); deconvolution
  (studentize by ŝ_T,safe²=max(s_plug²−[mean v̂²−z·SE]_+, floor); width ×√(1−ρ²));
  conservative worst-case envelope.
- **3.2 The three questions (the paper's spine).** *Can we deconvolve · do we need
  to · can we do it safely at this K?* The naive selector answered the first two;
  ours adds the third.
- **3.3 Safe selector (Algorithm 1).** Activate deconvolution iff
  (A) ρ̂_LCB>ρ₀ [need], (B) reliability D=max_t SE(ŝ_T²)/ŝ_T² ≤ τ [safe at this K],
  (C) stable, (D) ≥5% narrower than conservative [worth it]; else ρ̂_LCB≤ρ₀→PCB,
  else→conservative. τ calibrated once on a disjoint simulation grid to a coverage
  floor. Target-blind throughout.
- **3.4 Diagnostics returned** (usability): selected_branch, ρ̂, ρ̂_LCB, D,
  coverage floor, fallback_reason. `dapcb()` API [App. / package].

Algorithm 1 box: inputs (curves, clusters=country, design replicates, α); the four
gates; outputs (band + branch + diagnostics).

## 4. Theory (~1,000)

Four theorems (full proofs App. A; `THEORY_MAIN.md`, `DESIGN_AWARE_THEOREM.md`,
`ADAPTIVE_WIDTH_THEORY.md`):
- **Thm 1 (oracle validity):** 1a exact for the survey-estimate target
  (exchangeability only); 1b conservative for the latent target under symmetric ξ.
- **Thm 2 (estimated-law validity):** P(cover) ≥ 1−α−ε_{K,B}, ε_{K,B}=O(1/√K)+
  O(1/√B); width →oracle ×√(1−ρ²).
- **Thm 3′ (safe-adaptive finite-K validity — the deployed pipeline):**
  P(∀r,t cover) ≥ 1−α−δ, δ preregistered and observable, δ→0 as K grows. Proof:
  target-blind selector ⇒ mixture over branches each ≥1−α−δ.
- **Efficiency (Thm 3 / AW):** low-ρ reduction W_D/W_P=1−½ρ²+O(ρ⁴) (matches data
  to the decimal); conservative dominance W_D<W_C; boundary-aware excess width
  O_p(1/√K); full oracle inequality stated open.
- Modulation self-inclusion deficit O(g/K) → App.

## 5. Simulation and design-preserving stress test (~900)

- **5.1 Selector transition & finite-K (Fig 1, `selector_sweep.png`).** Known
  truth, ρ dial-able: selector moves PCB→deconv(at ρ₀)→conservative; plain
  deconvolution undercovers at finite K (0.75 at K=30, transition regime) — the
  honest ε_{K,B}.
- **5.2 Safe-selector grid (Fig 2, `safe_selector_grid.png`).** Worst-case coverage
  0.862 (32/36 cells ≥0.88; the four marginal cells 0.862–0.878 sit in the
  ρ-transition band, within ≈2 MC-SE — the visible finite-K remainder δ, vs the
  naive-deconvolution 0.75). K=30 high-ρ abstains to conservative; K=240 activates
  deconv at 0.44× conservative width; low-ρ width=1.00×PCB
  (`safe_deconv_coverage.png`, App.).
- **5.3 Design-preserving semi-synthetic (LAPOP real STRATA/PSU).** Subsampling
  saturates ρ̂ at ~0.23 — the deconvolution regime is unreachable even
  semi-synthetically on survey-scale data (s_plug²=s_R²+v̄²). Adaptive holds
  coverage across the sweep. [`SEMISYNTHETIC_RESULTS.md`]

## 6. ESS and LAPOP evidence (~900)

- **6.1 The regime characterization (headline empirical finding).** Across BOTH
  surveys, BOTH estimands (levels & wave-to-wave change), and three outcomes,
  national-level cross-national inference is **low-ρ** (ρ̂≤0.20<ρ₀=0.47): between-
  country variation dwarfs within-survey design noise. So the safe procedure
  reduces to clustered PCB on all real data — validated automatically, no needless
  correction. [Fig 4 level-vs-change ρ, `lapop_level_vs_change_rho.png`]
- **6.2 LAPOP has the real design effect ESS lacks.** deff½=SD(proper PSU)/
  SD(naive) median 1.13–1.20, up to 1.9 — the proper stratified-PSU band captures
  clustering variance the naive bootstrap misses; yet certification is
  coarse-robust (design effect moves width, not the binary decision).
  [`LAPOP_EXTERNAL_VALIDATION.md`]
- **6.3 What real data validates vs simulation.** Real: reduction, target-blind
  selection, efficiency over conservative, real deff, political reclassification.
  Simulation: high-ρ deconvolution validity, the branch transition, ε_{K,B}→0.
  Strict naming (semi-synthetic, pseudo-coverage) throughout.

## 7. Political reanalysis (~500)

- **The guarantee-unit hierarchy (Fig 3, `guarantee_hierarchy.png`).** trstprl:
  any-pair 20→12; net decline 10→6; persistent country-wide 4→**1 (Greece)**;
  Bonferroni-across-countries 1. stfdem: 23→14; …; persistent →1 (Greece).
- **Headline:** *marginal wave-by-wave estimates suggest widespread democratic
  disaffection, but a country-wide simultaneous design-aware band certifies a
  persistent distribution-wide trust decline in only one country over 2018–2022.*
  Reclassified countries are the weak-signal/high-noise ones (Fig 5,
  `country_reclassification_map.png`). Terminology: "certified by plug-in,
  inconclusive under design-aware" — never "false positive" (reserved for sim).
- **Youth robustness [PENDING #6]:** age-group distributional decline, 18–29
  primary / full benchmark / 50+ contrast. [one paragraph once run]

## 8. Discussion (~300) [WRITE]

- When the method reduces to ordinary PCB (design noise small — the common case)
  and when the design-aware machinery earns its keep.
- The hard limit: without design metadata (e.g. WVS), only weights-only breadth
  replication is possible — no design-valid inference (Thm 0).
- Scope: national-level cross-national attitudes; the deconvolution regime lives
  in small/very-clustered surveys, shown in simulation.
- One line on the broader lesson: calibration targets observed through complex
  samples need this everywhere prediction-under-shift is done on survey data.

---

## Appendices (pointers)
A. Proofs (Thm 0–3′, efficiency, modulation) — `THEORY_MAIN.md` etc.
B. Finite-K correction & K-sensitivity — `FINITE_K_CORRECTION_RESULTS.md`.
C. Full simulation/semi-synthetic tables — `results/*`.
D. WVS weights-only global replication — `WVS_ROLE_REDEFINITION.md`.
E. Poverty/education breadth (original PCB) — `papers/pcb-poverty/`.
F. Preregistration trail (all protocol docs) + reproduction + `dapcb()` API.
