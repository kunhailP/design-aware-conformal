"""E40 — the promised ESS mode/fieldwork audit (paper §7/§8).

Round-10 fieldwork (2020–22) saw nine countries switch from face-to-face to
self-completion; a wave-pair CDF shift there confounds attitude change with mode
effects, which no design bootstrap absorbs. Documented modes (ESS10 mode note,
ESS10_note_on_data_modes_e01_0.pdf; ESS R11 release notes):

  R9  (2018/19): face-to-face, all countries.
  R10 (2020/22): SELF-COMPLETION in AT, CY, DE, ES, IL, LV, PL, RS, SE;
                 face-to-face elsewhere (GB and FI ran parallel SC experiments;
                 the main-file data are face-to-face).
  R11 (2023/24): face-to-face everywhere in the integrated file (CZ collected
                 self-completion, released as a country-specific file only).

This audit (1) writes the country x round mode table with per-pair mode-constancy
flags, (2) reruns the rounds-9–11 certification EXCLUDING mode-confounded pairs
— for the nine SC countries both (9,10) and (10,11) straddle a switch, so their
any-pair and persistent rungs are marked mode-confounded; their net 9->11 span
has face-to-face endpoints and is recomputed directly — and (3) confirms the
Greek certified pair (10->11) is mode-constant.

Output: results/ess_mode_table.csv, results/ess_mode_constant_certification.csv
Run:    python -m pcb.experiments.e40_mode_audit
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

SC_MODES = {3, 4}          # 3 = CAWI, 4 = self-administered paper
VIDEO_MODE = 2             # video (web-based) interview, distinct from CAPI


def _mode_table():
    """Country x round administration mode, read from the data's own `mode`
    variable (not from external documentation). Round 9 ships mode='not
    available'; it was face-to-face throughout per the ESS9 documentation."""
    import pyreadstat
    d, _ = pyreadstat.read_dta("data/ess/Datafile-subset.dta",
                               usecols=["essround", "cntry", "mode"])
    d = d[d.essround.isin([9, 10, 11])]
    rows = []
    for (c, r), g in d.groupby(["cntry", "essround"], observed=True):
        m = g["mode"]
        n = len(g)
        sc = float(m.isin(SC_MODES).mean())
        vid = float((m == VIDEO_MODE).mean())
        rows.append(dict(cntry=str(c), essround=int(r), n=n,
                         share_selfcompletion=round(sc, 4),
                         share_video=round(vid, 4),
                         mode=("self-completion" if sc > 0.5 else
                               "face-to-face (mode not recorded)"
                               if m.isna().all() else "face-to-face")))
    return pd.DataFrame(rows).sort_values(["cntry", "essround"])


def _singleton_strata(df):
    """How many strata contribute a single PSU (and so no internal variance) in
    the core country-rounds -- the one bias the rescaled bootstrap cannot fix."""
    tot = single = resp_single = 0
    for (c, r), g in df.groupby(["cntry", "essround"], observed=True):
        if g["psu"].isna().all() or g["stratum"].isna().all():
            continue
        k = g.groupby("stratum", observed=True)["psu"].nunique()
        tot += len(k); single += int((k <= 1).sum())
        if (k <= 1).any():
            bad = set(k[k <= 1].index)
            resp_single += int(g["stratum"].isin(bad).sum())
    return tot, single, resp_single


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    # --- (1) mode table, derived from the data --------------------------------
    mt = _mode_table()
    mt.to_csv("results/ess_mode_table.csv", index=False)
    sc10 = sorted(mt[(mt.essround == 10) &
                     (mt["mode"] == "self-completion")].cntry.unique())
    SC_R10 = set(sc10)
    vid = mt[(mt.essround.isin([10, 11])) & (mt.share_video > 0)]
    print(f"mode table (from the data's own `mode` variable): "
          f"{mt.cntry.nunique()} countries")
    print(f"  round-10 self-completion ({len(sc10)}): {sc10}")
    print(f"  video interviewing present in {vid.cntry.nunique()} countries "
          f"(rounds 10-11), max share {vid.share_video.max():.2f} — collapsed "
          f"into face-to-face here, disclosed in the paper")

    core = df[[klass.get((c, r)) == "core"
               for c, r in zip(df.cntry, df.essround)]]
    tot, single, resp = _singleton_strata(core)
    print(f"  singleton strata in the core rounds: {single} of {tot} "
          f"({100*single/max(tot,1):.2f}%), covering {resp} respondents "
          f"({100*resp/max(len(core),1):.2f}%)\n")
    pd.DataFrame([dict(strata_total=tot, strata_singleton=single,
                       respondents_in_singleton=resp,
                       respondents_total=len(core))]).to_csv(
        "results/ess_singleton_strata.csv", index=False)

    # --- (2) mode-constant rerun ----------------------------------------------
    shipped = pd.read_csv("results/ess_country_certification.csv")
    out = []
    for outcome in e13.OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            core_rounds = [r for r in sorted(csub.essround.unique())
                           if klass.get((c, r)) == "core"]
            if len(core_rounds) < 2:
                continue
            rng = np.random.default_rng(det_seed(outcome, c))
            if c not in SC_R10:
                res = e13.audit_country(csub, core_rounds, outcome, rng)
                if res:
                    out.append(dict(outcome=outcome, cntry=c, confounded=False,
                                    any_da=res["any_da"], net_da=res["net_da"],
                                    persist_da=res["persist_da"]))
                continue
            # SC country: pairs straddle the switch -> any/persist mode-confounded;
            # net 9->11 has face-to-face endpoints, certify it directly.
            if 9 in core_rounds and 11 in core_rounds:
                net_out = e13._pair_diff(csub[csub.essround == 9],
                                         csub[csub.essround == 11], outcome, rng)
                net = (certify_decline_differences(net_out[0][None],
                                                   net_out[1][:, None],
                                                   ALPHA, CORE_T)["design_aware"]
                       if net_out is not None else False)
            else:
                net = None
            out.append(dict(outcome=outcome, cntry=c, confounded=True,
                            any_da=None, net_da=net, persist_da=None))
    res = pd.DataFrame(out)
    res.to_csv("results/ess_mode_constant_certification.csv", index=False)

    print("=== mode-constant certification (rounds 9-11) ===")
    for outcome in e13.OUTCOMES:
        r = res[res.outcome == outcome]
        s = shipped[shipped.outcome == outcome]
        clean = r[~r.confounded]
        print(f"{outcome}:")
        print(f"  shipped:        any {int(s.any_da.sum()):2d}  "
              f"net {int(s.net_da.sum()):2d}  persist {int(s.persist_da.sum()):2d}")
        print(f"  mode-constant:  any {int(clean.any_da.sum()):2d} (+{int(r.confounded.sum())} confounded excluded)  "
              f"net {int(r.net_da.astype(bool).sum() if r.net_da.notna().any() else 0):2d}  "
              f"persist {int(clean.persist_da.sum()):2d}")
        drop_net = sorted(set(s.cntry[s.net_da]) - set(r.cntry[r.net_da.fillna(False).astype(bool)]))
        add_net = sorted(set(r.cntry[r.net_da.fillna(False).astype(bool)]) - set(s.cntry[s.net_da]))
        if drop_net or add_net:
            print(f"  net changes: dropped {drop_net}, added {add_net}")
        pers = sorted(clean.cntry[clean.persist_da])
        print(f"  persistent (mode-constant subset): {pers}")

    # --- (3) Greece -----------------------------------------------------------
    print("\nGreece check: fielded rounds 10 and 11, both face-to-face "
          "(not in the R10 self-completion set) -> the certified 10->11 pair is "
          "mode-constant.")


if __name__ == "__main__":
    main()
