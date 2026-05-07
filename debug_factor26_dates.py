import sys
sys.path.insert(0, 'group_work/factor_lib')
from factors import read_pickle_bypass, COURSE_DATA_DIR, _ts_ir
from data_loader import load_dt
import pandas as pd

# Load close data
dt = load_dt(['close'])
print("Close date range:", dt['close'].index[0], "to", dt['close'].index[-1])
print("Close total dates:", len(dt['close']))

# Load Barra Beta
beta_path = COURSE_DATA_DIR / "barra" / "style" / "Beta.pkl"
size_path = COURSE_DATA_DIR / "barra" / "style" / "Size.pkl"

beta = read_pickle_bypass(beta_path)
size = read_pickle_bypass(size_path)

print("\nBeta date range:", beta.index[0], "to", beta.index[-1])
print("Size date range:", size.index[0], "to", size.index[-1])

# Check last valid dates
print("\n=== Last 20 dates of Beta data ===")
print("Date | Non-NaN count")
for i in range(-20, 0):
    date = beta.index[i]
    non_nan = beta.iloc[i].notna().sum()
    print(f"{date.strftime('%Y-%m-%d')} | {non_nan}")

print("\n=== Last 20 dates of Size data ===")
print("Date | Non-NaN count")
for i in range(-20, 0):
    date = size.index[i]
    non_nan = size.iloc[i].notna().sum()
    print(f"{date.strftime('%Y-%m-%d')} | {non_nan}")

# Check alignment with close
print("\n=== Close last 10 dates ===")
for i in range(-10, 0):
    date = dt['close'].index[i]
    in_beta = date in beta.index
    in_size = date in size.index
    print(f"{date.strftime('%Y-%m-%d')} | in Beta: {in_beta} | in Size: {in_size}")

# Check the actual overlap
common = beta.index.intersection(dt['close'].index)
print(f"\n=== Common dates: {len(common)} ===")
print(f"First common: {common[0]}")
print(f"Last common: {common[-1]}")
