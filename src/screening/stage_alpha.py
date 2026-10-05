"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
def stage_alpha(stage,delta=.05):
    if not isinstance(stage,int) or stage<1 or delta!=.05:raise ValueError('Fixed stage alpha specification violated')
    return delta/(stage*(stage+1))

def batch_size(remaining,active):
    if active<2 or remaining<6*active:return 0
    return remaining//active if remaining<12*active else 6
