"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from datetime import date,timedelta
import hashlib
import math
import numpy as np
import pandas as pd
from .config import validate_config,booking_weights,config_hash
from .state import GameState
from .demand import expected_demand,nb_inverse_cdf
from .inventory import sell
from .season import SimulationResult,summarize
from .exogenous import shock_spec

def simulate(policy,path,inputs,config,*,capture_trajectory=None,game_ids=None):
    validate_config(config)
    all_games=inputs.games
    if len(all_games)!=config['simulation']['n_games_expected']:
        raise ValueError('Full schedule must contain all 263 games')
    if path.shock_spec_json!=shock_spec(config,inputs.shock_ratios):
        raise ValueError('Path shock calibration does not match configuration/input pool')
    if tuple(g.game_id for g in all_games)!=path.game_ids or tuple(config['sales_windows_days_to_game'])!=path.windows:
        raise ValueError('Exogenous path schedule/window alignment failure')
    indices=list(range(len(all_games))) if game_ids is None else [i for i,g in enumerate(all_games) if g.game_id in game_ids]
    if not indices or (game_ids is not None and set(game_ids)!={all_games[i].game_id for i in indices}):
        raise ValueError('Requested game IDs absent from schedule')
    games=[all_games[i] for i in indices]
    capture=config['simulation']['save_trajectory'] if capture_trajectory is None else capture_trajectory
    n=len(games); windows=path.windows; weights=booking_weights(config)
    inv=np.array([g.capacity for g in games],dtype=np.int64)
    capacity=inv.copy(); cum=np.zeros(n,dtype=np.int64); prev_sales=cum.copy()
    velocity=np.zeros(n); expected_cum=np.zeros(n); revenue=np.zeros(n)
    last_price=np.array([g.reference_price for g in games]); reference=last_price.copy()
    price_history=[[] for _ in games]; sales_history=[[] for _ in games]
    rows=[]; negative=oversell=0; consumed=hashlib.sha256(); path_digest=path.path_hash
    # Canonical record of exact values actually consumed, including sold-out windows.
    for t,day in enumerate(windows):
        if config['baseline_demand']['source']=='dynamic':
            if inputs.dynamic_baselines is None:
                raise ValueError('M3.1 dynamic states are required; no silent fallback')
            baseline=np.array([inputs.dynamic_baselines[(g.game_id,day)] for g in games])
            source='dynamic'
        else:
            baseline=np.array([g.rolling_baseline if config['baseline_demand']['source']=='rolling' and day==0 else g.frozen_baseline for g in games])
            source='rolling' if config['baseline_demand']['source']=='rolling' and day==0 else 'frozen'
        states=[]
        for j,g in enumerate(games):
            states.append(GameState(g.game_id,g.game_date,g.home_team,g.away_team,t,day,
                (date.fromisoformat(g.game_date)-timedelta(days=day)).isoformat(),g.capacity,int(inv[j]),
                int(cum[j]),int(prev_sales[j]),float(velocity[j]),float(baseline[j]),source,
                float(cum[j]/max(expected_cum[j],1)) if t else 1.0,
                g.reference_price,float(last_price[j]),float(last_price[j]),g.special_event_flag,
                float(expected_cum[j]),sum(weights[:t]),windows[0],tuple(price_history[j]),tuple(sales_history[j])))
        proposed=np.array([float(policy.get_price(s)) for s in states])
        if not np.isfinite(proposed).all() or (proposed<=0).any():
            raise ValueError('Policy returned a nonfinite or nonpositive price')
        price=np.clip(proposed,reference*config['pricing']['min_multiplier'],reference*config['pricing']['max_multiplier'])
        shock=path.game_shock_draw[indices]
        uniform=path.window_uniform[indices,t]
        for j,i in enumerate(indices):
            consumed.update(f'{path.game_ids[i]}|{day}|'.encode())
            consumed.update(np.asarray([path.game_shock_uniform[i],shock[j],uniform[j]],dtype='<f8').tobytes())
        deterministic=config['simulation']['deterministic']
        factor=np.ones(n) if deterministic else shock
        intensity=expected_demand(baseline,weights[t],factor,price,reference,config['elasticity']['baseline'])
        demand=np.floor(intensity+0.5).astype(np.int64) if deterministic else nb_inverse_cdf(uniform,intensity,inputs.alpha)
        before=inv.copy()
        sales,inv=sell(inv,demand)
        negative+=int((inv<0).sum());oversell+=int((sales>before).sum())
        cum+=sales
        wr=price*sales;revenue+=wr
        duration=windows[t]-windows[t+1] if t+1<len(windows) else 1
        # Window is [game_date-day, next decision); final window is game day.
        velocity=sales/duration
        for j,g in enumerate(games):
            price_history[j].append(float(price[j]));sales_history[j].append(int(sales[j]))
            if capture:
                rows.append(dict(replication=path.replication,game_id=g.game_id,game_date=g.game_date,
                    window_index=t,days_to_game=day,decision_date=states[j].decision_date,window_duration_days=duration,
                    policy_id=policy.policy_id,baseline_demand=baseline[j],baseline_source_used=source,
                    booking_weight=weights[t],capacity=g.capacity,capacity_status=g.capacity_status,
                    inventory_before=int(before[j]),proposed_price=proposed[j],price=price[j],reference_price=reference[j],
                    price_multiplier=price[j]/reference[j],expected_demand=intensity[j],realized_demand=int(demand[j]),
                    sales=int(sales[j]),inventory_after=int(inv[j]),cumulative_sales=int(cum[j]),
                    previous_window_sales=int(prev_sales[j]),sales_velocity=float(velocity[j]),
                    policy_input_sales_velocity=states[j].sales_velocity,
                    expected_cumulative_sales_before=states[j].expected_cumulative_sales,
                    window_revenue=wr[j],cumulative_game_revenue=revenue[j],
                    game_shock_uniform=path.game_shock_uniform[indices[j]],game_shock_draw=shock[j],
                    applied_shock_factor=factor[j],window_uniform=uniform[j],path_hash=path_digest))
        expected_cum+=baseline*weights[t]
        prev_sales=sales.copy();last_price=price.copy()
    game_result=pd.DataFrame([dict(replication=path.replication,policy_id=policy.policy_id,game_id=g.game_id,
       capacity=g.capacity,tickets_sold=int(cum[j]),unsold_inventory=int(inv[j]),game_revenue=float(revenue[j]),
       sell_through_rate=float(cum[j]/g.capacity)) for j,g in enumerate(games)])
    summary=summarize(path.replication,policy.policy_id,game_result,path.path_hash,config_hash(config))
    return SimulationResult(summary,game_result,pd.DataFrame(rows),path.path_hash,consumed.hexdigest(),negative,oversell)
