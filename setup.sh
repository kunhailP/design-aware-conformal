#!/usr/bin/env bash
# Environment setup for the replication archive (run once, before run_*.sh).
# Python 3.11 + pinned packages + this package in editable mode. R (>= 4.1
# with the recommended package `foreign`) is optional: needed only for the R
# port (rpkg/dapcb) and for converting old SPSS portable SDDF files.
set -euo pipefail
cd "$(dirname "$0")"
python3 --version
python3 -m pip install --upgrade pip >/dev/null
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
if command -v Rscript >/dev/null 2>&1; then
  Rscript -e 'cat("R", R.version.string, "- foreign:", requireNamespace("foreign", quietly=TRUE), "\n")'
else
  echo "R not found: optional (rpkg/dapcb and scripts/convert_sddf_por.R only)"
fi
echo "setup complete"
