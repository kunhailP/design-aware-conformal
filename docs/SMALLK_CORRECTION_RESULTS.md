# Small-K base-band correction — results (E25)

Run once on the preregistered fresh grid (`SMALLK_CORRECTION_PREREG.md`), reported
exactly as produced. `results/smallk_validation.csv`. 120 cells, 3000 reps each.

## Preregistered criteria — outcome

| criterion | target | result |
|---|---|---|
| **C1 exact validity** | U0 ≥ Vovk floor ⌈(1−α)(K+1)⌉/(K+1) − 2·MC-SE, all cells | **PASS** |
| **C2 closes the gap** | U0 ≥ 0.88 for K≥20 **and** U0 ≥ S2 everywhere | **PASS** (U0 worst 0.893) |
| **C3 bounded width** | U0 mean width ≤ 1.10 × S2, **all** cells | **FAIL** (max 1.404) |

**Verdict as preregistered: C3 failed → U0 is not "validated-clean" under the strict
letter of the prereg.** Reported honestly; the goalpost is not moved.

## What actually happened

- **Validity is exact and the gap is closed.** S2 (the studentized base band the holdout
  deployed) undercovers to **0.802** (weak dependence, K=15) and 0.839 (K=30); U0's worst
  cell over all 120 is **0.893**, and every U0 cell sits at or above its distribution-free
  Vovk floor. U0 ≥ S2 in every single cell. The small-K hole is closed by construction.
- **The C3 failure is confined and diagnosable.** Only **5 of 120** cells exceed the 1.10
  width ratio, and **all 5 are at K=15** (the smallest K) on **heavy-tailed / irregular-
  length / weak-dependence** curves (max 1.404, heavy_tail_country K=15). In exactly those
  cells S2 "saves" width only by **undercovering** (0.866 there vs U0's 0.930) — its
  studentization exploits a per-country heavy tail that also makes it invalid. On the
  seven ~homoskedastic families the width ratio is ≤ 1.082 (mean 1.032).
- **On the real deployment data the width cost is within bound.** Real ESS full-sample
  LOCO transport bands (K=33): U0/S2 width = **1.024 (trstprl), 1.051 (stfdem)** — inside
  the 1.10 target. Real trust-CDF transport errors are ~homoskedastic across the low-trust
  core, so U0's constant-width band is competitive (consistent with E10, which found U0
  the narrowest variant on ESS).

## Honest reading

U0 delivers what the correction was for: a **finite-sample-exact ≥ 1−α guarantee at any
K**, closing the base-band small-K undercoverage the holdout exposed (0.802/0.843 → 0.893
worst), at ≤ 5% width on real data. Its only width premium above the preregistered 1.10
appears on **adversarial synthetic heavy-tailed curves at K=15** — where the studentized
alternative it is compared against is itself invalid, so the comparison is apples-to-
oranges. The strict prereg criterion C3 (≤ 1.10 on *all* synthetic cells) was, in
hindsight, mis-specified: it asked an exact constant-width band to match a per-threshold-
adaptive band's width on curves engineered to reward adaptivity.

**Decision surfaced to the PI (not auto-resolved, since a preregistered criterion
failed):**
1. **Adopt U0** as the deployed base band, documenting the C3 sim failure transparently
   and resting the width claim on the real-data arm (1.02–1.05) and the ~homoskedastic
   families (≤1.08). Rationale: the deployment target is real cross-national survey CDFs;
   U0 is the only base band with an unconditional any-K guarantee; where it is wider, the
   studentized alternative is invalid. *(recommended)*
2. **Keep S2**, and state the small-K undercoverage as an explicit scope condition
   (leaves the 0.843/0.802 hole open — weaker).
3. **Pursue an exact-and-adaptive band** under a new preregistration (e.g. split "S1", or
   studentization from an independent scale) to also win width on heavy-tailed curves —
   more work, uncertain payoff at K=15.

No code was changed in `dapcb` pending this decision.
