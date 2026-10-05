"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from dataclasses import dataclass
import hashlib,json
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Policy:
    policy_id:str
    family:str
    parameters:tuple
    description:str
    min_multiplier:float=.65
    max_multiplier:float=1.65
    def get_price(self,s):
        p=dict(self.parameters)
        progress=1-s.days_to_game/max(s.opening_days_to_game,1)
        q=s.remaining_inventory/s.capacity
        v=max(-1.,min(1.,(s.cumulative_sales-s.expected_cumulative_sales)/max(s.expected_cumulative_sales,1.)))
        if self.family=='Static':m=p['multiplier']
        elif self.family=='Time-based':
            x=max(0.,(progress-p['start_progress'])/(1-p['start_progress']))
            m=p['start']+(p['end']-p['start'])*x**p['power']
        elif self.family=='Inventory-based':
            gap=(1-p['target_sellthrough']*progress)-q
            m=p['base']+p['scarcity_gain']*max(gap,0)-p['clearance_gain']*max(-gap,0)
        elif self.family=='Sales-velocity':m=1+p['sensitivity']*v
        elif self.family=='Hybrid':
            m=p['base']+p['time_gain']*(2*progress-1)+p['inventory_gain']*(1-p['target_sellthrough']*progress-q)+p['velocity_gain']*v
        else:raise ValueError('Unknown policy family')
        return s.reference_price*max(.01,m)

def policies():
    result=[]
    def add(pid,family,params,description):result.append(Policy(pid,family,tuple(sorted(params.items())),description))
    for label,m in [('085',.85),('100',1.),('115',1.15),('130',1.3)]:
        add('STATIC_'+label,'Static',dict(multiplier=m),'Constant reference-price multiplier')
    for pid,start,end,power,delay in [
        ('EARLY_DISCOUNT',.70,1.05,1.,0.),('MILD_INCREASE',.95,1.10,1.,0.),
        ('MODERATE_INCREASE',.85,1.30,1.,0.),('LATE_SURGE',.90,1.55,3.,0.),
        ('FLAT_THEN_SURGE',1.,1.50,1.,.75),('HIGH_EARLY_NORMALIZE',1.35,.95,1.,0.)]:
        add('TIME_'+pid,'Time-based',dict(start=start,end=end,power=power,start_progress=delay),'Deterministic time profile with ex-ante shape')
    for i,params in enumerate([(.90,1.2,.15,1.),(.90,.7,.15,1.),(.90,.3,.10,1.),
        (.90,.15,1.2,1.),(.90,.15,.7,1.),(.75,.6,.6,1.05),(.98,.6,.6,1.),(.85,.9,.9,.95)],1):
        target,scarcity,clearance,base=params
        add(f'INV_{i:02d}','Inventory-based',dict(target_sellthrough=target,scarcity_gain=scarcity,clearance_gain=clearance,base=base),
            'Remaining-inventory feedback around ex-ante target sell-through trajectory')
    for i,gain in enumerate([.05,.10,.20,.35,.50,.80],1):
        add(f'VEL_{i:02d}','Sales-velocity',dict(sensitivity=gain),'Price responds to bounded cumulative-sales / expected-sales gap')
    for i,p in enumerate([(.10,.25,.10,.90,1.),(.20,.40,.15,.90,1.),(.30,.60,.20,.90,1.),
        (.10,.80,.35,.85,1.),(-.15,.45,.25,.90,1.10),(.20,.20,.60,.95,1.),
        (.05,.50,.50,.75,.95),(.25,.75,.40,.98,1.05)],1):
        a,b,c,target,base=p
        add(f'HYB_{i:02d}','Hybrid',dict(time_gain=a,inventory_gain=b,velocity_gain=c,target_sellthrough=target,base=base),
            'Additive time, remaining-inventory and cumulative-sales feedback')
    return tuple(sorted(result,key=lambda p:p.policy_id))

def registry():
    return pd.DataFrame([dict(policy_id=p.policy_id,family=p.family,parameters=json.dumps(dict(p.parameters),sort_keys=True,separators=(',',':')),
        description=p.description,min_multiplier=p.min_multiplier,max_multiplier=p.max_multiplier) for p in policies()])

