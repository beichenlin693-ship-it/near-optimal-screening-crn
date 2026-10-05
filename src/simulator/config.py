"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from pathlib import Path, PureWindowsPath
import hashlib
import json
import math
import yaml

ROOT = Path(__file__).resolve().parents[2]

def relative_path(root, value):
    p = Path(value)
    if p.is_absolute() or PureWindowsPath(value).is_absolute() or '..' in p.parts or not value:
        raise ValueError('Paths must be nonempty, project-relative and contain no traversal')
    resolved = (Path(root) / p).resolve()
    if not resolved.is_relative_to(Path(root).resolve()):
        raise ValueError('Path escapes project root')
    return resolved

def config_hash(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True, allow_nan=False).encode()).hexdigest()

def booking_weights(config):
    n = len(config['sales_windows_days_to_game'])
    kind = config['booking_curve']['type']
    if kind == 'baseline':
        return tuple(float(x) for x in config['booking_curve']['weights'])
    if kind == 'balanced':
        return (1.0/n,) * n
    raw = list(range(n, 0, -1)) if kind == 'early_heavy' else list(range(1, n+1))
    total = sum(raw)
    return tuple(x / total for x in raw)

def validate_config(c):
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    def finite(x):
        return isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)
    s = c['simulation']
    require(s['n_games_expected'] == 263, 'M3 benchmark must retain all 263 scheduled games')
    require(isinstance(s['replications'], int) and s['replications'] >= 2, 'At least two replications')
    for k in ['save_trajectory', 'deterministic']:
        require(isinstance(s[k], bool), f'{k} must be boolean')
    windows = c['sales_windows_days_to_game']
    require(len(windows) >= 1 and all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in windows), 'Invalid windows')
    require(windows[-1] == 0 and all(a > b for a,b in zip(windows,windows[1:])), 'Windows must strictly decrease to zero')
    require(c['baseline_demand']['source'] in ['rolling','frozen','dynamic'], 'Invalid baseline source')
    expected_rule = 'strictly_before_decision_date' if c['baseline_demand']['source']=='dynamic' else 'frozen_until_game_day'
    require(c['baseline_demand']['availability_rule'] == expected_rule, 'Unsafe rolling availability rule')
    require(c['booking_curve']['type'] in ['baseline','early_heavy','balanced','late_heavy'], 'Invalid booking curve')
    require(c['booking_curve']['status'] == 'structural_calibration_assumption', 'Booking curve is an assumption')
    weights = booking_weights(c)
    require(len(weights) == len(windows) and all(math.isfinite(w) and w >= 0 for w in weights) and abs(sum(weights)-1) <= 1e-12, 'Booking weights must be nonnegative and sum to one')
    e = c['elasticity']
    require(e['source'] == 'external_structural_parameter', 'Elasticity must retain structural identity')
    require(e['status'] == 'externally_calibrated_uncertain_structural_parameter', 'Invalid elasticity status')
    require(all(finite(e[k]) for k in ['baseline','min','max']) and 0 < e['min'] <= e['max'], 'Invalid elasticity range')
    require(e['min'] <= e['baseline'] <= e['max'] or (e['baseline']==0 and e['allow_zero_for_validation']), 'Elasticity must be positive within range (zero only for validation)')
    d = c['demand_shock']
    require(d['source'] == 'm2_oos_residual_pool' and d['distribution'] in ['empirical','normal','student_t'], 'Invalid shock source or distribution')
    bounds=d['factor_bounds']
    require(len(bounds)==2 and all(finite(x) for x in bounds) and 0 < bounds[0] < bounds[1], 'Invalid shock bounds')
    require(finite(d['student_t_df']) and d['student_t_df'] > 2, 'Student t requires finite variance')
    nb=c['negative_binomial']
    require(nb['alpha_source']=='m2', 'NB alpha source must be M2')
    if nb['alpha_override'] is not None:
        require(nb['override_only_for_sensitivity'] and finite(nb['alpha_override']) and nb['alpha_override']>0, 'Alpha override only for sensitivity')
    cap=c['capacity']
    if cap['status']=='public_venue_capacity':
        require(cap['source_priority']==['game_arena_date_public_capacity'], 'Invalid public capacity priority')
        require(c['baseline_demand']['source']=='dynamic', 'M3.1 requires dynamic states')
    else:
        require(cap['source_priority']==['observed_if_available','model_generated_proxy'], 'Invalid capacity priority')
        require(cap['proxy_baseline_source']=='frozen' and cap['status']=='model_generated_proxy', 'Capacity must be known at opening')
        require(finite(cap['occupancy_target']) and 0<cap['occupancy_target']<=1 and finite(cap['multiplier']) and cap['multiplier']>0, 'Invalid capacity parameters')
    p=c['pricing']
    require(all(finite(p[k]) for k in ['min_multiplier','max_multiplier']) and 0<p['min_multiplier']<=1<=p['max_multiplier'], 'Invalid price bounds')
    require(p['reference_source']=='m1_price_proxy_year' and p['reference_status']=='year_level_proxy', 'Reference price is a year-level proxy')
    for k,v in c['policies'].items():
        require(finite(v) and v >= 0, f'Invalid policy parameter {k}')
    require(c['randomness']['explicit_exogenous_path'] is True, 'Explicit exogenous paths are required')
    require(isinstance(c['randomness']['base_seed'],int) and c['randomness']['base_seed'] >= 0, 'Invalid seed')
    for v in c['paths'].values():
        relative_path(ROOT,v)
    vb=c['validation']['plausibility_season_ratio_bounds']
    require(len(vb)==2 and all(finite(x) for x in vb) and 0<vb[0]<vb[1], 'Invalid plausibility envelope')
    require(finite(c['validation']['plausibility_max_game_ratio']) and c['validation']['plausibility_max_game_ratio']>0, 'Invalid game envelope')
    require(all(finite(x) and 0<x<=1 for x in c['validation']['occupancy_scenarios']), 'Invalid capacity scenarios')
    config_hash(c)
    return c

def load_config(path='config/m3_config.yaml', root=ROOT):
    with relative_path(root,path).open(encoding='utf-8') as f:
        return validate_config(yaml.safe_load(f))
