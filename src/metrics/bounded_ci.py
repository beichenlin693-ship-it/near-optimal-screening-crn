"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np

def radius(values,delta,range_width):
    n=len(values)
    if not 0<delta<1 or range_width<=0:raise ValueError('Invalid confidence parameters')
    if n<2:return range_width
    variance=float(np.var(values,ddof=1))
    log=math.log(2/delta)
    return math.sqrt(2*variance*log/n)+7*range_width*log/(3*(n-1))

def difference_lcb(yj,yi,epsilon,delta,rounds,k,budget,paired):
    # Additional finite union over n handles adaptively chosen sample counts.
    if paired:
        n=min(len(yj),len(yi));z=np.asarray(yj[:n])-np.asarray(yi[:n])
        allocation=delta/(rounds*k*(k-1)*max(1,budget-1))
        rad=radius(z,allocation,2.)
        estimate=float(np.mean(z)) if n else 0.
        lcb=max(-1.,estimate-rad)
        variance=float(np.var(z,ddof=1)) if n>=2 else None
    else:
        allocation=delta/(2*rounds*k*max(1,budget-1))
        rj=radius(yj,allocation,1.);ri=radius(yi,allocation,1.)
        estimate=float(np.mean(yj)-np.mean(yi))
        lcb=max(0.,float(np.mean(yj))-rj)-min(1.,float(np.mean(yi))+ri)
        rad=rj+ri;n=0;variance=None
    return dict(paired_n=n,n_j=len(yj),n_i=len(yi),estimated_gap=estimate,LCB=lcb,
        epsilon=epsilon,confidence_radius=rad,paired_variance=variance,delta_allocated=allocation,
        confidence_type='paired_difference_EB' if paired else 'independent_arm_EB',
        criterion=bool(lcb>epsilon))
