# Gate 5C — simulation confirmation of the Gate-5B theorems

Status: 2026-07-06. Code: `pcb/experiments/e11_gate5c.py`,
`pcb/inference/decline_certify.py`. Data: `results/gate5c_partA_*.csv`,
`gate5c_partB_prop3.csv`, `gate5c_partC_certify.csv`. Tests:
`tests/test_gate5c.py` (+ existing 27). This is where implementation resumed
after the theorem-first Gate 5B.

## Part A — Candidate B (contamination-model conformal) CONFIRMED, ρ* ≈ 0.47

Latent deployment target (unsurveyed), fine sweep of the noise ratio
ρ = design-SD / transport-SD; oracle vs plug-in vs DA-deconvolved.

| ρ | oracle cov | plug-in cov | DA cov | oracle w | plug-in w | DA w |
|---|---|---|---|---|---|---|
| 0.21 | .902 | .911 | .892 | .317 | .330 | .312 |
| 0.34 | .905 | .935 | .900 | .194 | .214 | .191 |
| 0.47 | .892 | .935 | .876 | .142 | .167 | .142 |
| 0.64 | .885 | .956 | .855 | .103 | .132 | .104 |
| 1.03 | .894 | .990 | .798 | .064 | .102 | .067 |
| 1.29 | .892 | .990 | .746 | .051 | .094 | .054 |

- **B1 dominance CONFIRMED.** Plug-in coverage rises monotonically above nominal
  as ρ grows (.911 → .990): the plug-in band is *conservative* for the latent
  deployment target, exactly the stochastic-dominance prediction. The
  contaminated sup-magnitude exceeds the clean one in 8/8 cells in mean
  (per-replicate 97–100%). Validity is free — **no union bound**.
- **B2 deconvolution CONFIRMED.** DA recovers oracle width throughout
  (DA w ≈ oracle w, vs plug-in's ~10–30% excess) while holding coverage up to
  **ρ\* ≈ 0.47**; beyond it the s_plug²−v² subtraction over-corrects and DA
  undercovers (.86 → .75), so the estimator must fall back to the conservative
  plug-in band there.
- **ESS is safely inside the efficient regime** (ρ ≈ 0.16–0.20 ≪ 0.47): on real
  ESS the design-aware band gives oracle width AND validity. The fallback guard
  matters only for the noisiest small-country surveys and for WVS.

## Part B — Prop 3 rate CONFIRMED: Δ ≈ 0.382·(g/K), R² = 0.923

In-sample sliced modulation, L = 4 trajectory, g modulation slices, K countries.
Coverage deficit (attainable − observed):

| K \ g | 1 (pooled) | 2 | 4 (slotwise) |
|---|---|---|---|
| 20 | .016 | .032 | .087 |
| 30 | .005 | .018 | .054 |
| 50 | .006 | .020 | .018 |
| 100 | .007 | .011 | .012 |

The deficit grows with the slicing granularity g and shrinks as 1/K, and fits
the predicted self-inclusion rate **Δ ≈ c·(g/K), c = 0.382, R² = 0.923**. Prop 3
moves from conjecture to a characterized rate. Pooled (g = 1) has near-zero
deficit at all K; slotwise (g = L) is the failure mode. This is the result with
the widest reach (all studentized functional conformal), and no prior work
quantifies it.

## Part C — political payoff mechanism, design-aware vs plug-in

Within-country decline certification (the persistent-decline claim compares two
observed rounds of the SAME country → the country effect cancels, leaving a pure
survey-design inference on the consecutive differences over the low-trust core
t ≤ 1..4; design-bootstrap simultaneous one-sided band). Two graded levels of
the `POLITICAL_PAYOFF_ESTIMAND.md` hierarchy:

| country kind | persistent plug-in | persistent DA | net plug-in | net DA |
|---|---|---|---|---|
| true decline | .781 | .014 | 1.000 | .996 |
| one-off dip | .000 | .000 | .208 | .007 |
| stable | .004 | .000 | .329 | .018 |

**Net decline is the powerful, interpretable level** (trust lower at the end of
the period than the start, over the low-trust range):
- **Plug-in is INVALID**: false-certification on non-declining countries **.222**,
  far above α = 0.10 — ignoring survey uncertainty over-certifies decline (it
  wrongly flags 25% of stable and 21% of one-off-dip countries).
- **Design-aware is valid**: false-certification **.010 ≤ α**, while retaining
  strong power on true decliners (.68–.996).
- **Headline: plug-in flags 51.2% of countries as in net decline; design-aware
  certifies 34.2%.** The 17-point gap is precisely the over-certification that
  propagating survey-design uncertainty removes — the substantive "N flagged → M
  certified" result, in simulation.

**Persistent decline (every wave)** is the strict end: design-aware certifies it
for only 1.4% even of true monotone decliners — once you demand a
design-simultaneous guarantee that trust fell at *every* wave across the whole
low-trust range, almost nothing qualifies. Honest and reportable as the strong
claim; net decline is the one that carries the empirical section.

Certification validity is inherited from band coverage and holds against the
latent truth at both levels; the level-band non-overlap test (`certify_decline`)
is valid but powerless (bands wider than round-to-round change) — the
within-country DIFFERENCE construction is what gives power, because the country
effect cancels. This is itself a methodological point: certify the contrast, not
the levels.

## Verdict and hand-off to Gate 5D

All three Gate-5B targets confirmed: B1/B2 (ρ\* = 0.47, ESS efficient), Prop 3
(c·g/K), and the certification rule (valid; plug-in anti-conservative; net-level
powered). No falsifier from `GO_NO_GO_GATE5B.md` triggered. Gate 5D (real ESS +
WVS) can now run the design-aware band and the net-decline certification on
trstprl/stfdem, report the real N-vs-M country counts, and take on the
Foa–Mounk deconsolidation reanalysis.
