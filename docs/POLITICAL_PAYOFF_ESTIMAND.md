# Political Payoff Estimand — distribution-wide persistent decline in trust

Status: Gate 5B, 2026-07-06. This is the substantive contribution that the
methods enable — the difference between "clever method" and "paper political
scientists cite" (`PA_NOVELTY_RISK.md` §5). It USES the trajectory band's
simultaneity; a pointwise interval or a cutoff cannot certify it.

## 1. The question

> Which democracies exhibit a *persistent, distribution-wide* decline in
> political trust — as opposed to a one-off dip, a mean shift that hides
> offsetting tail movement, or noise?

Standard practice compares mean trust, or the headcount below a cutoff, round by
round. That (a) collapses the distribution to a scalar, (b) treats each round
independently, and (c) ignores survey-design uncertainty. The trajectory band
answers the distributional, multi-round, design-aware version.

## 2. The distributional-decline hierarchy (what the band certifies)

For country c with consecutive rounds r, r+1, trust CDF F_{c,r}(t) over the
0–10 scale. A shift toward LOWER trust means more mass at low t, i.e.
first-order stochastic deterioration (FOSD-down):
  F_{c,r+1}(t) ≥ F_{c,r}(t)  for all t   (CDF moves up ⇒ distribution moves
  down). Three nested claims, each certifiable at level 1−α from ONE simultaneous
band over the country's (rounds × thresholds):

- **Persistent decline (strongest):** FOSD-down holds for EVERY consecutive pair
  across the observed trajectory — trust deteriorated at every step, over the
  whole distribution.
- **Net decline:** FOSD-down between the first and last observed round, without
  requiring monotonicity in between.
- **Partial / threshold-local decline (weakest):** F moves up on SOME sub-range
  of t but not FOSD (e.g. the middle of the scale hollows out while the tails
  hold) — a change a mean or a single cutoff would misread.

Symmetric definitions give *recovery* and *stability*; the fourth cell is
*indistinguishable* (the band admits both directions).

## 3. Certification rule (why simultaneity is essential)

The design-aware trajectory band B delivers, jointly with prob ≥ 1−α, an
interval [lo_{c,r}(t), hi_{c,r}(t)] for every θ_{c,r}(t) SIMULTANEOUSLY over
(r,t). Any ordering functional that holds for EVERY surface inside the joint band
is certified at 1−α. Concretely:

- Certify **persistent decline** iff for every consecutive pair and every t the
  band forces F_{c,r+1}(t) ≥ F_{c,r}(t) — sufficient checkable condition:
  lo_{c,r+1}(t) ≥ hi_{c,r}(t) is too strong; the correct test is that the joint
  band contains no surface violating FOSD-down, i.e. the lower feasible
  F_{c,r+1} still dominates the upper feasible F_{c,r} in the FOSD partial order
  over the band's vertices. (Exact test = linear-program / vertex check over the
  band; a conservative sufficient test = pointwise lo_{r+1}(t) ≥ hi_r(t) ∀t.)
- A **pointwise** band cannot do this: certifying a claim that is JOINT over all
  (r,t) from marginally-valid pieces undercovers exactly by the Prop-1 recursion.
  This is the methodological payoff made substantive — the same
  curve→trajectory simultaneity failure, now deciding a political classification.

## 4. The headline result the paper is aiming for

> Standard round-by-round mean analysis flags N democracies as being in
> persistent trust decline. Certifying the same claim with a simultaneous,
> design-aware trajectory band — which propagates both cross-national transport
> uncertainty and each survey's design uncertainty — confirms only M < N;
> the remaining N−M are one-off dips, offsetting tail movements, or within
> survey+trajectory uncertainty, and cannot be certified as persistent decline
> without further data.

The value is the DEMOTION as much as the confirmation: the band separates
"looks like a trust crisis" from "certifiably a distribution-wide persistent
crisis," and names which countries need another wave to decide.

## 5. Why this is design-aware, not just clustered

The countries most likely to be MIS-classified by standard analysis are exactly
the small-sample, high-design-effect ESS countries (E9 flagged GR, IS, RS, TR as
short, volatile trajectories). There the survey error S is largest relative to
the trust change, so ignoring it (plug-in) over-certifies decline. The
design-aware band (Candidate B) is what prevents a design-noise wiggle from being
read as a political trajectory — this is where N1's method and the political
result are the SAME contribution, not two bolted together.

## 6. External replication (WVS/EVS)

Repeat the certification on WVS/EVS trust / satisfaction items over a more
heterogeneous country set — not the full method redevelopment, only: does the
persistent-decline classification (and its demotions) reproduce out of the
ESS-European frame? This is where the Foa–Mounk deconsolidation debate enters:
their claim of broad democratic-support erosion is a distribution-wide,
multi-wave claim — precisely the object this band certifies or demotes. Framing
the reanalysis as "which of the contested deconsolidation claims survive a
design-aware simultaneous band" is the highest-leverage substantive target
(`PA_NOVELTY_RISK.md` §5).

## 7. What Gate 5C/5D must deliver for this to count

- 5C: confirm the certification rule's level on simulated trajectories with known
  decline/stability (the vertex/LP test achieves ≥1−α; the conservative pointwise
  test is valid but looser).
- 5D: run it on ESS (trstprl primary, stfdem replication), report N vs M with
  the exact covered-country accounting, then WVS/EVS external replication and the
  deconsolidation reanalysis.
- Report the classification with the same discipline as coverage: exact counts,
  which countries move from "declining" to "indeterminate," and why (design vs
  transport uncertainty).
