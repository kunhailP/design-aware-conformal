"""Download ESS data files through the ESS Data Portal API.

The portal (https://ess.sikt.no) serves every data file by DOI through
    https://api.ess.sikt.no/v1/data/dataFile/10.21338/<doi>?format=csv&userId=<id>
which answers with a 307 redirect to a time-limited blob URL; the body is a
Parquet file whatever `format` says. `<id>` is the registered user's ESS user
ID (free registration; the ESS End User Licence applies). Nothing here is
redistributed: the script fetches into the gitignored data/ tree.

Usage:
    ESS_USER_ID=<your id> python scripts/fetch_ess_api.py            # everything
    ESS_USER_ID=<your id> python scripts/fetch_ess_api.py ess9e03_3   # one DOI

The DOIs below are the integrated-file editions cited in paper/refs.bib
(`essdata2024`) plus the rounds 7-8 SDDF files. Rounds 1-6 SDDF files are
per-country; pass their DOIs on the command line once known.
"""
from __future__ import annotations
import os
import sys
import urllib.request

INTEGRATED = ["ess1e06_7", "ess2e03_6", "ess3e03_7", "ess4e04_6", "ess5e03_6",
              "ess6e02_7", "ess7e02_3", "ess8e02_3", "ess9e03_3", "ess10e03_3",
              "ess10sce03_2", "ess11e04_2"]
SDDF = ["ess7sddfe1_2", "ess8sddfe01_1"]
OUT_DIR = "data/ess/api"


def fetch(doi: str, user_id: str, out_dir: str = OUT_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{doi}.parquet")
    url = (f"https://api.ess.sikt.no/v1/data/dataFile/10.21338/{doi}"
           f"?format=csv&userId={user_id}")
    with urllib.request.urlopen(url, timeout=1800) as r:      # follows the 307
        clen = r.headers.get("Content-Length")
        n = 0
        with open(out + ".part", "wb") as f:
            while True:
                b = r.read(1 << 22)
                if not b:
                    break
                f.write(b)
                n += len(b)
    if clen is not None and int(clen) != n:
        raise IOError(f"{doi}: expected {clen} bytes, got {n}")
    with open(out + ".part", "rb") as f:
        f.seek(-4, 2)
        if f.read(4) != b"PAR1":
            raise IOError(f"{doi}: not a complete Parquet file")
    os.replace(out + ".part", out)
    print(f"{doi:14s} {n/1e6:8.1f} MB -> {out}", flush=True)
    return out


def main(argv):
    user_id = os.environ.get("ESS_USER_ID")
    if not user_id:
        sys.exit("set ESS_USER_ID to your ESS Data Portal user ID")
    dois = argv or (INTEGRATED + SDDF)
    for doi in dois:
        out = os.path.join(OUT_DIR, f"{doi}.parquet")
        if os.path.exists(out):
            print(f"{doi:14s} present, skipping")
            continue
        fetch(doi, user_id)


if __name__ == "__main__":
    main(sys.argv[1:])
