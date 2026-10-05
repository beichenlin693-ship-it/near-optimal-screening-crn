"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class GameInput:
    game_id: str
    game_date: str
    home_team: str
    away_team: str
    frozen_baseline: float
    rolling_baseline: float
    capacity: int
    capacity_status: str
    capacity_provenance: str
    reference_price: float
    special_event_flag: int

@dataclass(frozen=True, slots=True)
class GameState:
    game_id: str
    game_date: str
    home_team: str
    away_team: str
    window_index: int
    days_to_game: int
    decision_date: str
    capacity: int
    remaining_inventory: int
    cumulative_sales: int
    previous_window_sales: int
    sales_velocity: float
    baseline_demand: float
    baseline_source_used: str
    rolling_demand_state: float
    reference_price: float
    current_price: float
    previous_price: float
    special_event_flag: int
    expected_cumulative_sales: float
    booking_fraction_elapsed: float
    opening_days_to_game: int
    price_history: tuple[float, ...]
    sales_history: tuple[int, ...]
