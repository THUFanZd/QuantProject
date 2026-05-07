"""Data loading helpers for local matrix-style factor research."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_project_config() -> dict:
    config_path = PROJECT_ROOT / "data" / "config.json"
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_data_root() -> Path:
    """Prefer portable project data, then fall back to configured paths."""

    local_candidates = [
        PROJECT_ROOT / "data" / "stock1000_px",
        PROJECT_ROOT / "data" / "stock1800_px",
    ]
    for candidate in local_candidates:
        if (candidate / "matrix").exists():
            return candidate

    config = read_project_config()
    paths = config.get("paths", {})
    for key in ("S1000", "S1800"):
        value = paths.get(key)
        if not value:
            continue
        candidate = Path(value)
        if (candidate / "matrix").exists():
            return candidate

    raise FileNotFoundError("Could not find a data root with a matrix folder.")


def load_dt(fields: list[str], data_root: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load selected matrix fields into the `dt` dictionary format."""

    root = data_root or resolve_data_root()
    matrix_dir = root / "matrix"
    dt: dict[str, pd.DataFrame] = {}

    for field in fields:
        path = matrix_dir / f"{field}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Missing matrix field {field!r}: {path}")
        frame = pd.read_pickle(path)
        frame.index = pd.to_datetime(frame.index)
        dt[field] = frame.sort_index()

    base = dt[fields[0]]
    for field in fields[1:]:
        dt[field] = dt[field].reindex(index=base.index, columns=base.columns)
    return dt


def load_universe_mask(like: pd.DataFrame, data_root: Path | None = None) -> pd.DataFrame:
    """Return True for stocks that should be excluded from calculation."""

    root = data_root or resolve_data_root()
    idxwgt_path = root / "idxWgt.pkl"
    if not idxwgt_path.exists():
        return pd.DataFrame(False, index=like.index, columns=like.columns)

    idxwgt = pd.read_pickle(idxwgt_path)
    idxwgt.index = pd.to_datetime(idxwgt.index)
    idxwgt = idxwgt.reindex(index=like.index, columns=like.columns)
    return idxwgt == 0


def make_listed_mask(vol: pd.DataFrame, listed_days: int = 20) -> pd.DataFrame:
    listed = vol.fillna(0).cumsum() > 0
    return listed.shift(listed_days, fill_value=False).astype(bool)
