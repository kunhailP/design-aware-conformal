"""E45 — certified magnitudes, and certified RISES (paper §7).

Two gaps the counts leave open.

(1) MAGNITUDES. A certification count is not a quantity anyone can cite. The
    same one-sided simultaneous band that certifies a decline also delivers its
    size: the largest d such that D_hat(t) - c*sd(t) >= d holds at every core
    threshold is a 1-alpha simultaneous lower bound on the decline in CDF
    points. We report it per country, for the rounds-9-11 window and for the
    full 2002-2024 record, so the paper can say "trust in parliament fell by at
    least d points over the low-trust core, with 90% simultaneous confidence."

(2) RISES. The hierarchy as deployed is decline-only, so a null at the
    persistent rung is consistent both with "episodes with recoveries" and with
    "slow monotone drift below the detection threshold". Running the same
    machinery with the inequality reversed certifies RECOVERIES, which
    discriminates the two readings: a country with certified declines AND
    certified rises across its record is episodic; one with neither is quiet or
    underpowered. This is the evidence the episodic reading needs.

Output: results/ess_magnitudes.csv, results/ess_rises.csv
Run:    python -m pcb.experiments.e45_magnitudes_and_rises   (~40 min)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)

OUTCOMES = ("trstprl", "stfdem")
MIN_N = 100


def _band_lower(diff_hat, diff_boot, alpha=ALPHA, t_mask=CORE_T):
    """One-sided simultaneous lower bound on the decline, in CDF points.

    Mirrors `certify_decline_differences`: c is the (1-alpha) quantile of the
    studentized sup deviation; the certified magnitude is
    min over (pair, threshold) of (D_hat - c*sd). Positive <=> certified.
    """
    dh = diff_hat[:, t_mask]
    db = diff_boot[:, :, t_mask]
    sd = np.maximum(db.std(0), 1e-6)
    dev = np.max((db - dh[None]) / sd[None], axis=(1, 2))
    c = np.quantile(dev, 1 - alpha)
    return float(np.min(dh - c * sd))


def _rise_lower(diff_hat, diff_boot, alpha=ALPHA, t_mask=CORE_T):
    """Same object with the inequality reversed: a certified RISE (recovery)."""
    return _band_lower(-diff_hat, -diff_boot, alpha, t_mask)


def _cells(csub, rounds, klass, c, outcome, rng):
    out = {}
    for r in rounds:
        y, w, s, p = _round_stats(csub[csub.essround == r], outcome)
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

    mag_rows, rise_rows = [], []
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            all_rounds = [r for r in sorted(csub.essround.unique())
                          if kl.get((c, r)) in ("core", "extended")]
            core_rounds = [r for r in sorted(csub.essround.unique())
                           if kl.get((c, r)) == "core"]
            rng = np.random.default_rng(det_seed("e45", outcome, c))
            cells = _cells(csub, all_rounds, kl, c, outcome, rng)
            row = dict(outcome=outcome, cntry=c)
            for label, rounds in (("short", [r for r in core_rounds if r in cells]),
                                  ("long", sorted(cells))):
                if len(rounds) < 2:
                    row[f"net_lb_{label}"] = np.nan
                    row[f"span_{label}"] = ""
                    continue
                F0, B0 = cells[rounds[0]]; F1, B1 = cells[rounds[-1]]
                lb = _band_lower((F1 - F0)[None], (B1 - B0)[:, None])
                row[f"net_lb_{label}"] = round(lb, 4)
                row[f"span_{label}"] = f"{rounds[0]}-{rounds[-1]}"
            mag_rows.append(row)

            # rises: any adjacent pair over the full record
            rr = sorted(cells)
            pairs = [(a, b) for a, b in zip(rr[:-1], rr[1:]) if b == a + 1]
            n_rise = n_fall = 0
            for a, b in pairs:
                Fa, Ba = cells[a]; Fb, Bb = cells[b]
                d, db = (Fb - Fa)[None], (Bb - Ba)[:, None]
                n_fall += int(_band_lower(d, db) > 0)
                n_rise += int(_rise_lower(d, db) > 0)
            if pairs:
                rise_rows.append(dict(outcome=outcome, cntry=c, n_pairs=len(pairs),
                                      n_certified_declines=n_fall,
                                      n_certified_rises=n_rise,
                                      episodic=bool(n_fall and n_rise)))
    mag = pd.DataFrame(mag_rows); mag.to_csv("results/ess_magnitudes.csv", index=False)
    ris = pd.DataFrame(rise_rows); ris.to_csv("results/ess_rises.csv", index=False)

    print("=== certified net decline, lower bound in CDF points (90% simultaneous) ===")
    for outcome in OUTCOMES:
        m = mag[(mag.outcome == outcome)]
        cert = m[m.net_lb_long > 0].sort_values("net_lb_long", ascending=False)
        print(f"\n{outcome} — full record:")
        print(cert[["cntry", "span_long", "net_lb_long", "net_lb_short"]]
              .to_string(index=False))
        cs = m[m.net_lb_short > 0].sort_values("net_lb_short", ascending=False)
        print(f"{outcome} — rounds 9-11: " +
              ", ".join(f"{r.cntry} {r.net_lb_short:+.3f}" for r in cs.itertuples()))

    print("\n=== certified rises (recoveries) over the full record ===")
    for outcome in OUTCOMES:
        r = ris[ris.outcome == outcome]
        print(f"{outcome}: {int(r.n_certified_rises.sum())} certified rising pairs "
              f"in {int((r.n_certified_rises > 0).sum())} countries; "
              f"{int(r.n_certified_declines.sum())} declining pairs in "
              f"{int((r.n_certified_declines > 0).sum())}; "
              f"both in {int(r.episodic.sum())} countries (episodic)")
        ep = sorted(r.cntry[r.episodic])
        print(f"  episodic: {ep}")


if __name__ == "__main__":
    main()
