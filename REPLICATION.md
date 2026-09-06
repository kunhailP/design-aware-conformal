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
| 2026-08-29 | fresh Linux container | e13, e26, e50 **and the e38 rescaled CSVs** reproduce bit-identically from sha256-verified inputs; the rounds 1–8 SDDF merge (e61) and the small-area rescaling sensitivity (e62) were run in this environment and their outputs committed |
| 2026-09-06 | fresh Linux container, **ESS inputs fetched by script through the ESS Data Portal API** (`scripts/fetch_ess_api.py`, `fetch_ess_sddf.py`, `build_ess_subset.py`; no Wizard download) | `ess_audit.csv` and **e13, e36, e40, e50, e56 reproduce bit-identically**; the SDDF merge upgrades the same 88 country-rounds; e61 reproduces `ess_joint_claims_sddf.csv` bit-identically and `ess_long_window_sddf.csv` value-identically (run before the integer-type fix in the build script; round columns printed as floats), and its new prevalence rerun (`ess_prevalence_sddf.csv`, committed) leaves the closed-testing bound at d = 6 on both outcomes |

## 1. Environment

- Python 3.11 (tested 3.11.10), CPU only. Exact package versions in
  `requirements.txt`; the two bit-identical reproductions above ran under
  those pins. R ≥ 4.2 only for the optional R port (`rpkg/dapcb`).
- Install: `pip install -r requirements.txt && pip install -e .`
- Hardware: any modern machine; nothing is parallelized, so wall-clock
  scales with single-core speed. Reference environment for the 2026-09-06
  reproduction: Ubuntu 22.04 container on Linux 6.8, AMD EPYC 7H12 (2
  sockets, 256 threads; one core used), 1 TiB RAM (peak resident set for the
  ESS `.dta` read ≈ 8–16 GB; 32 GB is ample), 20 GB disk (the ESS API
  Parquets and rebuilt subset take ≈ 0.3 GB; the Wizard `.dta` alone is
  2.0 GB), Python 3.11.10, R 4.1.2. Wall-clock there: Step 0 ≈ 45 s, e13
  ≈ 4 min, e36 ≈ 10 min, e50 ≈ 10 min, e56 ≈ 8 min, e61 ≈ 50 min
  (rounds 1–8 SDDF merge included). Runtimes in the tables below are from
  the same class of machine.
- Shell entry points (PA replication-guideline layout): `setup.sh`
  (environment), `run_public.sh` (Tier 1: tests, simulations, public-data
  analyses, figures), `run_restricted.sh` (Tier 2: verifies the licensed
  inputs' sha256 first, then the survey reanalyses), `run_all.sh` (both).
  `make` targets remain the fine-grained interface.

## 2. Run order

### Step 0 — contract tests (no data, ~20 s)

```bash
python -m pytest tests/ -q          # pytest reports the current count (119 at v1.1)
```

Theorem↔code contract tests plus the claim ledger. **If this
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
| `e38` | `results/*_rescaled.csv` (Rao–Wu–Yue sensitivity) | 1–2 h |
| `e62` | `results/small_area_transport_rescaled.csv` (RWY small-area sensitivity) | 1–2 h |
| `e61` | `results/ess_long_window_sddf.csv`, `results/ess_joint_claims_sddf.csv`, `results/ess_prevalence_sddf.csv` (rounds 1–8 SDDF upgrade; additionally needs the SDDF files per `docs/DATA_SOURCES.md` §1b). The prevalence rerun re-derives the closed-testing "at least six" on the design-upgraded p-value vector and prints Simes and Bonferroni d against the shipped values (both stay at 6; ledger pin `test_cross_country_prevalence_sddf`) | 40–75 min |

To verify bit-identity yourself: back up the committed CSV, rerun the
experiment, and `diff` — all runs are deterministic under fixed seeds
(`pcb.util.det_seed`).

### Step 3 — figures and paper (~3 min)

```bash
make figures && make paper
```


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
