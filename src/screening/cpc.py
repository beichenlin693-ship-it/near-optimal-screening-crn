"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
from .stage_alpha import stage_alpha,batch_size
from .paired_t import paired_test,lower_bound
from .welch_t import welch_test
from .holm import holm
from ..baselines.common import require_feasible,use_remainder

VERSION='epsilon_cpc_sh_v2_stage_local'

def run(ctx,epsilon,delta=.05):
    require_feasible(ctx,2)
    if delta!=.05:raise ValueError('Delta is frozen at .05')
    active=list(ctx.ids);before=ctx.counts()
    for _ in range(2):
        for i in active:ctx.sample(i)
    ctx.record(0,active,active,before,reason='warmup_anchor_only',phase='warmup',
        batch_paths={i:ctx.keys[i][:] for i in active},certification_uses_warmup=False)
    stage=1
    while len(active)>1:
        n=batch_size(ctx.budget.remaining_budget,len(active))
        if n==0:break
        old=active.copy();counts=ctx.counts();past_means,_=ctx.stats(active)
        anchor=ctx.best(active)  # Locked before requesting ANY fresh sample.
        anchor_order=ctx.budget.budget_used;start_counts={i:len(ctx.values[i]) for i in active}
        alpha=stage_alpha(stage,delta)
        for _ in range(n):
            for i in active:ctx.sample(i)
        fresh={i:ctx.values[i][start_counts[i]:] for i in active}
        paths={i:ctx.keys[i][start_counts[i]:] for i in active}
        if ctx.crn and any(paths[i]!=paths[anchor] for i in active):raise ValueError('Stage paired path mismatch')
        stats={i:(paired_test if ctx.crn else welch_test)(fresh[anchor],fresh[i],epsilon) for i in active if i!=anchor}
        correction=holm({i:r['raw_p'] for i,r in stats.items()},alpha)
        evidence=[]
        for i,record in stats.items():
            record.update(correction[i]);lcb,radius=lower_bound(record,record['holm_threshold'])
            # A later Holm-blocked hypothesis may pass its local threshold; that
            # is not a step-down rejection. A rejected hypothesis must be strict.
            if record['holm_reject'] and not lcb>epsilon:raise ValueError('Holm rejection / strict LCB numerical inconsistency')
            local_pass=record['raw_p']<=record['holm_threshold']
            if local_pass!=(lcb>epsilon):raise ValueError('t p-value / LCB numerical inconsistency')
            record.update(stage=stage,anchor=anchor,candidate=i,LCB=lcb,confidence_radius=radius,
                alpha_stage=alpha,safe_certificate=bool(record['holm_reject'] and lcb>epsilon),
                safe_elimination=False,anchor_order=anchor_order,first_fresh_order=anchor_order+1,
                anchor_start_n=start_counts[anchor],candidate_start_n=start_counts[i],
                anchor_path_ids=paths[anchor],candidate_path_ids=paths[i])
            evidence.append(record)
        safe=[r for r in evidence if r['safe_certificate']]
        safe.sort(key=lambda r:(r['holm_adjusted_p'],-(r['LCB']-epsilon),-r['estimated_gap'],r['candidate']))
        removed={r['candidate'] for r in safe[:len(active)//2]}
        for r in evidence:
            r['safe_elimination']=r['candidate'] in removed
            ctx.comparisons.append(r)
            if r['safe_elimination']:ctx.eliminations.append(dict(r))
        active=[i for i in active if i not in removed]
        ctx.record(stage,old,active,counts,sorted(removed),'fresh_Holm_certificates_only',phase='confidence',
            anchor=anchor,anchor_history_means=past_means,anchor_order=anchor_order,first_fresh_order=anchor_order+1,
            alpha_stage=alpha,batch_n=n,batch_paths=paths,start_counts=start_counts,
            safe_certificates=len(safe),elimination_cap=len(old)//2,certification_uses_warmup=False)
        stage+=1
    use_remainder(ctx,active,stage)
    return ctx.best(active)
