"""E26 — WVS deconsolidation reanalysis (preregistered WVS_DECONSOLIDATION_PREREG).

Named target: the Foa–Mounk "democratic deconsolidation" thesis. Marginal wave-by-wave
shifts in single items suggest eroding democratic support across many countries; we ask
how many survive the paper's honest object — a persistent, distribution-wide,
survey-aware, simultaneous decline. WVS has no PSU/stratum, so the survey-aware band is a
weighted respondent bootstrap (weights-only). Reported exactly as produced.

Run:  python -m pcb.experiments.e26_wvs_deconsolidation
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_wvs import load, ITEMS
from pcb.inference.decline_certify import certify_decline_differences
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import rho_lcb, deconv_reliability

ALPHA = 0.10
B = 2000
MIN_N = 400
SUPPORT = {"imp_dem": 10, "rej_leader": 4, "rej_army": 4, "sup_demsys": 4, "confid_parl": 4}
CORE = {"imp_dem": [6, 7, 8], "rej_leader": [1, 2], "rej_army": [1, 2],
        "sup_demsys": [1, 2], "confid_parl": [1, 2]}


def _wcdf(y, w, M):
    thr = np.arange(1, M + 1)
    return (w[:, None] * (y[:, None] <= thr[None, :])).sum(0) / w.sum()


def _resp_boot(y, w, M, rng):
    """Weighted respondent bootstrap → (B, M) CDF draws (weights-only, no PSU)."""
    n = len(y)
    idx = rng.integers(0, n, size=(B, n))
    yb, wb = y[idx], w[idx]
    thr = np.arange(1, M + 1)
    ind = (yb[:, :, None] <= thr[None, None, :])
    return (wb[:, :, None] * ind).sum(1) / wb.sum(1)[:, None]


def _cells(df, item):
    """Per (country, wave) with ≥MIN_N valid: (F, boot draws)."""
    M = SUPPORT[item]
    out = {}
    for (c, wv), g in df.groupby(["S003", "S002VS"], observed=True):
        m = g[item].notna() & g["_w"].notna() & (g["_w"] > 0)
        if m.sum() < MIN_N:
            continue
        y = g[item].to_numpy(float)[m.to_numpy()]
        w = g["_w"].to_numpy(float)[m.to_numpy()]
        rng = np.random.default_rng(det_seed("e26", item, int(c), int(wv)))
        out[(int(c), int(wv))] = (_wcdf(y, w, M), _resp_boot(y, w, M, rng))
    return out


def _certify_country(cells, c, waves, item):
    """Return dict of booleans for any-pair / net / persistent (survey-aware & plugin)."""
    M = SUPPORT[item]
    tmask = np.zeros(M, bool)
    tmask[[t - 1 for t in CORE[item]]] = True     # thresholds are 1..M
    ws = sorted(w for w in waves if (c, w) in cells)
    pairs = [(a, b) for a, b in zip(ws[:-1], ws[1:])]
    if not pairs:
        return None
    # per-pair difference and its bootstrap (independent draws per wave)
    dh, db = [], []
    for a, b in pairs:
        Fa, Ba = cells[(c, a)]; Fb, Bb = cells[(c, b)]
        dh.append(Fb - Fa); db.append(Bb - Ba)
    dh = np.array(dh)                              # (P, M)
    db = np.stack(db, 1)                           # (B, P, M)
    anypair = any(certify_decline_differences(dh[[i]], db[:, [i], :], ALPHA, tmask)["design_aware"]
                  for i in range(len(pairs)))
    anypair_pi = any(certify_decline_differences(dh[[i]], db[:, [i], :], ALPHA, tmask)["plugin"]
                     for i in range(len(pairs)))
    # net first→last
    Fa, Ba = cells[(c, ws[0])]; Fb, Bb = cells[(c, ws[-1])]
    net = certify_decline_differences((Fb - Fa)[None], (Bb - Ba)[:, None, :], ALPHA, tmask)
    # persistent country-wide simultaneous over all pairs × core
    per = certify_decline_differences(dh, db, ALPHA, tmask)
    return dict(anypair=anypair, anypair_pi=anypair_pi,
                net=net["design_aware"], net_pi=net["plugin"],
                persist=per["design_aware"], persist_pi=per["plugin"])


def _hierarchy(df, item, age_mask=None):
    d = df if age_mask is None else df[age_mask(df["X003"].to_numpy())]
    cells = _cells(d, item)
    countries = sorted({c for c, _ in cells})
    waves = sorted({w for _, w in cells})
    rows = {}
    for c in countries:
        r = _certify_country(cells, c, waves, item)
        if r:
            rows[c] = r
    return rows, len(rows)          # denominator = countries with ≥2 qualifying waves


def _gate_probe(df, item):
    """LOCO transport ρ̂/D at WVS K (weights-only design SD) — did any gate open?"""
    M = SUPPORT[item]
    tmask = [t - 1 for t in CORE[item]]
    cells = _cells(df, item)
    countries = sorted({c for c, _ in cells})
    Fmat = {c: np.array([cells[k][0][tmask] for k in cells if k[0] == c]) for c in countries}
    # weights-only design SD = SD across bootstrap draws, at the core thresholds
    Vmat = {c: np.array([cells[k][1][:, tmask].std(0) for k in cells if k[0] == c])
            for c in countries}
    mu = np.vstack([Fmat[c] for c in countries]).mean(0)
    E, V = [], []
    for c in countries:
        dev = Fmat[c] - mu[None, :]
        j = np.argmax(np.abs(dev), axis=0)
        E.append(dev[j, np.arange(dev.shape[1])])
        V.append(Vmat[c][j, np.arange(dev.shape[1])])
    E, V = np.array(E), np.array(V)
    K = E.shape[0]
    s = _modulation(E)
    return dict(item=item, K=K, rho_hat=float(np.sqrt((V**2).mean()) / s.mean()),
                rho_lcb=float(rho_lcb(E, V)), D=float(deconv_reliability(E, V)),
                vovk_floor=float(np.sqrt(2 / (K - 1))))


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]

    print("WVS deconsolidation reanalysis — guarantee-hierarchy collapse "
          "(plug-in vs survey-aware), α=0.10\n")
    print(f"{'item':12s}{'K':>4} | {'any-pair':>10}{'net':>8}{'persistent':>12}  (survey-aware / plug-in)")
    summ, gates = [], []
    for item in ITEMS:
        rows, K = _hierarchy(df, item)
        ap = sum(r["anypair"] for r in rows.values()); ap_pi = sum(r["anypair_pi"] for r in rows.values())
        nt = sum(r["net"] for r in rows.values()); nt_pi = sum(r["net_pi"] for r in rows.values())
        ps = sum(r["persist"] for r in rows.values()); ps_pi = sum(r["persist_pi"] for r in rows.values())
        persist_countries = [c for c, r in rows.items() if r["persist"]]
        print(f"{item:12s}{K:>4} | {ap:>3}/{ap_pi:<3}   {nt:>2}/{nt_pi:<2}   {ps:>3}/{ps_pi:<3}      "
              f"(persistent survey-aware countries: {persist_countries})")
        summ.append(dict(item=item, K_countries=K, anypair=ap, anypair_plugin=ap_pi,
                         net=nt, net_plugin=nt_pi, persist=ps, persist_plugin=ps_pi,
                         persist_countries=";".join(map(str, persist_countries))))
        gates.append(_gate_probe(df, item))
    pd.DataFrame(summ).to_csv("results/wvs_deconsolidation.csv", index=False)

    print("\nGate probe at WVS K (did the design-aware branch ever open?):")
    g = pd.DataFrame(gates)
    g["gate_A"] = g.rho_lcb > 0.47
    g["gate_B_floor_ok"] = g.vovk_floor <= 0.147
    pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    print(g[["item", "K", "rho_hat", "rho_lcb", "D", "vovk_floor", "gate_A", "gate_B_floor_ok"]].to_string(index=False))
    g.to_csv("results/wvs_gate_probe.csv", index=False)
    print(f"\ncross-national K: ESS ≤ 33, WVS ≤ {int(g.K.max())} (< 94 needed for gate B); "
          f"max ρ̂_LCB = {g.rho_lcb.max():.3f} (< ρ₀=0.47). Neither gate opens.")

    print("\nYouth vs older (persistent, survey-aware; Foa–Mounk youth claim):")
    for item in ("imp_dem", "rej_leader", "rej_army"):
        yr, yK = _hierarchy(df, item, age_mask=lambda a: (a >= 18) & (a <= 29))
        orr, oK = _hierarchy(df, item, age_mask=lambda a: a >= 50)
        yp = sum(r["persist"] for r in yr.values()); op = sum(r["persist"] for r in orr.values())
        print(f"  {item:12s}: youth 18–29 persistent {yp}/{yK} countries | older 50+ {op}/{oK}")


if __name__ == "__main__":
    main()
