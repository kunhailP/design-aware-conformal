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
- **Notes**: PSU/stratum ship in the *integrated* files only from round 9; rounds
  1–8 carry outcomes and weights (the long-window analysis `e36` uses a
  weights-only bootstrap there, disclosed in the paper). The separate Sample
  Design Data Files (rounds 1–8) would upgrade those rounds to the full design
  bootstrap and are flagged as a revision item.

## 2. World Values Survey / EVS trend file, 1981–2022

- **What**: WVS/EVS joint trend file, Stata version 4.1
  (`Trends_VS_1981_2022_stata_v4_1`).
- **Where**: <https://www.worldvaluessurvey.org/WVSEVStrend.jsp> (registration and
  purpose statement required by the WVSA/EVS terms).
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
