"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
from .common import require_feasible,common_round_samples,use_remainder

def run(ctx,**kwargs):
    require_feasible(ctx);active=list(ctx.ids);rounds=math.ceil(math.log2(len(active)))
    for stage in range(rounds):
        before=ctx.counts();old=active.copy()
        n=common_round_samples(ctx,active,rounds-stage)
        means,_=ctx.stats(active)
        active=sorted(active,key=lambda i:(-means[i],i))[:math.ceil(len(active)/2)]
        ctx.record(stage,old,active,before,[i for i in old if i not in active],'empirical_mean_halving',equal_new_prefix_samples=n)
    use_remainder(ctx,active,rounds)
    return active[0]
