# Political Analysis compliance audit (2026-08-20)

Checked against the live Cambridge author instructions
(`.../political-analysis/information/author-instructions/preparing-your-materials`,
fetched 2026-08-20). Status: ✅ compliant / 🔶 author action / ⬜ at-acceptance.

## Manuscript

| requirement | status | evidence / action |
|---|---|---|
| ≤ 6,000 words (abstract + body + figure legends + footnotes; excludes title page, references, words inside tables) | 🔶 | Estimated at/near the cap after the prevalence addition; **author runs the official count on the final PDF** (note in `titlepage.tex`). Rule stated on the title page matches PA's. |
| Abstract ≤ 200 words | ✅ | **198** by prose count (script in repo history) |
| Keywords | ✅ | not required by PA |
| 12-pt, double-spaced, page numbers, footnotes at bottom | ✅ | `main.tex`: `12pt` + `\doublespacing`; article-class page numbers; no endnotes |
| Line numbers | ✅ | added by ScholarOne, not the author |
| Figures/tables embedded in text during review | ✅ | verified in PDF; Figure 4 float fixed earlier (was after references) |
| Figures legible on small screens; no landscape | ✅ | Figure 2 redrawn at 8.6″ with 9–10.5-pt labels; none landscape |
| Figure fonts Verdana/Arial preferred | ✅ | `pcb/figures/style.py` now prefers Arial → Verdana (falls back to DejaVu where unavailable) |
| Captions carry title, sample/period, notes, units | ✅ | spot-checked all four main figures (replicates, K, windows, α stated) |
| References: Chicago author-date, `chicago.bst` + natbib | ✅ | exactly this setup |
| **Data citations with persistent identifiers, in the reference list** | ✅/🔶 | Added `@misc` entries for ESS, WVS/EVS trend v4.1, LAPOP Grand Merge, V-Dem v15 (doi:10.23696/vdemds25), Claassen (doi:10.7910/DVN/HWLW0J), cited from the Data Availability Statement. 🔶 author: record the ESS per-round edition DOIs and the WVS v4.1 versioned DOI shown by the providers (bib notes mark both). |
| Statement order: Funding → Acknowledgments → Data Availability → Competing Interests → References | ✅ | `main.tex` back matter, in that order |
| Funding statement format | ✅ | "no specific grant" sentence |
| Data Availability Statement in PA's initial format (code location cited) | ✅ | now opens "Replication code for this article is available at ⟨repo⟩", Dataverse-on-acceptance line retained |
| Competing interests statement | ✅ | "The author declares none" (+ ScholarOne declaration at submission) |
| Title page: title, author, affiliation, corresponding contact, ORCID; no acknowledgments on it | ✅ | `titlepage.tex`; ORCID 0009-0007-9067-8964 |
| Single-anonymized (do NOT anonymize) | ✅ | full author block in `main.tex` and title page |
| Supplementary Material as separate PDF, not counted, published as-is | ✅ | `supplement.pdf`, S-numbered |
| Generative-AI policy: code/data-analysis use disclosed in methods; text/proof revision in Acknowledgments; figure-generating code → code disclosure only; tool, version, dates, access, scope | 🔶 | **Author writes both halves.** The Acknowledgments stub now carries a NOTE spelling out the required split and content; placeholder sentence must be replaced before submission. |
| AI not an author | ✅ | single human author |

## Submission package

| requirement | status | evidence |
|---|---|---|
| Restricted-data notification to the editor at submission | ✅ | cover letter section, mirrors PA research-transparency policy |
| Replication materials at conditional acceptance (Dataverse; Code Ocean recommended for heavy dependencies) | ⬜ | `make deposit` builds the deterministic archive (`REPLICATION.md` §5); cover letter proposes a Code Ocean capsule |
| Reproducibility verifiable by the PA team | ✅ | 101 tests incl. 32-check claim ledger; e13/e26/e50 verified bit-identical from raw files in two environments |

## Remaining author actions (the full pre-submission list)

1. Official word count on the final PDF (title page note).
2. AI disclosure, both halves (Acknowledgments note explains the split).
3. ESS per-round edition DOIs + WVS v4.1 DOI into the two dataset bib entries.
4. Cover letter: masthead check, delete the draft note.
5. Read-through of the full PDF (voice pass); confirm the title change.
