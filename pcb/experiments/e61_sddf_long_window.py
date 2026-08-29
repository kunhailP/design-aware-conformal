"""E61 — the long window rerun with the rounds 1-8 SDDF design upgrade.

E36/E50 classify rounds 1-8 "extended" (weights-only respondent bootstrap)
because the integrated files carry no psu/stratum there; the paper disclosed
the separate Sample Design Data Files as the revision item that would settle
the weights-only understatement directly. This experiment is that item: it
merges whatever SDDF files sit under data/ess/sddf/ (pcb.data.ess_sddf),
lets the unchanged audit rule reclassify the covered country-rounds as core,
and reruns

  (a) the per-family long window of E36  -> results/ess_long_window_sddf.csv
  (b) the joint claim family of E50      -> results/ess_joint_claims_sddf.csv

with the SAME per-country seeds as the shipped runs, so core-round draws are
identical and every delta is attributable to the SDDF upgrade alone. Shipped
CSVs are not touched; the deltas against them are printed at the end.

Run:  python -m pcb.experiments.e61_sddf_long_window     (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import COLS, audit, load
from pcb.data.ess_sddf import load_sddf, merge_design
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)
from pcb.experiments.e36_ess_long_window import (MIN_N, OUTCOMES,
                                                 audit_country_long)
from pcb.inference.claim_family import certify_claim_family


def _prepare():
    df = load(columns=COLS + ["idno"])
    merged = merge_design(df, load_sddf())
    a_before, a_after = audit(df), audit(merged)
    up = (a_after["sample"] == "core") & (a_before["sample"] != "core")
    print(f"country-rounds upgraded to core: {int(up.sum())} "
          f"(core {int((a_before['sample'] == 'core').sum())} -> "
          f"{int((a_after['sample'] == 'core').sum())}); "
          f"still extended: {int((a_after['sample'] == 'extended').sum())}")
    kl = a_after.set_index(["cntry", "essround"])["sample"]
    merged = merged.assign(_w=merged["anweight"].fillna(merged["pspwght"]))
    merged = merged[merged._w.notna() & (merged._w > 0)]
    return merged, kl


def _run_e36_style(df, kl):
    from pcb.inference.decline_certify import certify_decline_differences
    rows, stash = [], {}
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            usable = [r for r in sorted(csub.essround.unique())
                      if kl.get((c, r)) in ("core", "extended")]
            if len(usable) < 2:
                continue
            rng = np.random.default_rng(det_seed("e36", outcome, c))
            res = audit_country_long(csub, usable, kl, c, outcome, rng)
            if res:
                stash[(outcome, c)] = (res.pop("_H"), res.pop("_Bd"),
                                       res.pop("_Hn"), res.pop("_Bn"))
                rows.append(dict(outcome=outcome, cntry=c, **res))
    cty = pd.DataFrame(rows)
    bonf, bonf_net = [], []
    for outcome in OUTCOMES:
        Kc = (cty.outcome == outcome).sum()
        for _, r in cty[cty.outcome == outcome].iterrows():
            H, Bd, Hn, Bn = stash[(outcome, r.cntry)]
            a = ALPHA / max(Kc, 1)
            bonf.append(certify_decline_differences(H, Bd, a, CORE_T)["design_aware"])
            bonf_net.append(
                certify_decline_differences(Hn, Bn, a, CORE_T)["design_aware"]
                if Hn is not None else False)
    cty["persist_da_bonf"] = bonf
    cty["net_da_bonf"] = bonf_net
    return cty


def _run_e50_style(df, kl):
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
                Fc = _wcdf(y, w)
                if kl.get((c, r)) == "core":
                    Bc = _design_boot(y, w, s, p, rng)
                else:
                    Bc = _naive_boot(y, w, rng)
                F.append(Fc); B.append(Bc); rr.append(int(r))
            if len(rr) < 3:
                continue
            res = certify_claim_family(np.array(F), np.stack(B, 1), ALPHA, CORE_T)
            rows.append(dict(outcome=outcome, cntry=c, n_rounds=len(rr),
                             r_first=rr[0], r_last=rr[-1], c=round(res["c"], 3),
                             net=res["net"], persistent=res["persistent"],
                             any_pair=res["any_pair"], episodic=res["episodic"],
                             n_spans=res["n_spans"],
                             n_declining=res["n_declining"],
                             n_rising=res["n_rising"],
                             frac_declining=round(res["frac_spans_declining"], 3),
                             net_lower=round(res["net_lower"], 4)))
    return pd.DataFrame(rows)


def _delta(tag, new, shipped_path, cols):
    if not os.path.exists(shipped_path):
        print(f"[{tag}] shipped file {shipped_path} missing; no delta")
        return
    old = pd.read_csv(shipped_path)
    print(f"\n=== {tag}: SDDF vs shipped ===")
    for outcome in OUTCOMES:
        n, o = new[new.outcome == outcome], old[old.outcome == outcome]
        for col in cols:
            cn = sorted(n.cntry[n[col].astype(bool)])
            co = sorted(o.cntry[o[col].astype(bool)])
            mark = "" if cn == co else "   <-- CHANGED"
            print(f"  {outcome:8s} {col:15s} {len(co):2d} -> {len(cn):2d}{mark}")
            if cn != co:
                gained, lost = set(cn) - set(co), set(co) - set(cn)
                if gained:
                    print(f"{'':28s}gained: {sorted(gained)}")
                if lost:
                    print(f"{'':28s}lost:   {sorted(lost)}")


def main():
    os.makedirs("results", exist_ok=True)
    df, kl = _prepare()

    e36 = _run_e36_style(df, kl)
    e36.to_csv("results/ess_long_window_sddf.csv", index=False)
    wo = int(e36.n_pairs_weightsonly.sum())
    print(f"\nE36-style rerun: {int(e36.n_pairs.sum())} pairs, "
          f"{wo} still with a weights-only side "
          f"(shipped: 174 of 231 per outcome pair-set)")
    _delta("per-family (e36)", e36, "results/ess_long_window.csv",
           ["any_da", "net_da", "persist_da", "net_da_bonf"])

    e50 = _run_e50_style(df, kl)
    e50.to_csv("results/ess_joint_claims_sddf.csv", index=False)
    _delta("joint band (e50)", e50, "results/ess_joint_claims.csv",
           ["net", "persistent", "any_pair", "episodic"])


if __name__ == "__main__":
    main()
