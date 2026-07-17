"""E32 — severity: what magnitude of decline would each rung detect?

Referee-facing power analysis for the claim hierarchy. Both referees' question
is the same: is "only one persistent certification" informative, or a statement
about test severity? This experiment answers it in simulation calibrated to
ESS-like scales (real-data injection requires the licensed microdata and is
flagged for the archived replication).

Design. A country's low-trust-core CDF declines by a known Delta (CDF points)
at every adjacent wave pair, for P pairs, at T_core thresholds. Wave estimates
carry design noise with SD v per threshold (ESS-like: n ~ 2000, deff ~ 1.2
gives v ~ 0.012; we sweep v). The certification instrument mirrors the deployed
one (design sup-t on pair differences, one-sided, alpha = 0.10): a pair
certifies if the difference band max_t (D_hat(t) + c_sup * se) < 0; the rungs
are any-pair (some pair certifies), net (first-to-last contrast certifies), and
persistent (ALL pairs certify).

Outputs per (Delta, v, P): detection rates per rung, and the implied minimum
Delta for 80% power. Deterministic. Writes results/severity.csv.

Run:  python -m pcb.experiments.e32_severity
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed

ALPHA = 0.10
T_CORE = 4
REPS = 4000
DELTAS = [0.00, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08]
VS = [0.008, 0.012, 0.020]
PS = [1, 2, 4]
MASTER = 20260719


def _sup_crit(v_diff, rng, n=4000):
    """One-sided sup-t critical value over T_CORE thresholds (correlation ~
    exchangeable 0.5 across thresholds of a CDF difference; simulated)."""
    z = rng.standard_normal((n, T_CORE))
    shared = rng.standard_normal((n, 1))
    corr = np.sqrt(0.5) * shared + np.sqrt(0.5) * z          # threshold corr 0.5
    return float(np.quantile(corr.max(axis=1), 1 - ALPHA))


def main(out="results/severity.csv"):
    rng0 = np.random.default_rng(det_seed(MASTER, "crit", 0, 0, 0))
    c_sup = _sup_crit(1.0, rng0)
    rows = []
    for v in VS:
        se = np.sqrt(2.0) * v                                 # pair difference SE
        for P in PS:
            for d in DELTAS:
                rng = np.random.default_rng(det_seed(MASTER, "sev", int(v * 1e4),
                                                     P, int(d * 1e3)))
                shared = rng.standard_normal((REPS, P, 1))
                idio = rng.standard_normal((REPS, P, T_CORE))
                noise = se * (np.sqrt(0.5) * shared + np.sqrt(0.5) * idio)
                Dhat = -d + noise                              # per-pair differences
                pair_cert = (Dhat + c_sup * se < 0).all(axis=2)   # (REPS, P)
                any_p = pair_cert.any(axis=1).mean()
                persist = pair_cert.all(axis=1).mean()
                # net: first-to-last contrast, magnitude P*d, SE sqrt(2)v (two waves)
                nshared = rng.standard_normal((REPS, 1))
                nidio = rng.standard_normal((REPS, T_CORE))
                Nhat = -P * d + se * (np.sqrt(0.5) * nshared + np.sqrt(0.5) * nidio)
                net = (Nhat + c_sup * se < 0).all(axis=1).mean()
                rows.append(dict(v=v, P=P, delta=d, any_pair=round(any_p, 4),
                                 net=round(net, 4), persistent=round(persist, 4)))
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv(out, index=False)
    print(f"E32 severity (alpha={ALPHA} one-sided sup-t over {T_CORE} thresholds, "
          f"{REPS} reps)\n")
    print(df.to_string(index=False))
    print("\nminimum Delta (CDF pts/pair) for 80% power:")
    for v in VS:
        for P in PS:
            s = df[(df.v == v) & (df.P == P)]
            for rung in ["any_pair", "net", "persistent"]:
                ok = s[s[rung] >= 0.80]
                need = ok.delta.min() if len(ok) else float("nan")
                print(f"  v={v:.3f} P={P} {rung:10s}: Δ ≥ {need}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
