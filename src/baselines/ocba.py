"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
from .common import require_feasible

def allocation_weights(means,variances,gap_floor,variance_floor):
    ids=sorted(means);best=sorted(ids,key=lambda i:(-means[i],i))[0]
    var={i:max(variances[i],variance_floor) for i in ids}
    weights={i:var[i]/max(means[best]-means[i],gap_floor)**2 for i in ids if i!=best}
    weights[best]=math.sqrt(var[best]*sum(weights[i]**2/var[i] for i in ids if i!=best))
    total=sum(weights.values())
    return best,{i:weights[i]/total for i in ids}

def allocation_targets(counts,weights,total):
    """Classical lower-bound correction: freeze overallocated arms, then apportion."""
    ids=sorted(counts);fixed={};free=set(ids)
    while free:
        available=total-sum(fixed.values());denom=sum(weights[i] for i in free)
        candidate={i:available*weights[i]/denom for i in free}
        over=[i for i in free if candidate[i]<counts[i]]
        if not over:break
        for i in over:fixed[i]=float(counts[i]);free.remove(i)
    continuous={**fixed,**candidate} if free else fixed
    # candidate may retain previously fixed entries only on the last loop exit.
    continuous.update(fixed)
    ints={i:max(counts[i],int(math.floor(continuous[i]))) for i in ids}
    residual=total-sum(ints.values())
    order=sorted(ids,key=lambda i:(-(continuous[i]-ints[i]),i))
    if not 0<=residual<=len(ids):raise ValueError('OCBA target apportionment error')
    for i in order[:residual]:ints[i]+=1
    return continuous,ints

def run(ctx,n0=5,gap_floor=1e-6,variance_floor=1e-12,batch_size=32,**kwargs):
    if n0!=5:raise ValueError('OCBA initialization is fixed at five')
    require_feasible(ctx,n0);before=ctx.counts()
    for _ in range(n0):
        for i in ctx.ids:ctx.sample(i)
    ctx.record(0,ctx.ids,ctx.ids,before,reason='OCBA_n0_5')
    stage=1
    while ctx.budget.remaining_budget:
        before=ctx.counts();means,variances=ctx.stats()
        best,weights=allocation_weights(means,variances,gap_floor,variance_floor)
        target_total=ctx.budget.budget_used+min(batch_size,ctx.budget.remaining_budget)
        continuous,targets=allocation_targets(before,weights,target_total)
        for i in ctx.ids:
            for _ in range(targets[i]-before[i]):ctx.sample(i)
        ctx.record(stage,ctx.ids,ctx.ids,before,reason='classic_OCBA_ratio_no_covariance',
            empirical_best=best,allocation_ratio=weights,allocation_target=continuous,integer_target=targets,actual_allocation=ctx.counts())
        stage+=1
    return ctx.best(ctx.ids)
