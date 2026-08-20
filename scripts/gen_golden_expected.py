"""Regenerate the R-package golden expectations from the Python reference.

Each case directory under rpkg/dapcb/inst/golden/ holds fixed inputs
(E.csv, V.csv, center.csv); this script runs `pcb.dapcb.dapcb` on them and
rewrites expected_lo.csv / expected_hi.csv / expected_meta.json, preserving
the `alpha` recorded in the existing meta. Run whenever the reference
implementation changes deliberately (e.g. the K/(K-1) LOO anchor inflation),
then re-run rpkg/dapcb/tests/golden.R to confirm the R port matches to 1e-10.

Usage: python scripts/gen_golden_expected.py
"""
import json
import os

import numpy as np

from pcb import dapcb

GOLDEN = os.path.join("rpkg", "dapcb", "inst", "golden")


def main():
    for name in sorted(os.listdir(GOLDEN)):
        d = os.path.join(GOLDEN, name)
        if not os.path.isdir(d):
            continue
        E = np.loadtxt(os.path.join(d, "E.csv"), delimiter=",", ndmin=2)
        V = np.loadtxt(os.path.join(d, "V.csv"), delimiter=",", ndmin=2)
        center = np.loadtxt(os.path.join(d, "center.csv"), delimiter=",")
        with open(os.path.join(d, "expected_meta.json")) as f:
            alpha = json.load(f)["alpha"]
        fit = dapcb(E, V, center, alpha=alpha)
        lo, hi = fit.band
        np.savetxt(os.path.join(d, "expected_lo.csv"), lo, fmt="%.18e")
        np.savetxt(os.path.join(d, "expected_hi.csv"), hi, fmt="%.18e")
        meta = {
            "alpha": alpha,
            "branch": fit.selected_branch,
            "rho_hat": fit.rho_hat,
            "rho_lcb": fit.rho_lcb,
            "reliability": fit.reliability,
            "delta_ucb": fit.delta_ucb,
            "coverage_level": fit.coverage_level,
            "gain_lcb": None if np.isnan(fit.gain_lcb) else fit.gain_lcb,
            "overlap_warning": bool(fit.overlap_warning),
        }
        with open(os.path.join(d, "expected_meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
            f.write("\n")
        print(f"{name:18s} branch={fit.selected_branch:13s} "
              f"cov={fit.coverage_level:.3f}")


if __name__ == "__main__":
    main()
