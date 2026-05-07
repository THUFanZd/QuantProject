import sys
sys.path.insert(0, 'group_work/factor_lib')
from factors import read_pickle_bypass, COURSE_DATA_DIR, _ts_ir
from data_loader import load_dt
import pandas as pd

# Load close data
dt = load_dt(['close'])

# Load Barra data
beta_path = COURSE_DATA_DIR / "barra" / "style" / "Beta.pkl"
size_path = COURSE_DATA_DIR / "barra" / "style" / "Size.pkl"

beta = read_pickle_bypass(beta_path)
size = read_pickle_bypass(size_path)

# Assign stock codes
idxwgt = pd.read_csv(COURSE_DATA_DIR / "idxWgt.csv", index_col=0, parse_dates=True)
beta.columns = idxwgt.columns[:len(beta.columns)]
size.columns = idxwgt.columns[:len(size.columns)]

# Align
beta_aligned = beta.reindex(index=dt['close'].index, columns=dt['close'].columns)
size_aligned = size.reindex(index=dt['close'].index, columns=dt['close'].columns)

# Calculate IR
beta_ir = _ts_ir(beta_aligned, 20)
size_ir = _ts_ir(size_aligned, 20)
factor = beta_ir - size_ir

# Check coverage by year
print("=== Factor 26 Coverage by Year ===")
for year in range(2017, 2026):
    year_data = factor[factor.index.year == year]
    valid = year_data.notna().sum().sum()
    total = year_data.size
    print(f"{year}: {valid}/{total} = {valid/total*100:.1f}%")

# Check a specific recent period
print("\n=== Last 30 days of factor values ===")
print("Date | Valid stocks | Total stocks")
for i in range(-30, 0):
    date = factor.index[i]
    valid = factor.iloc[i].notna().sum()
    total = len(factor.iloc[i])
    print(f"{date.strftime('%Y-%m-%d')} | {valid} | {total}")
