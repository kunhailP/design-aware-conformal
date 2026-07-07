# Go / No-Go — Gate 5B verdict

Status: 2026-07-06. Decision on whether design-aware clustered conformal (N1) is
a standalone methodological contribution or collapses to trivial inflation.
Inputs: `DESIGN_AWARE_FORMAL_SETUP.md`, `DESIGN_AWARE_METHOD_CANDIDATES.md`,
`DESIGN_AWARE_PROOF_SKETCHES.md`, `POLITICAL_PAYOFF_ESTIMAND.md`, and E6/E8–E10.

## Decision criteria (set in advance, setup §6/§7)

A candidate is a real contribution iff it (1) reduces to clustered PCB at v=0,
(2) covers the LATENT trajectory, (3) is NOT a K-fold union bound, (4) beats the
trivial [0,1] band non-trivially, (5) separates country exchangeability from
within-country design, (6) handles irregular rounds at least conditionally, and
(7) is honest in the ESS small-PSU regime.

## Verdict table

| candidate | (1) | (2) | (3) | (4) | (5) | (6) | (7) | outcome |
|---|---|---|---|---|---|---|---|---|
| A worst-case | ✓ | ✓ | ✗ | ~ | ✓ | ~ | ✓ | **baseline only** — fails (3), the union bound |
| **B contamination** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **GO — primary method** |
| C two-stage p-value | ✓ | ✓ | ✓ | ✓ | ✓ | ~ | ✗ | **appendix ideal** — fails (7), asymptotic in PSU |

## Ruling

**GO on Candidate B as the paper's methodological center.** It clears every
criterion: validity for the latent deployment trajectory comes from a
stochastic-dominance argument (exact under Gaussian design noise, else an
explicit estimable ε-correction) with **no union bound**; efficiency comes from
deconvolving the known survey variance out of the score scale, recovering oracle
width, guarded by an honest fallback to the conservative plug-in band when the
noise ratio is too high. It reduces exactly to the frozen clustered PCB at v=0.
The construction is empirically pre-validated (E6: conservative on deployment,
nominal in both views after the v-correction), so the theorem-first work is
confirming a measured effect, not hoping for one.

**A** is retained only as the conservative upper envelope that demonstrates the
cost of the naive union-bound combination — the thing B beats. **C** is retained
as a clean-theory appendix (exact under a design-p-value oracle) but its
exactness is illusory at ESS PSU counts, so the paper does not stand on it.

## Conditions that would flip this to NO-GO / pivot (stated honestly)

The GO is conditional. Revert to a pivot if Gate 5C shows any of:
- the B1 dominance condition (D) fails empirically on realistic ESS design noise
  AND the TV ε-correction is so large that B collapses to A's width;
- the B2 deconvolution guard threshold ρ* is so low that on ESS (ρ ≈ 0.16–0.20,
  so this is unlikely) the efficient regime is empty and B is only the
  conservative plug-in — in which case N1 adds validity accounting but no
  performance, and the paper leans on N2 + the political result instead;
- Prop 3's Δ(K,g) rate does not match the c·g/K expansion (would demote N2 from
  theorem to empirical observation).
None of these is expected given E6/E10, but they are the falsifiers.

## The two things that gate 9+ (unchanged, now scheduled)

1. **B's theorem, proved.** Sketch B1/B2 → a stated finite-sample proposition
   with condition (D) and the ρ* guard. Gate 5C simulation sets ρ* and confirms
   dominance + the width→oracle rate.
2. **The substantive result, landed.** `POLITICAL_PAYOFF_ESTIMAND.md`: N vs M
   persistent-decline certification on ESS, WVS/EVS replication, and the
   Foa–Mounk deconsolidation reanalysis. This, not more methods, is what carries
   a PA paper past a strong-survey-methodology paper. It remains the dominant
   risk to the 9+ target and is the reason no further method work is scheduled
   before it.

## Next gates (locked)

- **5C — simulation** (implementation resumes): extend the E6/E10 hierarchical
  DGP to (a) set ρ* and confirm B1/B2, (b) trace Δ(K,g) for Prop 3, (c) validate
  the persistent-decline certification level. This is where code returns.
- **5D — empirics**: ESS (trstprl + stfdem) under B, then WVS/EVS external
  replication and the deconsolidation reanalysis.
- Predictors (functional AR, macro GBM = unseen-country), weighted/abstention
  (region holdout), DA extreme-regime correction: fold in as robustness AFTER
  5C/5D, not before.

## Freeze

Gate 5A + 5B docs are committed under tag `gate5a-freeze` (5B docs to be added to
it). No implementation was done in 5B, per the theorem-first discipline.
