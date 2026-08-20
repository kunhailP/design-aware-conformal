\name{dapcb}
\alias{dapcb}
\alias{print.dapcb}
\title{Design-aware population conformal band (nominal-safe adaptive selector)}
\usage{
dapcb(cal_errors, v_cal, center, alpha = 0.10, tighten = TRUE,
      loo_center = TRUE)
\method{print}{dapcb}(x, ...)
}
\arguments{
\item{cal_errors}{K x T matrix of transport-error curves E_c(t) for the K
source populations over a fixed T-threshold grid.}
\item{v_cal}{K x T matrix of design-noise SDs from a stratified-PSU /
replicate-weight bootstrap; zeros for a census source.}
\item{center}{Length-T predicted curve for the new population.}
\item{alpha}{Miscoverage level (default 0.10).}
\item{tighten}{Apply the coverage-preserving isotonic tightening (default TRUE).}
\item{loo_center}{TRUE (default) declares the deployed leave-one-out
centering: the returned anchor radii (PCB, conservative) carry the K/(K-1)
inflation of the LOO-validity proposition, restoring exact finite-sample
validity for the construction as shipped; gates are evaluated on the
uninflated radii (the frozen rule). Set FALSE only for a symmetric center
(fixed, own-unit, split-fold), which is exact uninflated. The deconvolution
branch is never inflated.}
\item{x}{A \code{dapcb} object.}
\item{...}{Ignored.}
}
\value{
An object of class \code{dapcb}: a list with \code{lo}, \code{hi} (the band),
\code{selected_branch} ("PCB", "conservative", or "deconvolution"),
\code{rho_hat}, \code{rho_lcb}, \code{reliability}, \code{delta_ucb},
\code{gain_lcb}, \code{coverage_level}, \code{fallback_reason},
\code{overlap_warning}.
}
\description{
Finite-sample simultaneous conformal band for a new population's curve, with
the population as the exchangeable unit. Activates a design-noise
deconvolution only when four frozen, target-blind gates certify it is
reliable at this K; otherwise reduces to the exact clustered band (low design
noise) or a conservative envelope. Pure-R port of the reference Python
implementation, validated against it by shipped golden tests.
}
\examples{
K <- 30; T_ <- 8
E <- matrix(rnorm(K * T_, 0, 0.05), K, T_)
V <- matrix(abs(rnorm(K * T_, 0.005, 0.001)), K, T_)
center <- pmin(cumsum(abs(rnorm(T_, 0.08, 0.02))), 1)
fit <- dapcb(E, V, center, alpha = 0.10)
print(fit)
}
