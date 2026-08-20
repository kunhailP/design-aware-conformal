# Replication — start here

This file is the single entry point for a replication analyst. It states the
environment, the run order, what each step produces, how long it takes, and —
most importantly — where every number in the paper is pinned to a machine
check. Nothing in the paper rests on a number that is not either (a) in a
committed CSV under `results/` and pinned by `tests/test_paper_claims.py`, or
(b) an algebraic identity pinned by a contract test.

Verified reproductions to date (both from the raw licensed files, in
independent environments):

| date | environment | result |
|---|---|---|
| 2026-07-27 | author machine | e13 (ESS certification) and e26 (WVS hierarchy) reproduce the committed CSVs **bit-identically** |
| 2026-08-20 | fresh Linux container, this package's pinned versions | e13, e26, **and e50** (joint claim family) reproduce **bit-identically**; input files verified by sha256 against `docs/DATA_SOURCES.md` |

## 1. Environment

- Python 3.11 (tested 3.11.10), CPU only. Exact package versions in
  `requirements.txt`; the two bit-identical reproductions above ran under
  those pins. R ≥ 4.2 only for the optional R port (`rpkg/dapcb`).
- Install: `pip install -r requirements.txt && pip install -e .`
- Hardware: any modern machine. Runtimes below are from a 2026 Linux server;
  wall-clock scales with single-core speed (nothing is parallelized).

## 2. Run order

### Step 0 — contract tests (no data, ~20 s)

```bash
python -m pytest tests/ -q          # 104 tests
```

70 theorem↔code contract tests plus the claim ledger. **If this
passes, every headline number in the manuscript matches the committed CSVs**
— the ledger is the authoritative map from paper claims to artifacts (each
test names the CSV and the claim text it pins).

### Step 1 — Tier 1: no microdata (~15 min)

```bash
make tier1        # e28 e32 e29 e11 e19 e30 e31
python -m pcb.experiments.e57_feasibility_frontier   # frontier (committed CSVs)
python -m pcb.experiments.e58_center_exactness       # LOO seam (~1 min)
```

Simulation, theory checks, and every analysis that runs from committed
results. Two sealed validation grids are excluded from `tier1` for time
(`e22`, `e33`, several hours each); their frozen outputs and script hashes
are in `configs/`.

### Step 2 — Tier 2: licensed microdata (~30–60 min total)

Place the three licensed files exactly per `docs/DATA_SOURCES.md` (free
registration with each provider; sha256 checksums listed there — verify
before running). Then:

```bash
make tier2        # loaders + e13 e36 e26 e50 e54 e55
python -m pcb.experiments.e56_prevalence             # closed-testing bound
```

| step | produces | ~time |
|---|---|---|
| `pcb.data.audit_ess` | `data/ess/core_audit.parquet` | 3–5 min |
| `pcb.data.audit_wvs` / `audit_lapop` | WVS/LAPOP parquets | 2–5 min each |
| `e13` | `results/ess_country_certification.csv` (**bit-identical check**) | 3–6 min |
| `e26` | `results/wvs_deconsolidation.csv` (**bit-identical check**) | 3–6 min |
| `e50` | `results/ess_joint_claims.csv` (**bit-identical check**) | 5–15 min |
| `e36`, `e54`, `e55` | long window; small-area activation + holdout | 5–15 min each |
| `e56` | `results/ess_prevalence.csv` (prevalence d=6) | 5–10 min |

To verify bit-identity yourself: back up the committed CSV, rerun the
experiment, and `diff` — all runs are deterministic under fixed seeds
(`pcb.util.det_seed`).

### Step 3 — figures and paper (~3 min)

```bash
make figures && make paper
```

Supplement figures are matplotlib (`pcb/figures/`); the four **main** figures
are drawn by an R publication layer (`paper_figures/main_figures.R`, run via
`make figures-r`) that reads only committed `results/*.csv` — R >= 4.1 with
ggplot2, dplyr/tidyr/readr, cowplot, ggrepel, sf, scico. The committed PDFs
under `paper/figures/` are the canonical versions either way.

## 3. Where each number lives

`docs/REPLICATION_MAP.md` maps every headline claim in the manuscript to
(experiment → CSV → ledger test). The short version: if you change any
committed CSV or any pinned sentence of the paper, `pytest tests/ -q` fails.

## 4. What is deliberately preserved

`docs/` keeps the full development lineage — preregistrations, frozen-gate
derivations, two documented withdrawals with diagnoses, and the sealed
validation manifests whose script hashes were recorded before first
execution (`configs/`). `docs/README.md` states which documents are
authoritative and which are history. This is audit material, not run
instructions; nothing in Steps 0–3 depends on it.

## 5. Building the deposit archive

```bash
make deposit      # -> dist/dapcb-replication-<version>.zip + SHA256SUMS
```

Assembles the curated archive (code, tests, results, configs, paper sources
and PDFs, R package, docs with index; licensed data excluded) with a
deterministic file order and a SHA256 manifest of every shipped file.
