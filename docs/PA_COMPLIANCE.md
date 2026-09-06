# Political Analysis compliance audit (2026-08-20)

Checked against the live Cambridge author instructions
(`.../political-analysis/information/author-instructions/preparing-your-materials`,
fetched 2026-08-20). Status: ✅ compliant / 🔶 author action / ⬜ at-acceptance.

## Manuscript

| requirement | status | evidence / action |
|---|---|---|
| ≤ 6,000 words (abstract + body + figure legends + footnotes; excludes title page, references, words inside tables) | ✅ | **Measured 2026-09-06 with `texcount -inc main.tex`** (tabular cells excluded, math not counted). Before the pass: body 5,743 + abstract 193 + figure legends 190 = 6,126 (over). After the first pass: body 5,588 + 193 + 190 = 5,971. After the second read's additions (coordinate-level ρ, claim table, proof sketch, Bonferroni baselines, closed-testing assumption) and matching compression of §3/§4/§6/§7: body 5,590 + abstract 199 + figure legends 190 = 5,979. Third pass (headroom for the author's AI-disclosure sentence in §3, per PA's placement rule): body **5,511** + abstract **192** + figure legends 190 = **5,893**. Section headers (~170) and table captions (~165) are not in PA's definition; a Word-style count that included them would read ~6,300, so any further additions must be paid for. PA does not ask for the count to be stated on the title page. |
| Abstract ≤ 200 words | ✅ | **192** (`texcount`, 2026-09-06) |
| Keywords | ✅ | not required by PA |
| 12-pt, double-spaced, page numbers, footnotes at bottom | ✅ | `main.tex`: `12pt` + `\doublespacing`; article-class page numbers; no endnotes |
| Line numbers | ✅ | added by ScholarOne, not the author |
| Figures/tables embedded in text during review | ✅ | verified in PDF; Figure 4 float fixed earlier (was after references) |
| Figures legible on small screens; no landscape | ✅ | Figure 2 redrawn at 8.6″ with 9–10.5-pt labels; none landscape |
| Figure fonts Verdana/Arial preferred | ✅ | `pcb/figures/style.py` now prefers Arial → Verdana (falls back to DejaVu where unavailable) |
| Captions carry title, sample/period, notes, units | ✅ | spot-checked all four main figures (replicates, K, windows, α stated) |
| References: Chicago author-date, `chicago.bst` + natbib | ✅ | exactly this setup |
| **Data citations with persistent identifiers, in the reference list** | ✅/🔶 | `@misc` entries for ESS (all twelve integrated-file edition DOIs and the two SDDF DOIs in full `10.21338/...` form), the WVS Trend File v4.1 (doi:10.14281/18241.27; labelled WVS-only, not the EVS-merged IVS — the loader's 442,473 rows are the WVS file), LAPOP Grand Merge (doi:10.15695/lapop/CGD1393), V-Dem v15 (doi:10.23696/vdemds25), Claassen (doi:10.7910/DVN/HWLW0J), cited from the Data Availability Statement. |
| Statement order: Funding → Acknowledgments → Data Availability → Competing Interests → References | ✅ | `main.tex` back matter, in that order |
| Funding statement format | ✅ | "no specific grant" sentence |
| Data Availability Statement in PA's initial format (code location cited) | ✅ | now opens "Replication code for this article is available at ⟨repo⟩", Dataverse-on-acceptance line retained |
| Competing interests statement | ✅ | "The author declares none" (+ ScholarOne declaration at submission) |
| Title page: title, author, affiliation, corresponding contact, ORCID; no acknowledgments on it | ✅ | `titlepage.tex`; ORCID 0009-0007-9067-8964 |
| Single-anonymized (do NOT anonymize) | ✅ | full author block in `main.tex` and title page |
| Supplementary Material as separate PDF, not counted, published as-is | ✅ | `supplement.pdf`, S-numbered |
| Generative-AI policy: code/data-analysis use disclosed in methods; text/proof revision in Acknowledgments; cover-letter mention; tool, version, dates, access, scope | 🔶 | **Author action — placeholders intentionally retained** (see item 0 below). Slots: end of §3 (code/data analysis), Acknowledgments (text/proofs), cover letter (one sentence). Earlier drafts: `git show b28efc9:paper/main.tex`. The ledger test `test_no_author_placeholders_left` fails while the placeholders remain, so CI is red by design until this is written. |
| AI not an author | ✅ | single human author |

## Submission package

| requirement | status | evidence |
|---|---|---|
| Restricted-data notification to the editor at submission | ✅ | cover letter section, mirrors PA research-transparency policy |
| Replication materials at conditional acceptance (Dataverse; Code Ocean recommended for heavy dependencies) | ⬜ | `make deposit` builds the deterministic archive (`REPLICATION.md` §5); cover letter proposes a Code Ocean capsule |
| Reproducibility verifiable by the PA team | ✅ | contract tests + claim ledger (120 at the current main; CI green once the disclosure placeholders are removed); e13/e26/e50 verified bit-identical from raw files in two environments |

## Pre-submission pass, 2026-09-06

Done in this pass (all rebuilt, tests green, PDFs recompiled):

- Main text no longer leaks an experiment id (`\texttt{e46}` removed from §7).
- Three visible overfull lines fixed: the author/affiliation line under the
  title, Theorem 5's two-clause display (now `gather*`), and the repository
  URL in the Data Availability Statement (`url` package `hyphens` option).
- Supplement title block now carries the author (was "The Authors").
- Cover letter: addressed generically ("Dear Editors") — the journal's
  editorial-board page fetched 2026-09-06 lists Patrick T. Brandt as
  Editor-in-Chief from 1 September 2026 while the journal homepage still
  shows Hopkins/Stewart, so a named greeting is not safe until ScholarOne
  shows it; affiliation aligned with the manuscript; Proposition
  numbering corrected (unreachability is Proposition 2, claim-family
  transfer Proposition 1); bit-identical reproduction count updated to three.
- README / REPLICATION_MAP proposition numbers aligned with the compiled PDF.
- Dataset DOIs: ESS per-round edition DOIs and the WVS v4.1 DOI are in
  `refs.bib` (item 3 of the earlier list is closed).

Same day, from an external read-through of the main text (five P0/P1 items,
all applied; claim ledger green after each):

1. **Theorem 3 / Theorem 5 notation closed.** The statements now score the
   *observed* curves, $\widetilde R_c=\max_t|\widetilde E_c(t)|$, matching
   §2's definitions ($E_c$ latent, $\widetilde E_c$ observed) and §3's
   branch scores; the T1 target they guarantee is no longer stated with a
   latent score. (The supplement keeps its own self-contained convention,
   $E_c$ = plug-in curve, now flagged in its common setup.)
2. **"For every $K$" made literal.** Theorem 3 carries the
   $\widehat q=\infty$ convention when $\lceil(1-\alpha)(K{+}1)\rceil>K$
   (already in Proposition S1 and in the code), with the sentence "valid at
   every $K$, informative only for $K\ge\alpha^{-1}-1$"; §6's infeasibility
   remark now cites that convention.
3. **Claim family formalized** (new Table 2 in §3.1): contrast surface
   $\theta_{a,b}(t)=F_b(t)-F_a(t)$, core $\mathcal T_0$, and the events for
   pairwise / any-pair / net / persistent / recovery / across-country,
   with the certification condition for each — exactly what
   `certify_claim_family` computes.
4. **Theorem 5 proof sketch in the main text** (nested anchors below the
   floor; budget split + anchor-domination + union bound above it), replacing
   the compressed paragraph.
5. **§6–§7 compressed ~12%** (small-area and WVS detail trimmed toward the
   supplement; ESS claim ladder untouched), plus: the "not a monotone slide"
   sentence now rests explicitly on the certified decline+recovery evidence,
   not on persistent-rung non-certification; WVS is labelled an external
   substantive stress test, not a second validation; "nominal / theorem /
   validated operational" levels are named once in §3 and used consistently
   (§4, §6).

Second external read (proofs + code + CSVs cross-checked), same day — all
items applied except the one that needs the licensed microdata:

1. **ρ moved to the curve coordinate.** §2 now defines the design share
   $\rho(t)^2=\overline{v^2}(t)/s_{\rm plug}^2(t)$, where the additive model
   is exact, and states that the reported $\hat\rho_{\rm LCB}$ is a
   conservative aggregate (ratio of $t$-averaged bounds, exactly what
   `rho_lcb` computes); the score contamination $\xi=\tilde R-R$ is kept
   only as a defined quantity with $|\xi|\le\|S\|_\infty$, never treated as
   centred noise. Theorem 2(b)'s rate and (c)'s width factor, §3's
   $\sqrt{1-\rho(t)^2}$, Prop. 2(a), the efficiency paragraph and the
   supplement's common setup / Theorem 2 proof were rewritten to match.
2. **One notation system.** $G_c$ (latent deviation), $S_c$ (design
   error), $\tilde G_c=G_c+S_c$ (observed) in main text and supplement; the
   overloaded $E$ is gone (macro `\Gtilde`). Observed scores are
   $\tilde R_c$ throughout Theorems 3–5′ and the anchor-domination lemma.
3. **Closed testing: assumption stated, Bonferroni sensitivity added.**
   §7 and S4 state the Simes independence/PRDS requirement as a design
   assumption (not a property of separate RNG streams). `prevalence.py`
   gains Bonferroni local tests with a direct-closure subset bound, pinned
   to exhaustive closed testing on small families
   (`tests/test_prevalence_local_tests.py`); on the shipped p-values
   Bonferroni also gives d=6 and names the same six on both outcomes
   (ledger pin `test_ess_prevalence_bonferroni_sensitivity`).
4. **Wording:** "distribution-wide" → "over the preregistered core"
   (abstract, §1, §7, cover letter); Foa–Mounk reframed in §1 as the
   substantive thesis re-examined, not a methodological culprit; WVS "can
   only inflate" replaced by the clustering-vs-stratification statement;
   $\rho_0$ labelled a frozen operational cutoff (§3, §6); small-area
   activation labelled a feasibility demonstration up front, and the
   "marginal over regions" sentence now states the exchangeability
   presumption it rests on (§6).
5. **Bonferroni baselines in the wrong-unit simulation (e28).** New
   methods `per_round_bonf` / `marginal_bonf` at K=30 and a K=100
   companion CSV; the three original rows reproduce the committed CSV
   bit-identically. Finding: the corrected bands need K ≥ L/α−1 (79 at
   L=8; 479 for the threshold band), are infinite at survey K for L ≥ 4,
   and where feasible are 4–26% wider for the same or higher coverage. §5
   carries it; ledger pins it.
6. **e61 now reruns e56 under the SDDF upgrade** (`run_ess` refactor,
   writes `results/ess_prevalence_sddf.csv`, prints Simes and Bonferroni d
   against the shipped values).

**SDDF prevalence gate — CLOSED 2026-09-06.** The ESS inputs were fetched
through the ESS Data Portal API (integrated files by DOI; the 99 rounds 1–6
per-country SDDF archives from the portal catalogue; R7–8 SDDF by DOI), the
subset rebuilt by script, and e13/e40/e50/e56 reproduced bit-identically
from it. e61 then reran the prevalence p-values under the 88-country-round
SDDF upgrade: ten of sixty-six p-values move by at most 0.016 and **d = 6 on
both outcomes under Simes and under Bonferroni, same six countries**
(`results/ess_prevalence_sddf.csv`, pinned by
`test_cross_country_prevalence_sddf`; stated in §7 and S4).

## Remaining author actions

0. **AI disclosure — left blank on purpose (2026-09-06, author's decision to
   write it personally).** Three marked slots: `% AUTHOR TO WRITE` at the
   end of `sections/03_method.tex` (code/data-analysis use, Methods),
   the visible bold placeholder in `main.tex` Acknowledgments (text/proof
   use), and the bold placeholder in `cover_letter.md`. The previous drafts
   are in git history (commit `b28efc9`, `paper/main.tex`). Ledger test
   `test_no_author_placeholders_left` fails until the visible placeholders
   are removed (a hard failure, not an xfail), so the tree cannot pass CI
   in a submittable-looking state with them present. After submission,
   set `preferred-citation.journal` in `CITATION.cff` to "Under review,
   Political Analysis".
1. (superseded by 0) AI disclosure: both halves were written (Acknowledgments + Data
   Availability Statement) — review the wording, adjust if desired.
2. Read-through of the full PDF (voice pass), with particular attention to
   §2's rewritten objects paragraph, Table 2, and the §4 proof sketch.
3. Confirm the masthead on the day of submission (the editorial transition
   was dated 1 September 2026).
