import sys
sys.path.insert(0, 'group_work/factor_lib')
from factors import read_pickle_bypass, COURSE_DATA_DIR
from data_loader import load_dt
import pandas as pd

# Load Barra Beta
beta_path = COURSE_DATA_DIR / "barra" / "style" / "Beta.pkl"
beta = read_pickle_bypass(beta_path)
print("Beta shape:", beta.shape)
print("Beta index:", beta.index[0], "to", beta.index[-1])
print("Beta columns type:", type(beta.columns[0]))
print("Beta sample:", beta.iloc[-5:, :3])

# Load Barra Size
size_path = COURSE_DATA_DIR / "barra" / "style" / "Size.pkl"
size = read_pickle_bypass(size_path)
print("\nSize shape:", size.shape)
print("Size index:", size.index[0], "to", size.index[-1])

# Load idxWgt for stock codes
idxwgt_path = COURSE_DATA_DIR / "idxWgt.csv"
idxwgt = pd.read_csv(idxwgt_path, index_col=0, parse_dates=True)
print("\nidxWgt shape:", idxwgt.shape)
print("idxWgt columns:", list(idxwgt.columns[:5]))

# Load close for reference
dt = load_dt(['close'])
print("\nClose shape:", dt['close'].shape)
print("Close columns:", list(dt['close'].columns[:5]))
print("Close index:", dt['close'].index[0], "to", dt['close'].index[-1])

# Check date overlap
common_dates = beta.index.intersection(dt['close'].index)
print("\nCommon dates between Beta and Close:", len(common_dates))
print("Beta dates:", beta.index[:5].tolist())
print("Close dates:", dt['close'].index[:5].tolist())

# Assign columns and check
beta.columns = idxwgt.columns[:len(beta.columns)]
size.columns = idxwgt.columns[:len(size.columns)]
common_cols = set(beta.columns) & set(dt['close'].columns)
print("\nCommon columns after assignment:", len(common_cols))
