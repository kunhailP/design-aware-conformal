# Convenience targets. Entry point for replication: REPLICATION.md

PY ?= python

.PHONY: install test verify tier1 tier2 figures paper deposit clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	$(PY) -m pytest tests/ -q

# Full verification pass for a replication analyst: contract tests + claim
# ledger, then the fast no-microdata analyses that read committed results.
verify: test
	$(PY) -m pcb.experiments.e57_feasibility_frontier
	$(PY) -m pcb.experiments.e58_center_exactness

# Tier 1 — no microdata: simulation / theory / benchmarks (fast subset;
# e22/e33 grids take hours and are excluded here — run them directly).
tier1:
	$(PY) -m pcb.experiments.e28_wrong_unit_coverage
	$(PY) -m pcb.experiments.e32_severity
	$(PY) -m pcb.experiments.e29_beyond_surveys
	$(PY) -m pcb.experiments.e11_gate5c
	$(PY) -m pcb.experiments.e19_selector_sweep
	$(PY) -m pcb.experiments.e30_certified_core
	$(PY) -m pcb.experiments.e31_positive_regime
	$(PY) -m pcb.experiments.e60_wrong_unit_landscape

# Tier 2 — requires licensed microdata placed per docs/DATA_SOURCES.md.
tier2:
	$(PY) -m pcb.data.audit_ess
	$(PY) -m pcb.data.ess_panel
	$(PY) -m pcb.data.audit_wvs
	$(PY) -m pcb.data.audit_lapop
	$(PY) -m pcb.experiments.e13_ess_audit
	$(PY) -m pcb.experiments.e36_ess_long_window
	$(PY) -m pcb.experiments.e26_wvs_deconsolidation
	$(PY) -m pcb.experiments.e50_joint_claim_family
	$(PY) -m pcb.experiments.e54_small_area_transport
	$(PY) -m pcb.experiments.e55_small_area_exchangeability
	$(PY) -m pcb.experiments.e56_prevalence
	$(PY) -m pcb.experiments.e59_wvs_magnitudes

# Curated, deterministic replication archive (see REPLICATION.md §5).
deposit:
	$(PY) scripts/build_deposit.py

figures: figures-r
	@for f in pcb/figures/fig_*.py; do \
	  m=$$(basename $$f .py); echo "-> $$m"; \
	  $(PY) -m pcb.figures.$$m || exit 1; \
	done

# Main Figures 1-4: R publication layer (reads results/*.csv only).
figures-r:
	Rscript paper_figures/main_figures.R

paper:
	cd paper && pdflatex -interaction=nonstopmode main.tex >/dev/null && \
	  bibtex main >/dev/null && \
	  pdflatex -interaction=nonstopmode main.tex >/dev/null && \
	  pdflatex -interaction=nonstopmode main.tex >/dev/null && \
	  pdflatex -interaction=nonstopmode supplement.tex >/dev/null && \
	  bibtex supplement >/dev/null && \
	  pdflatex -interaction=nonstopmode supplement.tex >/dev/null && \
	  pdflatex -interaction=nonstopmode supplement.tex >/dev/null && \
	  echo "built main.pdf + supplement.pdf"

clean:
	rm -rf figures/ **/__pycache__ paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out
