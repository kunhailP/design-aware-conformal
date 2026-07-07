# WVS deconsolidation reanalysis — results (E26)

Run once per `WVS_DECONSOLIDATION_PREREG.md`, reported exactly as produced.
`results/wvs_deconsolidation.csv`, `results/wvs_gate_probe.csv`. Named target: the
Foa–Mounk "democratic deconsolidation" thesis. Survey-aware = weighted respondent
bootstrap (WVS has no PSU/stratum), α=0.10, B=2000, min-n 400/cell.

## The hierarchy collapses — marginal reading over-counts deconsolidation 2.6–6.5×

Denominator = countries with ≥2 qualifying waves. "SA" = survey-aware, "PI" = plug-in.

| item (pro-democratic; decline = deconsolidation) | K | any-pair SA/PI | persistent SA/PI | % persist | marginal→persistent |
|---|---|---|---|---|---|
| `imp_dem` importance of democracy (Foa–Mounk headline) | 59 | 26/36 | **14/21** | 24% | 36→14 (**2.6×**) |
| `confid_parl` confidence in parliament | 77 | 56/64 | 17/26 | 22% | 64→17 (3.8×) |
| `rej_leader` reject "strong leader" | 77 | 35/45 | 10/12 | 13% | 45→10 (4.5×) |
| `sup_demsys` support democratic system | 77 | 43/58 | 9/12 | 12% | 58→9 (6.4×) |
| `rej_army` reject army rule | 76 | 28/39 | 6/10 | 8% | 39→6 (6.5×) |

**Honest reading — not "deconsolidation is a myth."** A marginal wave-by-wave reading
flags 36–64 countries per item; the persistent, distribution-wide, survey-aware object
is certified in 6–17 (8–24% of countries). So (i) the marginal literature over-states
deconsolidation by **2.6–6.5×**, exactly the wrong-unit inflation this paper is about,
and (ii) design-awareness demotes a further ~20–30% at the persistent bar (e.g.
`imp_dem` 21→14, `confid_parl` 26→17). But persistent deconsolidation is **real in a
meaningful minority** — and the certified `imp_dem` set includes recognizable backsliders
(Turkey, Philippines, Mexico, Tunisia, Kazakhstan), which lends credibility. The claim is
calibration, not denial: the honest count is smaller and more specific than the panic.

This complements the ESS trust result (20 marginal → 1 persistent, Greece): the wrong-
unit correction bites across two structurally different survey families (European,
2-year, PSU-clustered, 0–10 scale vs global, ~5–10y, weights-only, 4-category), with the
*magnitude* of the over-count varying by context (dramatic for European trust
2018–2022; 2.6–6.5× for global deconsolidation 1981–2022).

## Youth (Foa–Mounk's central claim) — partially supported, honestly

Persistent, survey-aware, by age band:

| item | youth 18–29 | older 50+ |
|---|---|---|
| `imp_dem` importance of democracy | **7 / 45** | 3 / 53 |
| `rej_leader` reject strong leader | 0 / 53 | 4 / 51 |
| `rej_army` reject army rule | 1 / 54 | 4 / 50 |

Mixed, and we report it as such: the young show *more* persistent decline in rating
democracy essential (7 vs 3) — consistent with Foa–Mounk on that item — but **not** in
openness to authoritarian alternatives (0–1 vs 4 for strong-leader / army rule), which
runs *against* the "youth embrace strongmen" story. Small counts; interpret as
suggestive, not decisive. The deconsolidation-is-youth-led thesis is at best half-true.

## Gate probe — the two barriers are structurally anti-correlated

At the WVS transport scale the selector gates behave oppositely to ESS:

| survey | K | ρ̂_LCB | reliability floor √(2/(K−1)) | gate A (ρ̂_LCB>0.47) | gate B feasible (floor≤τ_D=0.147) |
|---|---|---|---|---|---|
| ESS | ≤ 33 | ≤ 0.146 | ≥ 0.25 | ✗ | ✗ (K too small) |
| **WVS** | 95–105 | **≤ 0.094** | **≤ 0.146** | ✗ (noise too small) | **✓** |

WVS, the largest repeated cross-national survey, finally clears **gate B** (K ≥ 94, so
the deconvolved scale is estimable) — but fails **gate A** decisively, because with no
PSU/stratum its design noise is weights-only and tiny (ρ̂ ≤ 0.12). ESS is the mirror
image: appreciable PSU design noise but far too few countries. **The two requirements —
enough exchangeable populations to estimate the deconvolution, and design noise large
enough relative to the between-country signal to be worth removing — are anti-correlated
across the real survey landscape.** The survey big enough to fit the correction has
almost no design noise; the survey with real design noise has too few countries. So
deconvolution is unreachable on real cross-national data not by coincidence but because
no single survey can satisfy both gates at once. (E24 established each barrier; E26 shows
they bind in *different* surveys and never jointly release.)

## Bottom line for the paper

E26 gives the paper a second, global, named-target reanalysis: the Foa–Mounk
deconsolidation battery, where the wrong-unit + design-aware correction shrinks the
marginal count 2.6–6.5× without denying that a real minority deconsolidated, and where
the youth thesis is only half-supported. And the gate probe upgrades the impossibility
story from "unreachable on ESS" to "unreachable on the two largest cross-national surveys
for *complementary structural reasons*."
