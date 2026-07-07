# PA Novelty Risk Assessment — is this a professor-grade PA paper?

Status: Gate 5A verdict, 2026-07-06. Non-defensive by instruction. Inputs:
`docs/NOVELTY_MATRIX.md`, `docs/THEOREM_CANDIDATES.md`, the four literature
surveys, and Gate 1–4 results.

## 1. The blunt question: is trajectory PCB a direct application of functional conformal?

**Largely yes, and we should stop pretending otherwise.** The honest reading of
the matrix:

- Diquigiovanni–Fontana–Vantini (JMVA 2022) already build a finite-sample
  simultaneous band from a nonconformity score that is a **max over a discrete
  index j AND over a functional argument t**: `R = sup_j sup_t |y_j−μ̂_j|/s_j`.
  Our trajectory score `R_c = max_r max_t |E_{c,r}|/s_r` is *the same object*
  with j renamed r.
- The one thing DFV does not supply — that the discrete index is an
  **exchangeable trajectory** rather than fixed heterogeneous components, and
  that the exchangeable unit is a **group/country** — is supplied wholesale by
  Dunn–Wasserman–Ramdas (2022): groups exchangeable, unequal within-group
  counts, finite-sample validity for a new group.
- So "threshold → curve → trajectory" is the **composition of two existing
  results**. It is a correct, useful, non-trivial composition (nobody has
  written it down for repeated cross-national surveys, and the empirics are
  clean), but a Political Analysis referee who knows this literature will call
  it an application. On its own it is a **6/10 methods contribution**, exactly
  as feared.

The empirical findings around it are stronger than the method:
- Prop 1 (round-level validity ≠ trajectory validity), with the 42.9%/54.3%
  collapse vs 0.89^7, is a genuinely useful diagnostic — but as *theory* it is
  the Šidák/pointwise-vs-simultaneous argument one level up, i.e. also known
  machinery.

**Conclusion:** trajectory PCB is the *setting and the motivation*, not the
novelty. Leading with it invites desk-reject framing.

## 2. Where the real novelty is (confirmed empty cells)

Two contributions fill cells that **no paper in a ~35-paper sweep occupies**:

**(N1) Design-aware clustered conformal — the calibration units are themselves
survey estimates carrying design variance.** Matrix answer (a) from the
clustered survey: *no* paper combines complex-survey-design uncertainty with
cross-population conformal. Wieczorek (design-based CP) is single-population,
scalar, same-population test point; DWR is clean-i.i.d.-within-group; the
noisy-calibration papers (Feldman 2022, Sesia 2025, Uncertain Imputation 2025)
are individual-level with global or adversarial noise, never known
per-unit heteroskedastic design variance. This intersection is **empty**, and
we already have a working prototype (E6) and a dominance-based validity route.
**This is the paper's methodological center.**

**(N2) Quantified self-inclusion (in-sample modulation) undercoverage — Prop 3.**
Matrix answer (b) from the functional survey: the DFV papers force the
modulation onto the training split *to avoid* self-inclusion and **never
quantify the penalty**; no functional-conformal paper does. Our E10 quantifies
it (K × slicing-granularity), and the result generalizes to all studentized
functional conformal, not just surveys. **Low novelty-risk, high citability,
and it is done — the experiment already ran.**

Two more are open but weaker:
- (N3) Irregular-length validity via mask-conditional / Mondrian routes —
  *application* of Fan et al. 2025 + Vovk 2012 to a new unit; necessity high,
  novelty moderate.
- (N4) Reject-option under shift — incremental over Wang–Goel 2026 +
  García-Galindo 2025; robustness section, not a headline.

## 3. Verdict — do we pivot?

**No full pivot; a re-centering.** The phenomenon and data are good, the
composition (trajectory PCB) is real but not enough, and there are two
genuinely empty cells adjacent to what we have already built. The move is to
**demote trajectory PCB to the setting and promote design-aware + Prop 3 to the
contribution.** Concretely the paper becomes:

> **The Wrong Unit of Uncertainty: Design-Aware Clustered Conformal Inference
> for Repeated Cross-National Surveys.** Population is the exchangeable unit;
> the calibration curves are survey estimates carrying design variance; the
> band is simultaneous over a country's (rounds × thresholds) and transports to
> unseen countries, future waves, and new regions, with an abstention
> certificate. Contributions: (N1) a design-aware clustered band with
> finite-sample validity under a design-bootstrap uncertainty set [empty cell];
> (N2) an exact account of when estimated modulation destroys coverage [empty
> cell]; (N3) conditional validity for irregular survey panels; and the
> diagnosis that round-level validity is not trajectory validity.

This is a professor-grade PA paper *if* N1 gets a real theorem (not just the E6
prototype) and the substantive result lands. It is still a good
JSSAM/Survey-Methodology paper if N1's theorem proves only conditional/
approximate.

## 4. Honest scorecard (professor-grade PA bar)

| dimension | trajectory-PCB-only (current) | re-centered (N1+N2 lead) |
|---|---|---|
| problem diagnosis | 8.5 | 8.5 |
| empirical clarity | 9 | 9 |
| implementation/reproducibility | 9 | 9 |
| methodological novelty vs literature | **5.5–6** | **7.5–8** |
| theoretical depth | 6 | 7.5 (needs N1 theorem) |
| political-science payoff | 4.5–5 | **still 4.5–5 — unaddressed** |
| **PA completeness** | **~6/10** | **~7.5/10, conditional on two deliverables** |

## 5. The two things that actually gate a top-tier outcome

Re-centering fixes novelty and theory. It does **not** fix the two lowest cells,
and these — not more methods — now gate the ceiling:

1. **N1 needs a theorem, not a prototype.** The E6 worst-case/studentized bands
   work empirically; the paper needs the finite-sample statement (dominance form
   in THEOREM_CANDIDATES.md §A) proved, with β spent honestly from α. This is
   Gate 5B/5C.
2. **The political-science payoff is still a 5.** A methods-only PA paper does
   not clear the top tier. The substantive result (persistent-low-trust
   trajectory certification; or a reanalysis where trajectory+design uncertainty
   overturns an apparently settled cross-national comparison — the Foa–Mounk
   deconsolidation debate remains the highest-leverage target) is the difference
   between "clever method" and "paper political scientists cite." This is
   unstarted and is the real risk to the professor-grade goal.

## 6. Recommended next gates (unchanged order, re-scoped)

- **Gate 5B — theorem-first design doc** for N1 (data-generating hierarchy,
  what is random, where design variance enters, exact statement, counterexample)
  and the formal Prop 3 statement. No code.
- **Gate 5C — simulation** confirming N1's β-accounting and Prop 3's rate,
  extending the E6/E10 grids.
- **Gate 5D — ESS + WVS** empirics under the re-centered method, then the
  substantive reanalysis.
- Predictors, weighted/abstention (N3/N4) fold in as robustness, not as new
  headline gates.

## 7. One-line answer for the user

The phenomenon is real and the trajectory band is publishable, but **as the
headline it is a 6/10 application of DFV-JMVA + Dunn–Wasserman–Ramdas**;
re-center on design-aware clustered conformal (empty cell) plus the quantified
modulation-undercoverage result (empty cell), prove the design-aware theorem,
and land one substantive reanalysis — that is the path from "good seed" to a
paper professors submit to PA.
