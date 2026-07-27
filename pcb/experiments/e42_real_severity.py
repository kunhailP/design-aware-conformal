"""E42 — the promised real-data severity injection (paper §5).

E32 gives the power curve of each rung under simulated ESS-like design noise
(threshold SE 0.012). Here we measure the same curves against the REAL design
noise: for every core country-pair (rounds 9-11), inject a known persistent
decline of delta CDF points across the low-trust core into the observed
difference (dh + delta on core thresholds) and rerun the exact certification
machinery with the country's own stratified-PSU bootstrap draws. Detection rate
across (country, pair) cells at each delta is the real-data power of the pair
rung; injecting into ALL of a country's pairs gives the persistent rung; the
first-to-last span gives the net rung.

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

DELTAS = (0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08)
OUTCOME = "trstprl"


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    inj = np.where(CORE_T, 1.0, 0.0)
    cells = []          # (cntry, [(dh, db) per pair])
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
        if pp:
            cells.append((c, pp))
    n_pairs = sum(len(pp) for _, pp in cells)
    print(f"{len(cells)} countries, {n_pairs} pairs; injecting persistent "
          f"declines of delta CDF points over the preregistered core\n")

    rows = []
    for delta in DELTAS:
        pair_hits = persist_hits = net_hits = 0
        for c, pp in cells:
            H = np.array([dh + delta * inj for dh, _ in pp])
            Bd = np.moveaxis(np.array([db for _, db in pp]), 1, 0)
            pair_hits += sum(
                certify_decline_differences(H[[i]], Bd[:, [i]], ALPHA, CORE_T)
                ["design_aware"] for i in range(len(pp)))
            persist_hits += certify_decline_differences(H, Bd, ALPHA, CORE_T)[
                "design_aware"]
            # net over the span: sum of injected pair differences
            net_hits += certify_decline_differences(
                H.sum(0, keepdims=True), Bd.sum(1, keepdims=True), ALPHA,
                CORE_T)["design_aware"]
        rows.append(dict(delta=delta, pair_rate=round(pair_hits / n_pairs, 3),
                         net_rate=round(net_hits / len(cells), 3),
                         persist_rate=round(persist_hits / len(cells), 3)))
        print(f"delta={delta:.2f}: pair {rows[-1]['pair_rate']:.2f}  "
              f"net {rows[-1]['net_rate']:.2f}  "
              f"persist {rows[-1]['persist_rate']:.2f}")
    res = pd.DataFrame(rows)
    res.to_csv("results/real_severity.csv", index=False)
    print("\n(delta=0 row = the observed certification rates, no injection; "
          "E32 simulation predicted 80% power at net 0.02-0.03, "
          "persistent 0.06-0.08)")


if __name__ == "__main__":
    main()
