# Cover letter — Political Analysis submission

*Draft. The author should check the salutation against the current masthead
before sending, add the AI-use sentence agreed for the Acknowledgments, and
delete this note.*

---

Professor Daniel Hopkins
Professor Brandon Stewart
Editors-in-Chief, *Political Analysis*

Dear Editors,

I am submitting **"The Wrong Unit of Uncertainty: Simultaneous Inference for
Repeated Cross-National Surveys"** for consideration as a Research Article.

**What the paper does.** Claims about repeated cross-national surveys routinely
attach uncertainty to the wrong unit, and to two different wrong units at once.
A single wave-pair contrast is read as a persistent, distribution-wide trend;
and the objects a conformal band calibrates on — other countries' attitude
distributions — are themselves complex-survey *estimates*, plugged in as if they
were truth. The paper gives a finite-sample simultaneous band over a country's
whole trajectory, with the country as the exchangeable unit, and an ordered
hierarchy of claims read off one band at one level. It then draws the scope
boundary for the second error: without the design-noise law the correction is
non-identified, and with it the correction remains unreachable at cross-national
scale, because the reliability diagnostic obeys an algorithmic floor requiring
at least 94 exchangeable populations. One unit down, on regions within the same
survey, the frozen procedure does activate.

Substantively, the hierarchy cuts a marginal reading of twenty of thirty
European countries to net decline in six; over 2002–2024 no country certifies a
persistent slide, twenty-three of thirty-three certify both declines and
recoveries, and span erosion certifies in eight. On the World Values Survey the
same shift of rung cuts the certified set several-fold, and what survives
concentrates in post-communist and Arab-Spring states rather than in the
consolidated democracies the deconsolidation thesis concerned.

**Relation to a companion manuscript.** The clustered population-conformal band
(the manuscript's Theorem 3) is base machinery shared with a companion paper of
mine that applies it in a non-survey domain, cited in the manuscript as
Park (2026); the manuscript says so where the band is introduced. Everything
the survey layer forces is new to this paper and appears in no other
manuscript: the curve-level non-identification theorem for estimated
calibration objects (Theorem 1), the finite-$K$ reliability floor and
survey-scale unreachability result (Proposition 1), the safe-adaptive selector
and its validity theorem (Theorem 5), the partially ordered claim family read
off one band, and both reanalyses. There is no textual overlap beyond the
shared base construction, which both papers disclose.

**Notification of restricted data access.** In line with the journal's
replication guidelines, which ask that the editor be notified at the time of
submission where access to the data is restricted or limited, I note that all
three microdata sources are licensed and cannot be redistributed:

- the European Social Survey integrated file, rounds 1–11 (free registration,
  ESS End User Licence);
- the World Values Survey / EVS joint trend file 1981–2022 (registration and a
  purpose statement required under the WVSA/EVS terms);
- the AmericasBarometer / LAPOP Grand Merge 2004–2023 (free after registration).

The restriction is on redistribution, not on access: each file is available to
any reader who registers with its provider, at no cost. The replication package
is built around this. All code is public, including every script that runs on
the restricted files, so that a reader holding the same three files reproduces
the results without modification. The package separates the analysis into a tier
that needs no microdata — the simulations, the theory contract tests, and the
sealed validation runs — and a tier that does, with exact file names, variable
lists, retrieval steps and sha256 checksums documented for each source. Two
results (the ESS certification counts and the WVS hierarchy) have been verified
to reproduce bit-identically from the raw files.

Given the dependency footprint — Python and R, a compiled survey-data reader,
and several long-running bootstrap experiments — I intend to prepare the
replication archive as a Code Ocean capsule, as the guidelines recommend for
archives with extensive dependencies.

**Other declarations.** The manuscript is not under consideration elsewhere. The
Supplementary Material is submitted as
a separate PDF and contains the proofs, the extended robustness analyses, and
two documented withdrawals: a result that an earlier draft reported and that our
own follow-up experiment refuted, and an artifact we diagnosed and report as
such. I declare no competing interests, and the research received no specific
grant.

Thank you for considering the manuscript.

Sincerely,

Kunwoo Park
Department of Politics, Kookmin University
Seoul, Republic of Korea
pkw31386094@gmail.com · ORCID 0009-0007-9067-8964
