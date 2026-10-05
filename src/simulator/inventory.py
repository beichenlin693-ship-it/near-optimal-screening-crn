"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import numpy as np

def sell(inventory,demand):
    inv,d=np.broadcast_arrays(np.asarray(inventory),np.asarray(demand))
    if not np.isfinite(inv).all() or not np.isfinite(d).all() or (inv<0).any() or (d<0).any() or (inv!=np.floor(inv)).any() or (d!=np.floor(d)).any():
        raise ValueError('Inventory and demand must be nonnegative integer counts')
    sales=np.minimum(inv,d).astype(np.int64)
    return sales,inv.astype(np.int64)-sales
