# Documentation index — what is authoritative and what is history

A reviewer opening this directory should not have to guess which document
governs. Three tiers:

## Authoritative (kept current; the paper and code defer to these)

| doc | role |
|---|---|
| `DATA_SOURCES.md` | exact licensed-file editions, retrieval steps, sha256 checksums |
| `REPRODUCIBILITY.md` | two-tier reproduction protocol; what was verified bit-identical |
| `PROOFS.md` | proof notes backing the supplement (the supplement is the citable text) |
| `SAFE_SELECTOR_SPEC.md` | frozen selector constants and gate definitions the code implements |
| `PA_REVISION_PLAN.md` | current revision plan: external-review verification ledger + framing items |
| `DEVELOPMENT_ROADMAP.md` | current development plan: the four-contribution target and workstreams |

## Working session logs (current, but planning documents — not specs)

`HANDOFF.md`, `REVISION_TRIAGE.md` — status snapshots from earlier revision
rounds; superseded where they conflict with `PA_REVISION_PLAN.md` /
`DEVELOPMENT_ROADMAP.md`.

## Development history (kept for auditability; NOT current)

Everything else — preregistrations (`*_PREREGISTRATION.md`, `*_PREREG.md`),
results write-ups (`*_RESULTS.md`), gate protocols, schema audits, theory
scratch (`THEORY_MAIN.md`, `THEOREM_CANDIDATES.md`, `DESIGN_AWARE_*.md`,
`ADAPTIVE_WIDTH_THEORY.md`, `EFFICIENCY_THEORY.md`, ...). These record how
results and constants were derived and frozen, including two documented
withdrawals; where they mention a companion (poverty/PIP) project, that is the
development lineage of the shared clustered-band machinery, cited in the paper
as Park (2026). They are deliberately preserved unedited: the sealed-validation
story depends on their timestamps. Numbers in these files reflect the state at
their date and may differ from the current paper; the claim ledger
(`tests/test_paper_claims.py`) pins the current paper to the current CSVs.
