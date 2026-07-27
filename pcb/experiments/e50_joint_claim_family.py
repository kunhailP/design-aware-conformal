"""E50 — the whole claim family from one band (ESS, rounds 1-11).

Replaces the per-family certification of E36/E43/E45 with a single simultaneous
band over every ordered contrast of a country's trajectory, at one critical
value. Every rung, every sub-span, and both directions are then read off that
one coverage event: the joint statement costs one alpha in total, not one alpha
per family, and the sub-span fraction and the endpoint-robustness statement stop
being sweeps of marginal tests.

Reports, per country and outcome:
  net / persistent / any-pair       -- the same rungs, now jointly certified
  n_declining / n_rising / n_spans  -- every ordered contrast, one guarantee
  frac_spans_declining              -- the endpoint-free erosion index
  episodic                          -- a certified decline AND a certified rise,
                                       both inside the same band
  net_lower                         -- certified span magnitude

Output: results/ess_joint_claims.csv
Run:    python -m pcb.experiments.e50_joint_claim_family   (~40 min)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
from pcb.inference.claim_family import certify_claim_family
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)

OUTCOMES = ("trstprl", "stfdem")
MIN_N = 100


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    kl = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows = []
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            usable = [r for r in sorted(csub.essround.unique())
                      if kl.get((c, r)) in ("core", "extended")]
            if len(usable) < 3:
                continue
            rng = np.random.default_rng(det_seed("e50", outcome, c))
            F, B, rr = [], [], []
            for r in usable:
                y, w, s, p = _round_stats(csub[csub.essround == r], outcome)
                if len(y) < MIN_N:
                    continue
                F.append(_wcdf(y, w))
                B.append(_design_boot(y, w, s, p, rng) if kl.get((c, r)) == "core"
                         else _naive_boot(y, w, rng))
                rr.append(int(r))
            if len(rr) < 3:
                continue
            res = certify_claim_family(np.array(F), np.stack(B, 1), ALPHA, CORE_T)
            rows.append(dict(outcome=outcome, cntry=c, n_rounds=len(rr),
                             r_first=rr[0], r_last=rr[-1], c=round(res["c"], 3),
                             net=res["net"], persistent=res["persistent"],
                             any_pair=res["any_pair"], episodic=res["episodic"],
                             n_spans=res["n_spans"], n_declining=res["n_declining"],
                             n_rising=res["n_rising"],
                             frac_declining=round(res["frac_spans_declining"], 3),
                             net_lower=round(res["net_lower"], 4)))
            print(f"{outcome:8s} {c}: c={res['c']:.2f}  net={res['net']}  "
                  f"persist={res['persistent']}  spans {res['n_declining']}"
                  f"/{res['n_spans']} down, {res['n_rising']} up")
    d = pd.DataFrame(rows)
    d.to_csv("results/ess_joint_claims.csv", index=False)

    print("\n=== one band, one guarantee (alpha=0.10, joint over every contrast "
          "and both directions) ===")
    for outcome in OUTCOMES:
        p = d[d.outcome == outcome]
        print(f"\n{outcome}: {len(p)} countries")
        print(f"  net span certified : {int(p.net.sum()):2d}  "
              f"-> {sorted(p.cntry[p.net])}")
        print(f"  persistent         : {int(p.persistent.sum()):2d}")
        print(f"  any adjacent pair  : {int(p.any_pair.sum()):2d}")
        print(f"  episodic (both directions inside one band): "
              f"{int(p.episodic.sum()):2d}")
        top = p.nlargest(6, "frac_declining")[["cntry", "frac_declining",
                                               "n_declining", "n_spans"]]
        print("  erosion index (share of contrasts certified declining):")
        print("   ", ", ".join(f"{r.cntry} {r.frac_declining:.2f}"
                               for r in top.itertuples()))
        print(f"  zero certified contrasts: "
              f"{sorted(p.cntry[p.n_declining == 0])}")


if __name__ == "__main__":
    main()
