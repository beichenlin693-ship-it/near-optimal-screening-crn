"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
from .budget import BudgetManager
from .cache import EvaluationCache

class RunContext:
    def __init__(self,ids,budget,crn,key,evaluate,config_hash='toy',scale=1.):
        self.ids=tuple(sorted(ids));self.crn=bool(crn);self.budget=BudgetManager(budget)
        self.cache=EvaluationCache();self.values={i:[] for i in self.ids};self.keys={i:[] for i in self.ids}
        self._key=key;self._evaluate=evaluate;self.config_hash=config_hash;self.scale=scale
        self.trace=[];self.comparisons=[];self.eliminations=[]
    def sample(self,policy_id):
        index=len(self.values[policy_id])+1;path=self._key(policy_id,index)
        value=self.cache.evaluate(policy_id,path,self.config_hash,self.budget,lambda:self._evaluate(policy_id,path))/self.scale
        if not 0<=value<=1+1e-12:raise ValueError('Normalized reward outside [0,1]')
        self.values[policy_id].append(value);self.keys[policy_id].append(path)
        return value
    def stats(self,active=None):
        active=self.ids if active is None else active
        means={i:float(np.mean(self.values[i])) if self.values[i] else None for i in active}
        variances={i:float(np.var(self.values[i],ddof=1)) if len(self.values[i])>=2 else None for i in active}
        return means,variances
    def best(self,active):
        means,_=self.stats(active)
        return sorted(active,key=lambda i:(-means[i],i))[0]
    def record(self,stage,before,after,counts_before,eliminated=(),reason='none',**extra):
        means,variances=self.stats(before)
        row=dict(stage=stage,active_set_before=list(before),new_evaluations={i:len(self.values[i])-counts_before.get(i,0) for i in self.ids},
            cumulative_evaluations={i:len(self.values[i]) for i in self.ids},sample_means=means,variances=variances,
            eliminated_policies=list(eliminated),elimination_reason=reason,active_set_after=list(after),budget_used=self.budget.budget_used,
            observations_scale='normalized_by_deterministic_revenue_upper_bound',**extra)
        self.trace.append(row)
    def counts(self):return {i:len(self.values[i]) for i in self.ids}

def require_feasible(ctx,n0=1):
    if len(ctx.ids)<2 or ctx.budget.budget_limit<n0*len(ctx.ids):raise ValueError('Infeasible budget for algorithm initialization')

def common_round_samples(ctx,active,remaining_rounds):
    """Equal new prefix lengths; defer indivisible remainder instead of overspending."""
    target=ctx.budget.remaining_budget//remaining_rounds
    n=target//len(active)
    if n==0 and ctx.budget.remaining_budget>=len(active):n=1
    for _ in range(n):
        for i in sorted(active):ctx.sample(i)
    return n

def use_remainder(ctx,active,stage):
    if not ctx.budget.remaining_budget:return
    before=ctx.counts()
    for t in range(ctx.budget.remaining_budget):ctx.sample(sorted(active)[t%len(active)])
    ctx.record(stage,active,active,before,reason='terminal_remainder_no_elimination')
