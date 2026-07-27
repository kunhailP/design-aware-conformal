\name{dapcb-diagnostics}
\alias{delta_ucb}
\alias{gate_b_feasible}
\alias{alpha_split}
\alias{rho_lcb}
\alias{deconv_reliability}
\alias{deconv_target_scale}
\title{Safe-selector diagnostics and frozen-budget helpers}
\usage{
delta_ucb(D)
gate_b_feasible(K)
alpha_split(K, alpha)
rho_lcb(cal_errors, v_cal, z = .Z, floor_frac = 0.05)
deconv_reliability(cal_errors, v_cal, floor_frac = 0.05)
deconv_target_scale(cal_errors, v_cal, z = .Z, floor_frac = 0.05)
}
\arguments{
\item{D}{Reliability diagnostic value.}
\item{K}{Number of calibration populations.}
\item{alpha}{Total miscoverage level.}
\item{cal_errors}{K x T matrix of transport-error curves.}
\item{v_cal}{K x T matrix of design-noise SDs.}
\item{z}{One-sided guard constant (frozen default).}
\item{floor_frac}{Scale floor fraction.}
}
\value{
\code{delta_ucb}: the frozen upper bound on the finite-K deconvolution
coverage remainder. \code{gate_b_feasible}: logical, whether the reliability
gate can open at all at this K (deterministic K >= 94 floor).
\code{alpha_split}: c(alpha_anchor, alpha_dec). \code{rho_lcb}: one-sided
lower confidence bound on the design/total SD ratio.
\code{deconv_reliability}: the diagnostic D. \code{deconv_target_scale}:
the finite-K-safe deconvolved target scale (length-T).
}
\description{
The target-blind diagnostics behind \code{\link{dapcb}}'s branch selection.
All constants are frozen in the companion replication package and are not
user-tunable.
}
