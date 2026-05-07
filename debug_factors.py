import sys
sys.path.insert(0, 'group_work/factor_lib')
from factors import read_pickle_bypass, COURSE_DATA_DIR
from data_loader import load_dt, load_universe_mask, make_listed_mask
import pandas as pd
import numpy as np

# Load mask
dt = load_dt(['close', 'vol'])
universe_mask = load_universe_mask(dt['close'])
listed_mask = make_listed_mask(dt['vol'])
mask = ~(universe_mask | ~listed_mask)

print("=" * 50)
print("Debug Factor 13 - Main Fund Stability")
print("=" * 50)

# Check net_mf_amount
net_mf_path = COURSE_DATA_DIR / "matrix" / "net_mf_amount.pkl"
print(f"Net MF path exists: {net_mf_path.exists()}")

if net_mf_path.exists():
    net_mf = read_pickle_bypass(net_mf_path, n_cols=1000)
    print(f"Net MF shape: {net_mf.shape}")
    print(f"Net MF index: {net_mf.index[0]} to {net_mf.index[-1]}")

    # Check alignment with close
    common_dates = net_mf.index.intersection(dt['close'].index)
    print(f"Common dates: {len(common_dates)}")

    # Check if we can assign stock codes
    idxwgt = pd.read_csv(COURSE_DATA_DIR / "idxWgt.csv", index_col=0, parse_dates=True)
    if len(net_mf.columns) == len(idxwgt.columns):
        net_mf.columns = idxwgt.columns
        common_cols = set(net_mf.columns) & set(dt['close'].columns)
        print(f"Common columns after assignment: {len(common_cols)}")

    # Align and check
    net_mf_aligned = net_mf.reindex(index=dt['close'].index, columns=dt['close'].columns)
    print(f"Net MF aligned shape: {net_mf_aligned.shape}")
    print(f"Net MF aligned non-NaN: {net_mf_aligned.notna().sum().sum()}")

    # Check if mask and net_mf have overlap
    valid_net_mf = net_mf_aligned.where(mask)
    print(f"Valid net_mf count: {valid_net_mf.notna().sum().sum()}")

print("\n" + "=" * 50)
print("Debug Factor 56 - Cashflow Price Trend")
print("=" * 50)

# Check data files
cfr_path = COURSE_DATA_DIR / "finMatrix" / "c_fr_sale_sg.pkl"
total_mv_path = COURSE_DATA_DIR / "matrix" / "total_mv.pkl"
adj_close_path = COURSE_DATA_DIR / "matrix" / "adj_close.pkl"

print(f"c_fr_sale_sg exists: {cfr_path.exists()}")
print(f"total_mv exists: {total_mv_path.exists()}")
print(f"adj_close exists: {adj_close_path.exists()}")

if cfr_path.exists():
    cfr = read_pickle_bypass(cfr_path, n_cols=1000)
    print(f"\nCFR shape: {cfr.shape}")
    print(f"CFR index: {cfr.index[0]} to {cfr.index[-1]}")

if total_mv_path.exists():
    total_mv = read_pickle_bypass(total_mv_path, n_cols=1000)
    print(f"\nTotal MV shape: {total_mv.shape}")
    print(f"Total MV index: {total_mv.index[0]} to {total_mv.index[-1]}")

if adj_close_path.exists():
    adj_close = read_pickle_bypass(adj_close_path, n_cols=1000)
    print(f"\nAdj Close shape: {adj_close.shape}")
    print(f"Adj Close index: {adj_close.index[0]} to {adj_close.index[-1]}")
