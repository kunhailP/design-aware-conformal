#!/usr/bin/env bash
# Tier 2 -- the licensed-microdata reanalyses (ESS, WVS, LAPOP). The inputs
# are not redistributed: obtain them per docs/DATA_SOURCES.md (or build the
# ESS subset through the ESS Data Portal API with scripts/fetch_ess_api.py +
# scripts/build_ess_subset.py) and place them at the paths below. The script
# checks presence and, for Wizard/provider downloads, the sha256, then runs
# the Tier 2 pipeline. Set ESS_SDDF=1 to include the rounds 1-8 SDDF rerun
# (e61; needs data/ess/sddf/, see DATA_SOURCES.md 1b). ~1-2 h on one core.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}

declare -A SHA=(
  ["data/ess/Datafile-subset.dta"]="bbabd8f6a071d566e9cc7741d321b3c09d70ec500efd221bb668fef749e581b2"
  ["data/wvs/data_pa/Trends_VS_1981_2022_Stata_v4_1.dta"]="d12c6e3ced6bef34a08917eb504c392795efa2aa7a7e614de37cfdc35c822c0f"
  ["data/lapop/raw/Grand_Merge_2004-2023_LAPOP_AmericasBarometer_v1.0_FREE.dta"]="06af29d17362db51f78720651b39d1734ca7f8255484fc3a1923becc37fa3c29"
)
# ESS is the one input with a sanctioned alternative route (the API-built
# subset of scripts/build_ess_subset.py differs byte-wise from the Wizard
# download but reproduces every headline CSV bit-identically); a mismatch
# there is reported and checked downstream. WVS and LAPOP have no such route:
# a checksum mismatch means a different edition, and the run stops.
missing=0; bad=0
for f in "${!SHA[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING  $f  (see docs/DATA_SOURCES.md)"; missing=1; continue
  fi
  got=$(sha256sum "$f" | cut -d' ' -f1)
  if [ "$got" = "${SHA[$f]}" ]; then
    echo "OK       $f  (sha256 matches the provider download)"
  elif [[ "$f" == data/ess/* ]]; then
    echo "PRESENT  $f  (sha256 differs from the Wizard download: allowed for the"
    echo "         script-built ESS subset; headline CSVs are verified below)"
  else
    echo "MISMATCH $f  (sha256 differs from the cited edition; see docs/DATA_SOURCES.md)"; bad=1
  fi
done
if [ "$missing" -eq 1 ]; then
  echo "licensed inputs missing; nothing run. Place the files and rerun."; exit 2
fi
if [ "$bad" -eq 1 ]; then
  echo "licensed input edition mismatch; nothing run."; exit 3
fi

echo "== Tier 2: loaders + reanalyses"
make PY="$PY" tier2
if [ "${ESS_SDDF:-0}" = "1" ]; then
  echo "== e61: rounds 1-8 SDDF upgrade (long window, joint band, prevalence)"
  $PY -m pcb.experiments.e61_sddf_long_window
fi
echo "== bit-identity check of the regenerated headline CSVs against results/EXPECTED_SHA256SUMS"
if [ "${ESS_SDDF:-0}" = "1" ]; then
  sha256sum -c results/EXPECTED_SHA256SUMS
else
  grep -v "_sddf.csv" results/EXPECTED_SHA256SUMS | sha256sum -c -
fi
echo "run_restricted.sh complete: every headline CSV reproduced bit-identically"
