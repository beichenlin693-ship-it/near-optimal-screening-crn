"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from dataclasses import dataclass
from typing import Protocol
from .state import GameState

class PricingPolicy(Protocol):
    policy_id: str
    def get_price(self,state:GameState)->float: ...

@dataclass(frozen=True,slots=True)
class StaticReferencePolicy:
    multiplier: float=1.0
    policy_id: str='P0_static'
    def get_price(self,state):
        return state.reference_price*self.multiplier

@dataclass(frozen=True,slots=True)
class SmokePolicy:
    policy_id: str
    time_start: float
    time_end: float
    inventory_gain: float
    velocity_gain: float
    signal_limit: float

    def get_price(self,s):
        progress=1-s.days_to_game/max(s.opening_days_to_game,1)
        time=self.time_start+(self.time_end-self.time_start)*progress
        # All signals are computed from history at the start of this window.
        target=min(s.capacity,s.expected_cumulative_sales)
        inventory_signal=(s.cumulative_sales-target)/s.capacity
        velocity_signal=(s.cumulative_sales-target)/max(target,0.10*s.capacity)
        velocity_signal=max(-self.signal_limit,min(self.signal_limit,velocity_signal))
        inv=1+self.inventory_gain*inventory_signal
        vel=1+self.velocity_gain*velocity_signal
        if self.policy_id=='P1_time':
            multiplier=time
        elif self.policy_id=='P2_inventory':
            multiplier=inv
        elif self.policy_id=='P3_velocity':
            multiplier=vel
        elif self.policy_id=='P4_hybrid':
            multiplier=time*inv*vel
        else:
            raise ValueError('Unknown smoke policy')
        return s.reference_price*max(multiplier,0.01)

def smoke_policies(config):
    p=config['policies']
    return [StaticReferencePolicy()]+[SmokePolicy(name,p['time_start_multiplier'],p['time_end_multiplier'],p['inventory_gain'],p['velocity_gain'],p['velocity_signal_limit'])
        for name in ['P1_time','P2_inventory','P3_velocity','P4_hybrid']]
