"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
from .common import require_feasible,common_round_samples,use_remainder
from ..metrics.bounded_ci import difference_lcb

def run(ctx,epsilon,delta=.05,**kwargs):
    require_feasible(ctx);active=list(ctx.ids);k=len(active);rounds=math.ceil(math.log2(k))
    for stage in range(rounds):
        before=ctx.counts();old=active.copy()
        if len(active)==1:break
        n=common_round_samples(ctx,active,rounds-stage)
        evidence={};comparison_start=len(ctx.comparisons)
        for i in active:
            for j in active:
                if i==j:continue
                if ctx.crn:
                    shared=min(len(ctx.keys[j]),len(ctx.keys[i]))
                    if ctx.keys[j][:shared]!=ctx.keys[i][:shared]:raise ValueError('Cannot pair mismatched paths')
                row=difference_lcb(ctx.values[j],ctx.values[i],epsilon,delta,rounds,k,ctx.budget.budget_limit,ctx.crn)
                row.update(stage=stage,policy_i=i,dominating_policy_j=j)
                ctx.comparisons.append(row)
                if row['criterion'] and (i not in evidence or (-row['LCB'],j)<(-evidence[i]['LCB'],evidence[i]['dominating_policy_j'])):
                    evidence[i]=row
        target=math.ceil(len(active)/2);max_remove=len(active)-target
        eliminated=sorted(evidence,key=lambda i:(-evidence[i]['LCB'],i))[:max_remove]
        for i in eliminated:
            row=dict(evidence[i],elimination_valid=bool(evidence[i]['LCB']>epsilon))
            ctx.eliminations.append(row)
        active=[i for i in active if i not in eliminated]
        ctx.record(stage,old,active,before,eliminated,'confidence_safe_dominated_only',target_active_size=target,
            safe_candidates=len(evidence),equal_new_prefix_samples=n,epsilon=epsilon,
            comparison_start=comparison_start,comparison_end=len(ctx.comparisons),
            elimination_evidence=[evidence[i] for i in eliminated])
    use_remainder(ctx,active,rounds)
    return ctx.best(active)
