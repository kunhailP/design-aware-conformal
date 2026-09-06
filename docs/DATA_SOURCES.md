# Data sources — exact files, retrieval, and placement

Three licensed survey microdata files drive every real-data result. None is
redistributed here (`/data/` is gitignored); each is freely available after
registration with its provider. Place the files exactly as below — the loaders in
`pcb/data/` hard-code these paths.

## 1. European Social Survey (ESS), rounds 1–11

- **What**: ESS Data Wizard subset of the integrated files, all countries, rounds
  1–11, with the variables listed below.
- **Where**: <https://ess.sikt.no> → Data Wizard → select rounds 1–11, all
  countries, and the variables: `essround, cntry, trstprl, trstplt, trstprt,
  stfdem, ppltrst, dweight, pspwght, pweight, anweight, psu, stratum, prob`.
  Download as Stata (`.dta`). Registration is free; the ESS End User Licence
  applies.
- **Place at**: `data/ess/Datafile-subset.dta`
- **Verify**: 1,959,409,874 bytes; sha256
  `bbabd8f6a071d566e9cc7741d321b3c09d70ec500efd221bb668fef749e581b2`
- **Scripted alternative (verified 2026-09-06)**: the same subset can be built
  from the ESS Data Portal API without the Wizard. With your ESS user ID
  (shown on the portal's API page after registration):
  ```bash
  ESS_USER_ID=<id> python scripts/fetch_ess_api.py     # 12 integrated + 2 SDDF Parquets, ~95 MB
  python scripts/build_ess_subset.py                   # -> data/ess/Datafile-subset.dta
  ```
  The API serves each cited edition DOI (`refs.bib`, `essdata2024`) as a
  Parquet file; the build script stacks rounds 1–11 (round 10 = face-to-face
  file then self-completion file), keeps the Wizard variables plus `idno` and
  `mode`, and recodes the ESS missing codes (77/88/99; `mode` 9) to missing as
  the Stata files do. The file it writes differs byte-wise from the Wizard
  download (different writer), but every country × round count equals
  `results/ess_audit.csv` and `e13` reproduces
  `results/ess_country_certification.csv` **bit-identically** from it — the
  within-country row order the bootstrap depends on is the integrated files'.
- **Notes**: PSU/stratum ship in the *integrated* files only from round 9; rounds
  1–8 carry outcomes and weights (the long-window analysis `e36` uses a
  weights-only bootstrap there, disclosed in the paper).

### 1b. ESS Sample Design Data Files (SDDF), rounds 1–8

- **What**: the separately distributed design variables (`idno, cntry, psu,
  stratify, prob`) for rounds 1–8. Rounds 7–8 ship as one integrated file per
  round; rounds 1–6 as per-country files (not every country-round exists, and
  some carry no PSU — those stay weights-only).
- **Where**: <https://ess.sikt.no> — rounds 7–8 via the ESS API
  (`https://api.ess.sikt.no/v1/data/dataFile/10.21338/ess7sddfe1_2` and
  `.../ess8sddfe01_1`, with your ESS user ID; CSV format), rounds 1–6 from each
  round's country documentation pages (`.spss.zip` archives).
- **Place at**: `data/ess/sddf/` (any nesting; `.csv/.sav/.dta/.por`, zips are
  auto-extracted). Old-vintage `.por` files unreadable by pyreadstat can be
  converted to CSV with R's `foreign::read.spss`.
- **Scripted alternative (verified 2026-09-06)**:
  ```bash
  ESS_USER_ID=<id> python scripts/fetch_ess_api.py ess7sddfe1_2 ess8sddfe01_1   # rounds 7-8 (then export the Parquets to CSV under data/ess/sddf/)
  python scripts/fetch_ess_sddf.py          # rounds 1-6: 99 per-country .spss.zip archives from the portal catalogue
  Rscript scripts/convert_sddf_por.R        # converts the .por vintages pyreadstat cannot read (needs R + `foreign`)
  python -m pcb.data.ess_sddf               # ingest: 88 country-rounds upgraded to core (90 -> 178)
  ```
  The rounds 1–6 archives are the "Sample data (SDDF)" related materials of
  each country page (public document store; no user ID needed). Of the 72
  `.por` files, pyreadstat reads 46 and R's `foreign` reads the other 26; both
  are needed for the full set.
- **Used by**: `pcb.data.ess_sddf` (merge on `cntry, essround, idno`, filling
  psu/stratum only where the integrated file lacks them) and
  `pcb.experiments.e61_sddf_long_window` (the long-window rerun; upgrades 88
  country-rounds, changes no net or persistent count — committed outputs
  `results/ess_long_window_sddf.csv`, `results/ess_joint_claims_sddf.csv`,
  `results/ess_prevalence_sddf.csv`).

## 2. World Values Survey (WVS) Trend File, 1981–2022

- **What**: the WVS-only Trend File 1981–2022, version 4.1 (`WVS_Trend_1981_2022_v4.1`,
  Stata; 442,473 cases, 108 countries/territories, 306 surveys; doi:10.14281/18241.27).
  This is **not** the Integrated Values Surveys (IVS) file that merges the EVS trend
  (666,907 cases): the separately distributed EVS trend file is not merged in, and
  the paper labels every result from this file "WVS".
- **Where**: <https://www.worldvaluessurvey.org/WVSEVStrend.jsp> (registration and
  purpose statement required by the WVSA terms).
- **Place at**: `data/wvs/data_pa/Trends_VS_1981_2022_Stata_v4_1.dta`
- **Verify**: 499,799,219 bytes; sha256
  `d12c6e3ced6bef34a08917eb504c392795efa2aa7a7e614de37cfdc35c822c0f`
- **Notes**: the trend file ships weights (exposed as `_w` by the loader) but
  **no PSU/stratum identifiers**; every WVS band in the paper is therefore
  weights-only, with the understated-variance direction disclosed.

## 3. AmericasBarometer / LAPOP Grand Merge, 2004–2023

- **What**: `Grand_Merge_2004-2023_LAPOP_AmericasBarometer_v1.0_FREE.dta` (free
  public version).
- **Where**: <https://www.vanderbilt.edu/lapop/> → data access (free after
  registration).
- **Place at**:
  `data/lapop/raw/Grand_Merge_2004-2023_LAPOP_AmericasBarometer_v1.0_FREE.dta`
- **Verify**: 1,118,523,828 bytes; sha256
  `06af29d17362db51f78720651b39d1734ca7f8255484fc3a1923becc37fa3c29`
- **Notes**: full stratified-PSU structure ships in the merged file; the loader
  excludes the 2021 phone-mode round (documented in `pcb/data/audit_lapop.py`).

## Public, redistributable inputs

- **V-Dem v15** country–year (`v2x_regime`, `v2x_polyarchy`): via the
  `vdemdata` repository (<https://github.com/vdeminstitute/vdemdata>,
  `data/vdem.RData`); path set by `VDEM_PATH` for `e35`.
- **Claassen support-for-democracy panel** (corrected AJPS series): Harvard
  Dataverse `doi:10.7910/DVN/HWLW0J` (`Support_democracy_ajps_correct.csv`);
  path set by `CLAASSEN_PATH` for `e37`. Original PA-2019 materials:
  `doi:10.7910/DVN/A47LUM`.

## Loader entry points (code is authoritative for recodes)

| survey | schema audit | cache built |
|---|---|---|
| ESS | `python -m pcb.data.audit_ess` | `data/ess/core_audit.parquet` |
| ESS panel | `python -m pcb.data.ess_panel` | `data/ess/panel.parquet` |
| WVS | `python -m pcb.data.audit_wvs` | `data/wvs/trends_deconsolidation.parquet` |
| LAPOP | `python -m pcb.data.audit_lapop` | `data/lapop/*.parquet` |

Weight construction: ESS uses `anweight` with `pspwght` fallback (the
population-size weight `pweight` is a within-country constant and cancels in
country CDFs). Item recodes, missing-code handling, and sample filters live in
the loaders — treat the code, not this file, as the authority.
