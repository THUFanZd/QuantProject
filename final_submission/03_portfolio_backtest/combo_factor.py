"""Public composite-factor interface for the final submission package."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


BACKTEST_PATH = Path(__file__).resolve().parent / "backtest.py"
SPEC = spec_from_file_location("final_submission_backtest", BACKTEST_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load portfolio implementation from {BACKTEST_PATH}")
IMPLEMENTATION = module_from_spec(SPEC)
SPEC.loader.exec_module(IMPLEMENTATION)

build_standardized_factors = IMPLEMENTATION.build_standardized_factors
build_historical_factor_weights = IMPLEMENTATION.build_historical_factor_weights
summarize_factor_weights = IMPLEMENTATION.summarize_factor_weights
combine_factor_scores = IMPLEMENTATION.combine_factor_scores
barra_neutralize = IMPLEMENTATION.barra_neutralize

__all__ = [
    "build_standardized_factors",
    "build_historical_factor_weights",
    "summarize_factor_weights",
    "combine_factor_scores",
    "barra_neutralize",
]
