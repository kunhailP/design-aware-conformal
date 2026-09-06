#!/usr/bin/env bash
# Tier 1 -- everything that needs no licensed microdata, non-interactively:
# contract tests + claim ledger, the simulation/theory experiments, the
# analyses that read committed results, and the paper figures. Outputs go to
# results/ and figures/ (relative paths throughout). ~20 min on one core.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
echo "== Step 0: contract tests + claim ledger"
$PY -m pytest tests/ -q
echo "== Step 1: Tier 1 experiments"
make PY="$PY" tier1
$PY -m pcb.experiments.e57_feasibility_frontier
$PY -m pcb.experiments.e58_center_exactness
echo "== Figures (from committed results/*.csv)"
make PY="$PY" figures
echo "run_public.sh complete"
