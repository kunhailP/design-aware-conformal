"""E43 — endpoint sensitivity of the net rung (long window, rounds 1-11).

A net claim is a first-to-last contrast, and a paper whose diagnosis is that
wave-pair contrasts get narrated as trends must show its own span claims are
not artifacts of which waves happen to bracket a country's participation. For
every country we re-certify the net rung over EVERY admissible sub-span
(first' <= last', spanning at least MIN_STEPS adjacent steps), and record:

  net_full        : certifies over the country's full span (the headline claim)
  n_spans, n_cert : how many admissible sub-spans certify
  loo_first       : certifies with the first round dropped
  loo_last        : certifies with the last round dropped
  robust          : net_full AND loo_first AND loo_last
  frac_cert       : n_cert / n_spans -- how special the headline endpoints are

A country that certifies only at its full span, and not when either endpoint is
dropped, is an endpoint-fragile certification: real, but a statement about the
two waves that bracket the record rather than about the two decades between.

Output: results/ess_endpoint_sensitivity.csv
Run:    python -m pcb.experiments.e43_endpoint_sensitivity   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)
from pcb.inference.decline_certify import certify_decline_differences

OUTCOMES = ("trstprl", "stfdem")
MIN_N = 100
MIN_STEPS = 2          # a sub-span must cover at least two adjacent-round steps


def _cells(csub, rounds, klass, c, outcome, rng):
    out = {}
    for r in rounds:
        sub = csub[csub.essround == r]
        y, w, s, p = _round_stats(sub, outcome)
        if len(y) < MIN_N:
            continue
        F = _wcdf(y, w)
        B = (_design_boot(y, w, s, p, rng) if klass.get((c, r)) == "core"
             else _naive_boot(y, w, rng))
        out[r] = (F, B)
    return out


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
            if len(usable) < 2:
                continue
            rng = np.random.default_rng(det_seed("e43", outcome, c))
            cells = _cells(csub, usable, kl, c, outcome, rng)
            rounds = sorted(cells)
            # adjacency structure: steps are consecutive ESS rounds present
            if len(rounds) < 2:
                continue

            def net_cert(a, b):
                Fa, Ba = cells[a]; Fb, Bb = cells[b]
                return certify_decline_differences((Fb - Fa)[None],
                                                   (Bb - Ba)[:, None],
                                                   ALPHA, CORE_T)["design_aware"]

            spans = [(a, b) for i, a in enumerate(rounds)
                     for b in rounds[i + 1:]
                     if rounds.index(b) - rounds.index(a) >= MIN_STEPS]
            n_cert = sum(net_cert(a, b) for a, b in spans)
            full = net_cert(rounds[0], rounds[-1])
            loo_first = net_cert(rounds[1], rounds[-1]) if len(rounds) >= 3 else None
            loo_last = net_cert(rounds[0], rounds[-2]) if len(rounds) >= 3 else None
            robust = bool(full and loo_first and loo_last) if len(rounds) >= 3 else None
            rows.append(dict(outcome=outcome, cntry=c, n_rounds=len(rounds),
                             r_first=rounds[0], r_last=rounds[-1],
                             net_full=bool(full),
                             loo_first=loo_first, loo_last=loo_last,
                             robust=robust, n_spans=len(spans), n_cert=n_cert,
                             frac_cert=round(n_cert / len(spans), 3) if spans else np.nan))
            print(f"{outcome:8s} {c}: full={bool(full)} loo_first={loo_first} "
                  f"loo_last={loo_last} spans {n_cert}/{len(spans)}")
    res = pd.DataFrame(rows)
    res.to_csv("results/ess_endpoint_sensitivity.csv", index=False)

    print("\n=== endpoint robustness of the net rung ===")
    for outcome in OUTCOMES:
        p = res[res.outcome == outcome]
        cert = p[p.net_full]
        rob = cert[cert.robust.fillna(False)]
        frag = cert[~cert.robust.fillna(False)]
        print(f"{outcome}: net certified in {len(cert)} countries; "
              f"endpoint-robust in {len(rob)} -> {sorted(rob.cntry)}")
        if len(frag):
            print(f"  endpoint-fragile (drops when an endpoint is removed, or "
                  f"only 2 rounds): {sorted(frag.cntry)}")


if __name__ == "__main__":
    main()
