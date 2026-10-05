"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
from .paired_t import finish

def welch_test(anchor,candidate,epsilon):
    a=np.asarray(anchor,dtype=float);b=np.asarray(candidate,dtype=float)
    if len(a)!=len(b) or len(a)<2:raise ValueError('Invalid independent batch')
    n=len(a);va=0. if np.all(a==a[0]) else float(np.var(a,ddof=1));vb=0. if np.all(b==b[0]) else float(np.var(b,ddof=1));total=va/n+vb/n
    df=(total**2/((va/n)**2/(n-1)+(vb/n)**2/(n-1))) if total>0 else None
    return finish(float(np.mean(a)-np.mean(b)),math.sqrt(total),df,epsilon,
        paired_sd=None,anchor_variance=va,candidate_variance=vb,test='Welch_Satterthwaite_approximation',batch_n=n)
