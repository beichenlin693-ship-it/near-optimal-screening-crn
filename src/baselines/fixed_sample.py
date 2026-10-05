"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import numpy as np
from scipy.stats import t

CATEGORIES={
    'DSTTB-setwise-2023':'PUBLISHED',
    'B1-Bonferroni-box-epsilon':'EXTERNAL-FRAMEWORK INSTANTIATION',
    'B2-paired-Bonferroni-epsilon':'STANDARDIZED ADAPTATION',
    'epsilon-CPC-SH':'FROZEN PROPOSED METHOD',
    'Uniform-no-screening':'DESCRIPTIVE NO-SCREENING REFERENCE'}

def screen(x,epsilon,method,alpha=.05):
    x=np.asarray(x,dtype=float)
    n,k=x.shape
    assert n>=2 and k>=2 and np.isfinite(x).all() and epsilon>=0
    means=x.mean(axis=0)
    if method in ['DSTTB-setwise-2023','B1-Bonferroni-box-epsilon']:
        beta=(1+(1-alpha)**(1/k))/2 if method=='DSTTB-setwise-2023' else 1-alpha/(2*k)
        c=t.ppf(beta,n-1)
        radius=c*x.std(axis=0,ddof=1)/np.sqrt(n)
        lower=means-radius;upper=means+radius
        # Reject strictly; equality retains the boundary candidate.
        keep=upper+epsilon>=lower.max()
        detail=dict(critical_quantile=float(beta),critical_t=float(c),df=n-1,
                    means=means.tolist(),lower=lower.tolist(),upper=upper.tolist(),benchmark=float(lower.max()))
    elif method=='B2-paired-Bonferroni-epsilon':
        beta=1-alpha/(k*(k-1));c=t.ppf(beta,n-1)
        differences=x[:,None,:]-x[:,:,None]  # [rep, candidate i, rival j] = Y_j-Y_i
        lower=differences.mean(axis=0)-c*differences.std(axis=0,ddof=1)/np.sqrt(n)
        np.fill_diagonal(lower,-np.inf)
        max_lower=lower.max(axis=1)
        keep=max_lower<=epsilon
        detail=dict(critical_quantile=float(beta),critical_t=float(c),df=n-1,
                    means=means.tolist(),max_gap_lower_bound=max_lower.tolist())
    else:raise ValueError(method)
    assert keep.any() and keep[int(np.argmax(means))]
    return keep,detail
