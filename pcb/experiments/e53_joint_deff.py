"""E53 — design-effect sensitivity of the JOINT certified set.

E44 stress-tested the weights-only rounds against the per-family construction,
which certifies a nine-country span set on a 34-country universe. The main text
now reports the eight-country set from the joint band (E50), so that robustness
check does not describe the table it was being used to caption. This rerun
applies the same inflation -- F + sqrt(deff)*(F_b - F) on the rounds-1-8 cells
only -- inside the joint construction, and reports where each certification
breaks.

Output: results/joint_claims_deff.csv
Run:    python -m pcb.experiments.e53_joint_deff   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

import pcb.experiments.e50_joint_claim_family as e50

DEFFS = (0.6, 0.8, 1.0, 1.2, 1.3, 1.5, 2.0)


def main():
    os.makedirs("results", exist_ok=True)
    rows = []
    for deff in DEFFS:
        e50.DEFF_EXTENDED = deff
        out = "results/_tmp_joint.csv"
        real = "results/ess_joint_claims.csv"
        keep = pd.read_csv(real) if os.path.exists(real) else None
        e50.main()
        d = pd.read_csv(real)
        d.insert(0, "deff", deff)
        rows.append(d)
        if keep is not None and deff == DEFFS[-1]:
            keep.to_csv(real, index=False)      # restore the shipped run
    e50.DEFF_EXTENDED = 1.0
    t = pd.concat(rows, ignore_index=True)
    t.to_csv("results/joint_claims_deff.csv", index=False)
    print("\n=== joint-band net set under weights-only design-effect inflation ===")
    for oc in e50.OUTCOMES:
        base = set(t[(t.deff == 1.0) & (t.outcome == oc) & t.net].cntry)
        print(f"\n{oc}: base {sorted(base)}")
        for deff in DEFFS:
            s = set(t[(t.deff == deff) & (t.outcome == oc) & t.net].cntry)
            drop = sorted(base - s)
            print(f"  deff {deff}: {len(s)} certify"
                  + (f"   lost: {drop}" if drop else "   (set intact)"))
    if not t.empty:
        print("\nper-country net lower bound by deff (trstprl):")
        piv = (t[t.outcome == "trstprl"]
               .pivot_table(index="cntry", columns="deff", values="net_lower"))
        print(piv.round(4).to_string())


if __name__ == "__main__":
    main()
