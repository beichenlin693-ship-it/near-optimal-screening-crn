"""Explicit simulator input container; no raw-data loading or simulation on import.
Inputs: legally acquired game metadata and prespecified derived parameters.
Outputs: Inputs instance. Runtime: negligible. See data/README.md for excluded data.
"""
from dataclasses import dataclass
import pandas as pd
from .state import GameInput

@dataclass(frozen=True)
class Inputs:
    games: tuple[GameInput, ...]
    alpha: float
    m2_alpha: float
    shock_ratios: tuple[float, ...]
    residual_audit: pd.DataFrame
    shock_fit: pd.DataFrame
    provenance: pd.DataFrame
    dynamic_baselines: object = None
