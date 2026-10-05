"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
import pandas as pd

def evaluate_selections(selections,truth,r_cal,epsilon):
    t=truth.sort_values(['mean_revenue','policy_id'],ascending=[False,True]).reset_index(drop=True)
    means=t.set_index('policy_id').mean_revenue.to_dict();best=t.iloc[0].policy_id;bestmean=float(t.iloc[0].mean_revenue)
    result=selections.copy()
    result['truth_mean_selected']=result.selected_policy.map(means)
    if result.truth_mean_selected.isna().any():raise ValueError('Selected policy absent from independent truth')
    result['truth_best_mean']=bestmean;result['regret']=bestmean-result.truth_mean_selected
    result['normalized_regret']=result.regret/r_cal;result['epsilon']=epsilon
    result['epsilon_optimal_selected']=result.regret.le(epsilon)
    result['exact_best_selected']=result.selected_policy.eq(best)
    result['top3_selected']=result.selected_policy.isin(t.head(3).policy_id)
    return result

def wilson(successes,n,z=1.959963984540054):
    p=successes/n;denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return max(0.,center-radius),min(1.,center+radius)

def summarize_metrics(rows,group_columns=('method','budget','crn')):
    output=[]
    for keys,g in rows.groupby(list(group_columns),sort=True):
        if not isinstance(keys,tuple):keys=(keys,)
        n=len(g);pgs=float(g.epsilon_optimal_selected.mean());lo,hi=wilson(int(g.epsilon_optimal_selected.sum()),n)
        output.append(dict(zip(group_columns,keys),macro_replications=n,PGS_epsilon=pgs,PGS_wilson_low=lo,PGS_wilson_high=hi,
            EOC=float(g.regret.mean()),EOC_mcse=float(g.regret.std(ddof=1)/np.sqrt(n)) if n>1 else 0.,
            normalized_EOC=float(g.normalized_regret.mean()),exact_PCS=float(g.exact_best_selected.mean()),
            top3_PCS=float(g.top3_selected.mean()),metric_status='pilot_plugin_reference_truth_not_formal_result'))
    return pd.DataFrame(output)
