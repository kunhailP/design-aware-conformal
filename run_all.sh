#!/usr/bin/env bash
# Master script: public tier, then the restricted tier if the licensed inputs
# are present, then the paper build (needs a TeX Live with chicago.bst).
set -euo pipefail
cd "$(dirname "$0")"
./run_public.sh
if ./run_restricted.sh; then :; else
  rc=$?
  if [ "$rc" -eq 2 ]; then echo "restricted tier skipped (inputs missing)"; else exit "$rc"; fi
fi
if command -v pdflatex >/dev/null 2>&1; then make paper; else echo "pdflatex not found: paper build skipped"; fi
echo "run_all.sh complete"
