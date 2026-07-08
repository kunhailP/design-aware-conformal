# CLAIM LEDGER — Paper 2 truth table

Single source of truth for every headline claim: current number, where it came
from, and (after the exact-core rerun) the revised number. **No claim enters the
manuscript unless its row here is filled and its generating script is named.**

Baseline frozen at tag `v0_original` (c4f034e), working branch `pa_core_exact`.
Current numbers below were extracted from the committed `results/*.csv`
(produced by the original runs); the licensed microdata is NOT in this repo, so
the **Rerun** column stays blank until the runs are repeated on a machine that
has the data files (paths in §4).

---

## 1. Headline claims

| # | Claim | Current number | Result file | Script | Method | Rerun |
|---|-------|----------------|-------------|--------|--------|-------|
| L1 | ESS `trstprl`: persistent distribution-wide decline, design-aware | **1 country (GR)** (plug-in: 4 — BE, GB, GR, NL) | `results/ess_country_certification.csv` (`persist_da`) | `pcb/experiments/e12_ess_decline.py` | within-country studentized design bootstrap (Rao–Wu stratified-PSU), one-sided simultaneous | |
| L2 | L1 after across-country Bonferroni | **GR survives** (`persist_da_bonf`: GR) | same | same | same + Bonferroni over 30 countries | |
| L3 | ESS `stfdem`: persistent decline, design-aware | **1 country (GR)** (plug-in: 3 — DE, GR, NL) | same | same | same | |
| L4 | L3 after Bonferroni | **0 countries** (GR drops) | same | same | same | |
| L5 | WVS over-count, marginal (any-pair plug-in) vs persistent design-aware | **2.6× / 4.5× / 6.5×** (imp_dem 36→14; rej_leader 45→10; rej_army 39→6) | `results/wvs_deconsolidation.csv` | `pcb/experiments/e26_wvs_deconsolidation.py` | weights-only respondent bootstrap (no PSU ids — approximate) | |
| L6 | WVS over-count, persistent plug-in vs persistent design-aware | **1.5× / 1.2× / 1.7×** (21→14; 12→10; 10→6) | same | same | same | |
| L7 | Age robustness: GR persists in mid (30–49, trstprl), older (50+, trstprl w/ Bonferroni; stfdem), full sample; **youth 18–29: 0 countries survive design-aware** (plug-in youth: GR, HU, SE) | `results/ess_youth_certification.csv` | `pcb/experiments/e23_ess_youth.py` | same engine per age stratum | |
| L8 | Deconvolution gates never open (need gate ρ̂_LCB < ρ₀; reliability gate K < 94) | gates closed on ESS and WVS | `results/wvs_gate_probe.csv`, e12 output | `_gate_probe` in e26 / e12 | Prop 1 bound, distribution-free | |

**Wording discipline:** L5 (2.6–6.5×) is *marginal any-pair plug-in ÷ persistent
design-aware* — i.e., claim-strength escalation **and** design blindness at once.
L6 isolates design blindness alone (1.2–1.7×). The manuscript must say which
ratio it is quoting; quoting L5 while describing L6 is the kind of slip this
ledger exists to prevent.

## 2. Evidence waterfall (current, ESS, design-aware unless noted)

Counts of certified countries at each estimand strength (N=30):

| Estimand (weak → strong) | trstprl | stfdem |
|---|---|---|
| any wave-pair, plug-in | 20 | 23 |
| any wave-pair, design-aware | 12 | 14 |
| first-to-last net decline, plug-in | 10 | 13 |
| first-to-last net decline, design-aware | 6 (AT BE EE GB GR NL) | 8 (AT BE DE EE GB GR NL PT) |
| persistent trajectory, plug-in | 4 | 3 |
| persistent trajectory, design-aware | **1 (GR)** | **1 (GR)** |
| + across-country Bonferroni | **1 (GR)** | **0** |

This table is the skeleton of the waterfall figure. The political point: the
literature's modal claim ("declining trust in Europe") lives at row 1; the
defensible trajectory-wide claim lives at row 6.

## 3. Rerun decision tree (agreed 2026-07-08)

- **A. Numbers hold** → floor confirmed; selector/deconv demoted to scope;
  exact-core restructure proceeds as planned.
- **B. GR holds, WVS ratios shift** → keep GR headline; demote WVS to
  "marginal evidence systematically exceeds persistent trajectory-wide
  evidence" without the specific ×-range.
- **C. GR changes (0 or several countries)** → recenter the paper on
  *inferential escalation* (claim–estimand mismatch quantified), not "only
  Greece."
- **D. Bands too wide / nothing certifies** → revisit the estimand ladder
  (adjacent-wave persistence, net decline, minimum-duration, practical
  threshold) as *distinct estimands chosen ex ante*, never post hoc.

## 4. Rerun protocol (user's machine — data required)

Licensed microdata (never committed):

- `data/ess/Datafile-subset.dta` — ESS Data Wizard subset (incl. `agea`)
- `data/wvs/data_pa/Trends_VS_1981_2022_Stata_v4_1.dta`

Then, from the repo root on branch `pa_core_exact`:

```bash
python -m pcb.experiments.e12_ess_decline        # → L1–L4, waterfall (ESS)
python -m pcb.experiments.e26_wvs_deconsolidation # → L5, L6, L8 (WVS)
python -m pcb.experiments.e23_ess_youth          # → L7
```

Paste the refreshed `results/ess_country_certification.csv`,
`results/wvs_deconsolidation.csv`, `results/ess_youth_certification.csv` and
fill the **Rerun** column. Two-instrument caveat (THEOREM_AUDIT §0): these
headlines come from the within-country design-bootstrap engine; the exact
unstudentized conformal band (Thm 3) is the *transport* instrument and is
validated separately (e9, e25, e28) — do not relabel one as the other.
