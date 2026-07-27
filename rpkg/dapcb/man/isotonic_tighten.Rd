\name{isotonic_tighten}
\alias{isotonic_tighten}
\title{Coverage-preserving isotonic tightening of a CDF band}
\usage{isotonic_tighten(lo, hi)}
\arguments{
\item{lo}{Numeric vector of lower band limits.}
\item{hi}{Numeric vector of upper band limits.}
}
\value{list with tightened \code{lo} and \code{hi}.}
\description{
The truth is a nondecreasing [0,1] function, so the lower bound may be raised
to its running maximum and the upper bound lowered to its running minimum from
the right without losing coverage.
}
