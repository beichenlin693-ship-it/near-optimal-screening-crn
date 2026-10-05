"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from .common import require_feasible

def run(ctx,**kwargs):
    require_feasible(ctx);before=ctx.counts()
    n,remainder=divmod(ctx.budget.budget_limit,len(ctx.ids))
    for rank,i in enumerate(ctx.ids):
        for _ in range(n+int(rank<remainder)):ctx.sample(i)
    ctx.record(0,ctx.ids,ctx.ids,before,reason='uniform_allocation')
    return ctx.best(ctx.ids)
