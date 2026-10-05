# Direct external screening comparison

The published set-wise DSTTB rule follows Zhao, Gatica and Eckman,
[Screening Simulated Systems for Optimization (2023)](https://www.informs-sim.org/wsc23papers/001.pdf).
Its independence-calibrated marginal intervals motivate CRN OFF use. B1 uses
Bonferroni marginal boxes to retain validity under dependence given marginal
coverage. B2 is the study's standardized all-directed-pair Bonferroni adaptation;
it is not an original published DSTTB algorithm.

The implementation is `src/baselines/fixed_sample.py`. Inputs are n-by-K stored
observation matrices and an epsilon threshold; it generates no observations.
The prespecified comparison uses K=32, B=512, n=16, alpha=0.05, 1,000 Gaussian
selections and 200 WNBA selections per applicable cell. The selected prefix is
not an additional independent experiment.

CPC and the external procedures use independent algorithm banks. B1 and B2
share their fixed-sample bank. No algorithm-level paired difference test was
used. Recommendation from a retained set is a separate standardized extension
(largest survivor sample mean, ties lowest ID); it is not a native selection
guarantee of DSTTB or the adaptations.

Uncertainty intervals are copied from stored outputs. Unknown removed-policy
identities in two Gaussian CPC failures remain bounded rather than imputed.
The study covers one external budget and supports no universal dominance claim.
