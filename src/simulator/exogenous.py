"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import norm, t as student_t

def _immutable_array(values, shape=None):
    a=np.asarray(values,dtype='<f8')
    if shape is not None and a.shape!=shape:
        raise ValueError('Exogenous array shape mismatch')
    # Bytes-backed: callers cannot simply set writeable=True to mutate a shared path.
    return np.frombuffer(a.tobytes(),dtype='<f8').reshape(a.shape)

@dataclass(frozen=True, slots=True)
class ExogenousPath:
    replication: int
    base_seed: int
    game_ids: tuple[str,...]
    windows: tuple[int,...]
    game_shock_uniform: np.ndarray
    game_shock_draw: np.ndarray
    window_uniform: np.ndarray
    shock_spec_json: str

    def __post_init__(self):
        n=len(self.game_ids)
        if len(set(self.game_ids))!=n or not n or self.replication<0:
            raise ValueError('Invalid path keys')
        for key,shape in [('game_shock_uniform',(n,)),('game_shock_draw',(n,)),('window_uniform',(n,len(self.windows)))]:
            a=_immutable_array(getattr(self,key),shape)
            if not np.isfinite(a).all():
                raise ValueError('Nonfinite exogenous path')
            if key.endswith('uniform') and not ((a>0)&(a<1)).all():
                raise ValueError('Uniforms must lie strictly inside (0,1)')
            if key=='game_shock_draw' and not (a>0).all():
                raise ValueError('Demand factors must be positive')
            object.__setattr__(self,key,a)

    def metadata(self):
        return dict(version=1,replication=self.replication,base_seed=self.base_seed,
                    game_ids=self.game_ids,windows=self.windows,shock_spec_json=self.shock_spec_json)

    @property
    def path_hash(self):
        h=hashlib.sha256(json.dumps(self.metadata(),sort_keys=True).encode())
        for a in [self.game_shock_uniform,self.game_shock_draw,self.window_uniform]:
            h.update(a.tobytes())
        return h.hexdigest()

    def save(self,filename):
        np.savez_compressed(filename,metadata=json.dumps(self.metadata(),sort_keys=True),
            game_shock_uniform=self.game_shock_uniform,game_shock_draw=self.game_shock_draw,
            window_uniform=self.window_uniform,path_hash=self.path_hash)

    @classmethod
    def load(cls,filename):
        with np.load(filename,allow_pickle=False) as z:
            m=json.loads(str(z['metadata']))
            if m.pop('version')!=1:
                raise ValueError('Unsupported exogenous path version')
            m['game_ids']=tuple(m['game_ids']); m['windows']=tuple(m['windows'])
            path=cls(**m,game_shock_uniform=z['game_shock_uniform'],game_shock_draw=z['game_shock_draw'],window_uniform=z['window_uniform'])
            if path.path_hash!=str(z['path_hash']):
                raise ValueError('Saved path hash mismatch')
        return path

def shock_spec(config,ratios):
    return json.dumps({'settings':config['demand_shock'],
        'ratio_sha256':hashlib.sha256(np.asarray(ratios,dtype='<f8').tobytes()).hexdigest()},sort_keys=True)

def transform_shock(uniform,config,ratios):
    d=config['demand_shock']
    raw=np.asarray(ratios,dtype=float)
    lo,hi=d['factor_bounds']
    u=np.asarray(uniform)
    if not d['enabled']:
        return np.ones_like(u)
    if d['distribution']=='empirical':
        support=np.clip(raw,lo,hi)
        factors=support[np.minimum((u*len(support)).astype(int),len(support)-1)]
        center=float(support.mean())
    else:
        mean=float(raw.mean()); std=float(raw.std(ddof=1))
        def quantile(q):
            if d['distribution']=='normal':
                v=norm.ppf(q,loc=mean,scale=std)
            else:
                df=d['student_t_df']
                v=student_t.ppf(q,df,loc=mean,scale=std*np.sqrt((df-2)/df))
            return np.clip(v,lo,hi)
        factors=quantile(u)
        # Fixed deterministic quadrature, never a policy- or path-dependent center.
        center=float(quantile((np.arange(16384)+0.5)/16384).mean())
    return factors/center if d['normalize_mean'] else factors

def _keyed_uniform(seed,replication,game_id,stream):
    digest=hashlib.sha256(f'M3-v1|{seed}|{replication}|{game_id}|{stream}'.encode()).digest()
    words=np.frombuffer(digest,dtype='<u4')
    rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence(words)))
    return float(np.clip(rng.random(),np.nextafter(0.,1.),np.nextafter(1.,0.)))

def generate_exogenous_path(config,games,ratios,replication):
    """No policy argument or policy inspection. Streams are keyed by game and day."""
    if not isinstance(replication,int) or replication<0:
        raise ValueError('Replication must be a nonnegative integer')
    seed=config['randomness']['base_seed']
    ids=tuple(g.game_id for g in games)
    windows=tuple(config['sales_windows_days_to_game'])
    shock_u=np.array([_keyed_uniform(seed,replication,g,'game_shock') for g in ids])
    window_u=np.array([[_keyed_uniform(seed,replication,g,f'window:{day}') for day in windows] for g in ids])
    return ExogenousPath(replication,seed,ids,windows,shock_u,transform_shock(shock_u,config,ratios),window_u,shock_spec(config,ratios))
