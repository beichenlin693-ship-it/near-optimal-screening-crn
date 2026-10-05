"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from collections import Counter,defaultdict

class BudgetExceeded(RuntimeError):pass

class BudgetManager:
    def __init__(self,budget_limit):
        if not isinstance(budget_limit,int) or budget_limit<0:raise ValueError('Invalid budget')
        self.budget_limit=budget_limit;self.budget_used=0
        self.calls_by_policy=Counter();self.path_ids_by_policy=defaultdict(list)
        self.duplicate_call_attempts=0;self._keys=set()
    @property
    def remaining_budget(self):return self.budget_limit-self.budget_used
    def charge(self,policy_id,path_id):
        if (policy_id,path_id) in self._keys:raise ValueError('Duplicate simulator call blocked')
        if self.remaining_budget<=0:raise BudgetExceeded('No remaining season-call budget')
        self.budget_used+=1;self.calls_by_policy[policy_id]+=1
        self.path_ids_by_policy[policy_id].append(path_id);self._keys.add((policy_id,path_id))
