"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
from .common import require_feasible,use_remainder

def standard_schedule(budget,k):
    logbar=.5+sum(1/i for i in range(2,k+1))
    return [math.ceil((budget-k)/(logbar*(k+1-stage))) for stage in range(1,k)]

def run(ctx,**kwargs):
    require_feasible(ctx);active=list(ctx.ids);k=len(active)
    for stage,target in enumerate(standard_schedule(ctx.budget.budget_limit,k),1):
        before=ctx.counts();old=active.copy();current=len(ctx.values[active[0]])
        requested=max(1,target) # B=K boundary: initialize exactly one sample per arm.
        add=min(max(0,requested-current),ctx.budget.remaining_budget//len(active))
        for _ in range(add):
            for i in sorted(active):ctx.sample(i)
        means,_=ctx.stats(active)
        # Reverse ID tie-break for rejection preserves lowest-ID winner.
        rejected=sorted(active,key=lambda i:(-means[i],i))[-1]
        active=[i for i in active if i!=rejected]
        ctx.record(stage,old,active,before,[rejected],'one_empirical_worst_rejection',
            classic_target_n=target,corrected_target_n=current+add,deterministic_correction=bool(current+add!=target))
    use_remainder(ctx,active,k)
    return active[0]
