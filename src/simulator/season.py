"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
from dataclasses import dataclass
import math
import pandas as pd

@dataclass
class SimulationResult:
    summary: dict
    games: pd.DataFrame
    trajectory: pd.DataFrame
    path_hash: str
    consumed_path_hash: str
    negative_inventory_count: int
    oversell_count: int

def summarize(replication,policy_id,game_results,path_hash,config_hash):
    revenue=math.fsum(game_results.game_revenue.tolist())
    sales=int(game_results.tickets_sold.sum())
    cap=int(game_results.capacity.sum())
    avg=revenue/sales if sales else 0.0
    return dict(replication=replication,policy_id=policy_id,total_revenue=revenue,
        total_sales=sales,tickets_sold=sales,average_price=avg,average_realized_price=avg,
        sell_through_rate=sales/cap,unsold_inventory=cap-sales,number_of_games=len(game_results),
        total_capacity=cap,path_hash=path_hash,config_hash=config_hash)
