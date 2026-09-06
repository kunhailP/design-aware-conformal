#!/usr/bin/env Rscript
# Convert old-vintage SPSS portable (.por) SDDF files, which pyreadstat cannot
# read, to CSV next to the originals so that pcb.data.ess_sddf can ingest them
# (docs/DATA_SOURCES.md, section 1b). Uses base R's recommended package
# `foreign`; no CRAN install needed.
#
# Usage:  Rscript scripts/convert_sddf_por.R [data/ess/sddf]
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else "data/ess/sddf"
files <- list.files(root, pattern = "\\.por$", recursive = TRUE,
                    full.names = TRUE, ignore.case = TRUE)
ok <- 0; bad <- character(0)
for (f in files) {
  out <- sub("\\.por$", ".csv", f, ignore.case = TRUE)
  if (file.exists(out)) { ok <- ok + 1; next }
  d <- tryCatch(foreign::read.spss(f, to.data.frame = TRUE,
                                   use.value.labels = FALSE),
                error = function(e) NULL)
  if (is.null(d)) { bad <- c(bad, f); next }
  write.csv(d, out, row.names = FALSE)
  ok <- ok + 1
}
cat(sprintf("converted %d of %d .por files\n", ok, length(files)))
if (length(bad)) cat("unreadable:\n", paste(" ", bad, collapse = "\n"), "\n")
