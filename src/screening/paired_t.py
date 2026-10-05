"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
from scipy.stats import t

def finish(gap,se,df,epsilon,**extra):
    if not all(math.isfinite(x) for x in [gap,se,epsilon]) or se<0:raise ValueError('Invalid t inputs')
    zero=se==0.
    statistic=None if zero else (gap-epsilon)/se
    raw=(0. if gap>epsilon else 1.) if zero else float(t.sf(statistic,df))
    return dict(estimated_gap=gap,standard_error=se,degrees_of_freedom=df,t_statistic=statistic,
        t_statistic_kind=('positive_infinity' if gap>epsilon else 'nonpositive_degenerate') if zero else 'finite',
        raw_p=raw,zero_variance=zero,epsilon=epsilon,**extra)

def paired_test(anchor,candidate,epsilon):
    a=np.asarray(anchor,dtype=float);b=np.asarray(candidate,dtype=float)
    if len(a)!=len(b) or len(a)<2:raise ValueError('Invalid paired batch')
    d=a-b;sd=0. if np.all(d==d[0]) else float(np.std(d,ddof=1))
    return finish(float(np.mean(d)),sd/math.sqrt(len(d)),len(d)-1,epsilon,
        paired_sd=sd,anchor_variance=None,candidate_variance=None,test='paired_Student_t',batch_n=len(d))

def lower_bound(record,alpha):
    radius=0. if record['zero_variance'] else float(t.isf(alpha,record['degrees_of_freedom'])*record['standard_error'])
    return record['estimated_gap']-radius,radius
