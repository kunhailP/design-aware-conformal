"""E42 — real-data severity injection: what each rung can detect against the
ACTUAL ESS design noise (paper §5).

E32 gives the power curve of each rung under simulated ESS-like design noise
(threshold SE 0.012). Here we measure the same curves against the real thing:
for every core country-pair (rounds 9-11), inject a known persistent decline of
delta CDF points across the low-trust core and rerun the exact certification
machinery with the country's own stratified-PSU bootstrap draws.

Injection semantics (this is the delicate part). `certify_decline_differences`
certifies when D_hat - c*sd >= 0 with c the (1-alpha) quantile of the
*studentized* bootstrap deviations (db - dh)/sd. A shift of the estimand moves
the point estimate AND travels with the bootstrap distribution centred on it:
so the injection must be added to `dh` and to `db` alike. Adding it only to
`dh` (as an earlier version of this script did) lowers c by delta/sd while
raising the margin by delta -- counting the injection twice and overstating
power by roughly a factor of two in delta.

Two designs are reported, because they answer different questions:

  POWER (primary, null-imposed, Monte Carlo).  A power curve needs a known
  truth AND a randomly drawn estimate: fixing D_hat at the truth makes
  certification the deterministic event delta >= c*max sd, which is a
  minimum-detectable-effect calculation, not power (and returns a structural
  0.000 at delta=0 for any data and any alpha -- not a size estimate). We
  therefore keep each country-pair's real design-noise structure and, per
  replicate, draw the estimation error from its own bootstrap:
      e_b   = db[b] - dh                      (a draw of D_hat - D)
      D_hat = delta*inj + e_b                 (estimate under the injected truth)
      draws = D_hat + (db - dh)               (bootstrap recentred on it)
  At delta=0 the certification rate is then the honest realized size; at
  delta>0 it is the rung's power against a known persistent decline of that
  size, at real ESS design noise.

  DETECTION (secondary, additive).  dh <- dh + delta*inj, db <- db + delta*inj:
  the injected decline on top of whatever each country actually did. At
  delta=0 this is the observed certification rate. This measures how much
  extra decline it would take to bring the certified set to a given size, not
  the rung's power.

Rungs, each built exactly as the deployed instrument builds it:
  pair       : one adjacent-round difference at a time;
  persistent : one simultaneous band over ALL adjacent pairs x core thresholds;
  net        : the DIRECT first-to-last span contrast (not a sum of adjacent
               pair draws -- summing re-resamples the interior rounds and
               inflates the variance to V(F_9)+2V(F_10)+V(F_11) instead of the
               telescoped V(F_9)+V(F_11) the deployed net band uses).

Output: results/real_severity.csv
Run:    python -m pcb.experiments.e42_real_severity   (~30 min)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
import pcb.experiments.e13_ess_audit as e13
from pcb.experiments.e12_ess_decline import ALPHA, CORE_T
from pcb.inference.decline_certify import certify_decline_differences

DELTAS = (0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.12)
OUTCOME = "trstprl"
REPS = 200          # Monte Carlo replicates per country in the power design


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    inj = np.where(CORE_T, 1.0, 0.0)
    cells = []          # (cntry, [(dh, db) per adjacent pair], (dh_net, db_net))
    for c, csub in df.groupby("cntry", observed=True):
        core_rounds = [r for r in sorted(csub.essround.unique())
                       if klass.get((c, r)) == "core"]
        pairs = [(r, r + 1) for r in core_rounds if r + 1 in core_rounds]
        if not pairs:
            continue
        rng = np.random.default_rng(det_seed("e42", OUTCOME, c))
        pp = []
        for r0, r1 in pairs:
            out = e13._pair_diff(csub[csub.essround == r0],
                                 csub[csub.essround == r1], OUTCOME, rng)
            if out is not None:
                pp.append(out)
        if not pp:
            continue
        # direct first-to-last span contrast, as the deployed net band builds it
        net = e13._pair_diff(csub[csub.essround == core_rounds[0]],
                             csub[csub.essround == core_rounds[-1]], OUTCOME, rng)
        cells.append((c, pp, net))
    n_pairs = sum(len(pp) for _, pp, _ in cells)
    n_net = sum(1 for _, _, net in cells if net is not None)
    print(f"{len(cells)} countries, {n_pairs} adjacent pairs, {n_net} with a "
          f"direct span contrast; injecting persistent declines of delta CDF "
          f"points over the preregistered core\n")

    rng = np.random.default_rng(det_seed("e42", "montecarlo"))
    rows = []
    for design in ("power", "detection"):
        blurb = ("null-imposed Monte Carlo: truth = injection, estimate drawn "
                 f"from the country's own bootstrap, {REPS} reps"
                 if design == "power"
                 else "additive: injection on top of the observed decline")
        print(f"\n--- {design} ({blurb}) ---")
        for delta in DELTAS:
            pair_hits = persist_hits = net_hits = 0
            pair_n = persist_n = net_n = 0
            for c, pp, net in cells:
                if design != "power":
                    H = np.array([dh + delta * inj for dh, _ in pp])
                    Bd = np.moveaxis(
                        np.array([db + delta * inj for _, db in pp]), 1, 0)
                    pair_hits += sum(
                        certify_decline_differences(H[[i]], Bd[:, [i]], ALPHA,
                                                    CORE_T)["design_aware"]
                        for i in range(len(pp)))
                    pair_n += len(pp)
                    persist_hits += certify_decline_differences(
                        H, Bd, ALPHA, CORE_T)["design_aware"]
                    persist_n += 1
                    if net is not None:
                        dh_n, db_n = net
                        acc = delta * len(pp)
                        net_hits += certify_decline_differences(
                            (dh_n + acc * inj)[None], (db_n + acc * inj)[:, None],
                            ALPHA, CORE_T)["design_aware"]
                        net_n += 1
                    continue
                # --- power: redraw the estimate each replicate -----------------
                B = pp[0][1].shape[0]
                for _ in range(REPS):
                    idx = rng.integers(0, B)
                    H, Bd_list = [], []
                    for dh, db in pp:
                        err = db[idx] - dh                    # a draw of D_hat - D
                        Dhat = delta * inj + err
                        H.append(Dhat)
                        Bd_list.append(Dhat[None, :] + (db - dh[None]))
                    H = np.array(H)
                    Bd = np.moveaxis(np.array(Bd_list), 1, 0)
                    pair_hits += sum(
                        certify_decline_differences(H[[i]], Bd[:, [i]], ALPHA,
                                                    CORE_T)["design_aware"]
                        for i in range(len(pp)))
                    pair_n += len(pp)
                    persist_hits += certify_decline_differences(
                        H, Bd, ALPHA, CORE_T)["design_aware"]
                    persist_n += 1
                    if net is not None:
                        dh_n, db_n = net
                        acc = delta * len(pp)
                        err = db_n[idx] - dh_n
                        Dn = acc * inj + err
                        net_hits += certify_decline_differences(
                            Dn[None], (Dn[None, :] + (db_n - dh_n[None]))[:, None],
                            ALPHA, CORE_T)["design_aware"]
                        net_n += 1
            rows.append(dict(design=design, delta=delta,
                             pair_rate=round(pair_hits / max(pair_n, 1), 3),
                             net_rate=round(net_hits / max(net_n, 1), 3),
                             persist_rate=round(persist_hits / max(persist_n, 1), 3)))
            print(f"delta={delta:.2f}: pair {rows[-1]['pair_rate']:.3f}  "
                  f"net {rows[-1]['net_rate']:.3f}  "
                  f"persist {rows[-1]['persist_rate']:.3f}")
    res = pd.DataFrame(rows)
    res.to_csv("results/real_severity.csv", index=False)
    print("\ndelta = per-pair decline in CDF points over the core; the net row "
          "accumulates it over the span.\npower/delta=0 is the realized size "
          "(nominal 0.10); detection/delta=0 is the observed certification rate."
          "\nE32's simulation at SE 0.012 predicted 80% power at net 0.02-0.03 "
          "and persistent 0.06-0.08 per pair.")


if __name__ == "__main__":
    main()
