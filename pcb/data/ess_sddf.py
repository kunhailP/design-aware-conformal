"""ESS Sample Design Data Files (SDDF) — the rounds 1-8 design upgrade.

The integrated ESS files carry psu/stratum only from round 9; rounds 1-8 are
classified "extended" (weights-only) by the audit, which is what makes 174 of
the long window's 231 pairs weights-only. ESS distributes the missing design
variables separately as Sample Design Data Files: one integrated file per
round for rounds 7-8, one file per country for rounds 1-6 (variables idno,
cntry, psu, stratify, prob; format varies by vintage).

This module ingests whatever SDDF files are placed under data/ess/sddf/
(any nesting; .dta/.sav/.por/.csv/.zip), harmonizes them to
(cntry, essround, idno, psu, stratum, prob), and merges them into the
integrated subset so that pcb.data.audit_ess.audit() reclassifies the covered
country-rounds as "core" under its own unchanged rule (psu/stratum coverage
> 0.95, >= 20 PSUs). Country-rounds without a usable SDDF stay "extended":
the upgrade is partial by construction and e61 reports exactly how partial.

Where a file carries psu but no stratify variable, stratum is filled with a
single constant stratum (unstratified PSU bootstrap) and the fill is counted
in the ingest report; ESS documents stratify as unavailable for some early
country-rounds.

Run:  python -m pcb.data.ess_sddf        -> data/ess/sddf_merged.parquet
"""
from __future__ import annotations
import os
import re
import zipfile

import numpy as np
import pandas as pd

SDDF_DIR = "data/ess/sddf"
CACHE = "data/ess/sddf_merged.parquet"

# harmonized names <- variants seen across SDDF vintages
COLMAP = {"stratify": "stratum", "stratval": "stratum", "stratum": "stratum",
          "psu": "psu", "idno": "idno", "cntry": "cntry", "prob": "prob",
          "essround": "essround"}
READABLE = (".dta", ".sav", ".por", ".csv")


def _read_any(path: str) -> pd.DataFrame | None:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    import pyreadstat
    reader = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav,
              ".por": pyreadstat.read_por}[ext]
    df, _ = reader(path)
    return df


def _from_filename(name: str) -> tuple[int | None, str | None]:
    """(essround, cntry) recovered from an SDDF filename where possible."""
    rnd = None
    m = re.search(r"ESS(\d+)", name, re.IGNORECASE)
    if m:
        rnd = int(m.group(1))
    cty = None
    m = re.search(r"ESS\d+[_-]?([A-Z]{2})[_-]?SDDF", name, re.IGNORECASE)
    if m:
        cty = m.group(1).upper()
    return rnd, cty


def _harmonize(df: pd.DataFrame, fname: str, report: dict) -> pd.DataFrame | None:
    df = df.rename(columns={c: COLMAP[c.lower()] for c in df.columns
                            if c.lower() in COLMAP})
    df = df.loc[:, ~df.columns.duplicated()]
    if "idno" not in df.columns or "psu" not in df.columns:
        report["skipped_no_keys"].append(fname)
        return None
    rnd, cty = _from_filename(fname)
    if "essround" not in df.columns:
        if rnd is None:
            report["skipped_no_round"].append(fname)
            return None
        df["essround"] = rnd
    if "cntry" not in df.columns:
        if cty is None:
            report["skipped_no_cntry"].append(fname)
            return None
        df["cntry"] = cty
    if "stratum" not in df.columns:
        df["stratum"] = 1.0
        report["stratum_filled"].append(fname)
    if "prob" not in df.columns:
        df["prob"] = np.nan
    keep = df[["cntry", "essround", "idno", "psu", "stratum", "prob"]].copy()
    keep["cntry"] = keep["cntry"].astype(str).str.strip().str.upper()
    for col in ("essround", "idno", "psu", "stratum", "prob"):
        keep[col] = pd.to_numeric(keep[col], errors="coerce")
    keep = keep.dropna(subset=["essround", "idno", "psu"])
    return keep


def load_sddf(sddf_dir: str = SDDF_DIR, cache: str | None = CACHE,
              verbose: bool = True) -> pd.DataFrame:
    """All SDDF files under sddf_dir, harmonized and deduplicated."""
    if cache and os.path.exists(cache):
        return pd.read_parquet(cache)
    report = {"skipped_no_keys": [], "skipped_no_round": [],
              "skipped_no_cntry": [], "stratum_filled": [], "read": []}
    frames = []
    for root, _, files in os.walk(sddf_dir):
        for f in sorted(files):
            path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if ext == ".zip":
                xdir = os.path.join(root, "_x_" + os.path.splitext(f)[0])
                if not os.path.exists(xdir):
                    with zipfile.ZipFile(path) as z:
                        z.extractall(xdir)
                continue
            if ext not in READABLE or f.startswith("."):
                continue
            try:
                raw = _read_any(path)
            except Exception as e:                      # unreadable vintage
                report["skipped_no_keys"].append(f"{f} ({e})")
                continue
            h = _harmonize(raw, f, report)
            if h is not None:
                frames.append(h)
                report["read"].append(f)
    # a zip pass may have extracted new readables: one more sweep
    extracted = [os.path.join(r, f) for r, _, fs in os.walk(sddf_dir)
                 for f in fs if "_x_" in r and
                 os.path.splitext(f)[1].lower() in READABLE
                 and not f.startswith(".")]
    for path in sorted(extracted):
        f = os.path.basename(path)
        if f in report["read"]:
            continue
        try:
            raw = _read_any(path)
        except Exception as e:
            report["skipped_no_keys"].append(f"{f} ({e})")
            continue
        h = _harmonize(raw, f, report)
        if h is not None:
            frames.append(h)
            report["read"].append(f)
    if not frames:
        raise FileNotFoundError(
            f"no usable SDDF files under {sddf_dir}; place the ESS Sample "
            "Design Data Files there (rounds 7-8: one integrated file per "
            "round; rounds 1-6: per-country files)")
    s = pd.concat(frames, ignore_index=True)
    dup = s.duplicated(["cntry", "essround", "idno"], keep=False)
    n_dup = int(dup.sum())
    s = s.drop_duplicates(["cntry", "essround", "idno"], keep="first")
    if verbose:
        print(f"SDDF ingest: {len(report['read'])} files, {len(s):,} rows, "
              f"{s.cntry.nunique()} countries, rounds "
              f"{sorted(s.essround.astype(int).unique())}")
        if n_dup:
            print(f"  duplicate (cntry, round, idno) keys dropped: {n_dup:,}")
        for k in ("skipped_no_keys", "skipped_no_round", "skipped_no_cntry",
                  "stratum_filled"):
            if report[k]:
                print(f"  {k}: {len(report[k])} -> {report[k][:5]}"
                      f"{' ...' if len(report[k]) > 5 else ''}")
    if cache:
        s.to_parquet(cache)
    return s


def merge_design(df: pd.DataFrame, sddf: pd.DataFrame,
                 verbose: bool = True) -> pd.DataFrame:
    """Fill missing psu/stratum in the integrated subset from the SDDF.

    Only rows whose integrated psu is missing are filled (rounds 9-11 keep
    their shipped design variables untouched), so the shipped core sample is
    bit-unchanged and the SDDF acts purely as an upgrade for rounds 1-8.
    """
    if "idno" not in df.columns:
        raise KeyError("integrated subset must be loaded with idno "
                       "(load(columns=COLS + ['idno']))")
    key = ["cntry", "essround", "idno"]
    m = df.merge(sddf.rename(columns={"psu": "psu_sddf",
                                      "stratum": "stratum_sddf",
                                      "prob": "prob_sddf"}),
                 on=key, how="left")
    fill = m["psu"].isna() & m["psu_sddf"].notna()
    m.loc[fill, "psu"] = m.loc[fill, "psu_sddf"]
    m.loc[fill, "stratum"] = m.loc[fill, "stratum_sddf"]
    if "prob" in m.columns:
        pfill = fill & m["prob"].isna()
        m.loc[pfill, "prob"] = m.loc[pfill, "prob_sddf"]
    if verbose:
        by_round = m[fill].groupby("essround").size()
        print(f"SDDF merge: filled psu/stratum for {int(fill.sum()):,} rows "
              f"({fill.mean():.1%} of subset) in rounds "
              f"{sorted(by_round.index.astype(int))}")
    return m.drop(columns=["psu_sddf", "stratum_sddf", "prob_sddf"])


def main():
    from pcb.data.audit_ess import COLS, load, audit
    df = load(columns=COLS + ["idno"])
    merged = merge_design(df, load_sddf())
    a_before, a_after = audit(df), audit(merged)
    up = (a_after["sample"] == "core") & (a_before["sample"] != "core")
    print(f"\ncountry-rounds upgraded to core: {int(up.sum())} "
          f"(core {int((a_before['sample'] == 'core').sum())} -> "
          f"{int((a_after['sample'] == 'core').sum())})")
    print(a_after[up][["cntry", "essround", "n", "psu", "stratum",
                       "n_psu"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
