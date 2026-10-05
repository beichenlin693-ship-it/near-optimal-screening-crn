"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
def holm(pvalues,alpha):
    if not 0<alpha<1 or any(not 0<=p<=1 for p in pvalues.values()):raise ValueError('Invalid Holm inputs')
    ordered=sorted(pvalues,key=lambda i:(pvalues[i],i));m=len(ordered);blocked=False;adjusted=0.;out={}
    for index,i in enumerate(ordered):
        factor=m-index;threshold=alpha/factor
        adjusted=min(1.,max(adjusted,factor*pvalues[i]))
        reject=not blocked and pvalues[i]<=threshold
        out[i]=dict(holm_rank=index+1,holm_threshold=threshold,holm_adjusted_p=adjusted,
            holm_reject=reject,holm_blocked_by_prior=blocked)
        if not reject:blocked=True
    return out
