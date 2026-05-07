"""Data loading helpers for local matrix-style factor research."""

from __future__ import annotations

import json
import pickletools
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_project_config() -> dict:
    config_path = PROJECT_ROOT / "data" / "config.json"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def read_pickle_bypass(path: Path) -> pd.DataFrame:
    """Read pickle file bypassing version compatibility issues."""
    blobs: list[bytes] = []
    for op, arg, _ in pickletools.genops(path.read_bytes()):
        if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
            blobs.append(bytes(arg))

    if len(blobs) == 0:
        raise ValueError(f"Cannot find numeric payloads in {path}")

    # Check if this is Barra style (2 blobs: values + dates)
    # Values blob is large, dates blob is smaller
    if len(blobs) >= 2 and len(blobs[1]) < len(blobs[0]) // 100:
        values_blob, dates_blob = blobs[0], blobs[1]
        n_dates = len(dates_blob) // 8
        values = np.frombuffer(values_blob, dtype="<f8").reshape(n_dates, -1)
        date_us = np.frombuffer(dates_blob, dtype="<i8")
        dates = pd.to_datetime(date_us, unit="us")
        return pd.DataFrame(values, index=dates)

    # Filter for large blobs (>100KB) for other formats
    large_blobs = [b for b in blobs if len(b) > 100000]

    if len(large_blobs) == 1:
        # Single combined blob (like net_mf_amount)
        values_blob = large_blobs[0]
        total_values = len(values_blob) // 8
        n_cols = 1000
        n_dates = total_values // n_cols
        values = np.frombuffer(values_blob, dtype="<f8").reshape(n_dates, n_cols)
        dates = pd.date_range(start="2010-01-04", periods=n_dates, freq="B")
        return pd.DataFrame(values, index=dates)

    # Multiple small blobs (one per stock, like close.pkl)
    from collections import Counter
    blob_sizes = [len(b) for b in blobs if len(b) > 1000]
    if not blob_sizes:
        raise ValueError(f"Cannot parse pickle format in {path}")
    size_counts = Counter(blob_sizes)
    common_size = size_counts.most_common(1)[0][0]
    stock_blobs = [b for b in blobs if len(b) == common_size]
    n_dates = common_size // 8
    values = np.column_stack([np.frombuffer(b, dtype="<f8") for b in stock_blobs])
    dates = pd.date_range(start="2010-01-04", periods=n_dates, freq="B")

    return pd.DataFrame(values, index=dates)


def resolve_data_root() -> Path:
    """Find the data root directory."""

    # Check for stock1000 data in various locations
    local_candidates = [
        PROJECT_ROOT / "data" / "stock1000_px",
        PROJECT_ROOT / "data_1800" / "stock1000" / "data",
        PROJECT_ROOT / "data" / "stock1800_px",
    ]
    for candidate in local_candidates:
        if (candidate / "matrix").exists():
            return candidate

    raise FileNotFoundError("Could not find a data root with a matrix folder.")


def load_dt(fields: list[str], data_root: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load selected matrix fields into the `dt` dictionary format."""

    root = data_root or resolve_data_root()
    matrix_dir = root / "matrix"
    dt: dict[str, pd.DataFrame] = {}

    # Load stock codes from idxWgt for column alignment
    idxwgt_csv = root / "idxWgt.csv"
    stock_codes = None
    if idxwgt_csv.exists():
        idxwgt = pd.read_csv(idxwgt_csv, index_col=0, parse_dates=True)
        stock_codes = idxwgt.columns.tolist()

    for field in fields:
        path = matrix_dir / f"{field}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Missing matrix field {field!r}: {path}")
        try:
            frame = pd.read_pickle(path)
            frame.index = pd.to_datetime(frame.index)
        except Exception:
            # Fall back to bypass method for version compatibility
            frame = read_pickle_bypass(path)
        frame = frame.sort_index()

        # Assign stock codes as column names if available
        if stock_codes is not None and len(frame.columns) == len(stock_codes):
            frame.columns = stock_codes

        dt[field] = frame

    base = dt[fields[0]]
    for field in fields[1:]:
        dt[field] = dt[field].reindex(index=base.index, columns=base.columns)
    return dt


def load_universe_mask(like: pd.DataFrame, data_root: Path | None = None) -> pd.DataFrame:
    """Return True for stocks that should be excluded from calculation."""

    root = data_root or resolve_data_root()

    # Try CSV first (more compatible)
    idxwgt_csv = root / "idxWgt.csv"
    idxwgt_pkl = root / "idxWgt.pkl"

    if idxwgt_csv.exists():
        idxwgt = pd.read_csv(idxwgt_csv, index_col=0, parse_dates=True)
    elif idxwgt_pkl.exists():
        try:
            idxwgt = pd.read_pickle(idxwgt_pkl)
            idxwgt.index = pd.to_datetime(idxwgt.index)
        except Exception:
            return pd.DataFrame(False, index=like.index, columns=like.columns)
    else:
        return pd.DataFrame(False, index=like.index, columns=like.columns)

    idxwgt = idxwgt.reindex(index=like.index, columns=like.columns)
    return idxwgt == 0


def make_listed_mask(vol: pd.DataFrame, listed_days: int = 20) -> pd.DataFrame:
    listed = vol.fillna(0).cumsum() > 0
    return listed.shift(listed_days, fill_value=False).astype(bool)
