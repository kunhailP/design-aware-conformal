"""Fetch the rounds 1-6 per-country ESS Sample Design Data Files (SDDF).

Rounds 7-8 ship integrated SDDF files with DOIs (scripts/fetch_ess_api.py).
Rounds 1-6 are per-country archives listed only on each country's
documentation page of the ESS Data Portal. This script reads those pages the
way the portal does -- the public GraphQL catalogue (api.nsd.no/graphql,
`countrySeriesMetadata`, related materials of type "Sample data (SDDF)") --
and downloads every `.spss.zip` it lists from the portal's public document
store into data/ess/sddf/round<N>/ (gitignored; the ESS End User Licence
applies). `pcb.data.ess_sddf` then ingests them (zips are auto-extracted).

Usage:  python scripts/fetch_ess_sddf.py
"""
from __future__ import annotations
import json
import os
import urllib.request

GRAPHQL = "https://api.nsd.no/graphql"
DOC_STORE = "https://stessrelpubprodwe.blob.core.windows.net/data"
ESS_SERIES_ID = "321b06ad-1b98-4b7d-93ad-ca8a24e8788a"
OUT_DIR = "data/ess/sddf"

QUERY = """
query countrySeriesMetadata($countryCode: String!, $seriesId: ID!,
                            $instance: Instance!, $agencyId: Agency!) {
  search {
    countrySeriesMetadata(countryCode: $countryCode, seriesId: $seriesId,
                          instance: $instance, agencyId: $agencyId) {
      seriesCoverage { spatialCoverage {
        countryCategoriesControlledVocabulary { value } } }
      studies {
        studyCitation { title { en } }
        dataCollection {
          relatedMaterials { typeOfMaterial { en } alternateTitle { en } url }
        }
      }
    }
  }
}"""


def _gql(variables: dict) -> dict:
    req = urllib.request.Request(
        GRAPHQL, data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Content-Type": "application/json", "Origin": "https://ess.sikt.no"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def sddf_links() -> list[dict]:
    base = dict(seriesId=ESS_SERIES_ID, instance="PUBLISHED", agencyId="INT_ESSERIC")
    first = _gql(dict(base, countryCode="AT"))["data"]["search"]["countrySeriesMetadata"]
    codes = [c["value"] for c in first["seriesCoverage"]["spatialCoverage"]
             ["countryCategoriesControlledVocabulary"]]
    links = []
    for cc in codes:
        meta = _gql(dict(base, countryCode=cc))["data"]["search"]["countrySeriesMetadata"]
        for st in meta["studies"]:
            rnd = st["studyCitation"]["title"]["en"]           # "ESS1" ... "ESS11"
            for m in (st.get("dataCollection") or {}).get("relatedMaterials") or []:
                kind = ((m.get("typeOfMaterial") or {}).get("en") or "").lower()
                url = m.get("url") or ""
                if "sddf" in kind or "sddf" in url.lower():
                    links.append(dict(cntry=cc, round=rnd, url=url))
    return links


def main():
    links = sddf_links()
    print(f"{len(links)} SDDF archives listed for rounds 1-6")
    for l in links:
        rnd = int(l["round"].replace("ESS", ""))
        out_dir = os.path.join(OUT_DIR, f"round{rnd}")
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, os.path.basename(l["url"]))
        if os.path.exists(out):
            continue
        with urllib.request.urlopen(DOC_STORE + l["url"], timeout=600) as r, \
                open(out + ".part", "wb") as f:
            f.write(r.read())
        os.replace(out + ".part", out)
        print(f"  {l['round']:5s} {l['cntry']}  {os.path.getsize(out)/1e3:7.0f} kB  {out}")
    json.dump(links, open(os.path.join(OUT_DIR, "sddf_links.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
