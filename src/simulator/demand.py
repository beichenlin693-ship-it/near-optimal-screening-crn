"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import numpy as np
from scipy.stats import nbinom

def expected_demand(baseline,weight,factor,price,reference_price,elasticity):
    b,w,m,p,r=np.broadcast_arrays(*[np.asarray(x,dtype=float) for x in (baseline,weight,factor,price,reference_price)])
    if not all(np.isfinite(x).all() for x in (b,w,m,p,r)) or not np.isfinite(elasticity):
        raise ValueError('Nonfinite demand inputs')
    if (b<0).any() or (w<0).any() or (m<0).any() or (p<=0).any() or (r<=0).any() or elasticity<0:
        raise ValueError('Invalid demand inputs')
    mean=b*w*m*np.power(p/r,-elasticity)
    if not np.isfinite(mean).all():
        raise ValueError('Demand intensity overflow')
    return mean

def nb_inverse_cdf(uniform,mean,alpha):
    u,mu=np.broadcast_arrays(np.asarray(uniform,dtype=float),np.asarray(mean,dtype=float))
    if not np.isfinite(alpha) or alpha<=0 or not np.isfinite(mu).all() or (mu<0).any() or not ((u>0)&(u<1)).all():
        raise ValueError('Invalid NB2 inverse CDF inputs')
    out=np.zeros(mu.shape,dtype=np.int64)
    positive=mu>0
    values=nbinom.ppf(u[positive],1/alpha,1/(1+alpha*mu[positive]))
    if not np.isfinite(values).all() or (values<0).any() or (values>np.iinfo(np.int64).max).any():
        raise ValueError('NB2 quantile outside safe integer range')
    out[positive]=values.astype(np.int64)
    return out
