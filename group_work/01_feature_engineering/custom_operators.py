"""Custom operators added for stage 1 feature engineering.

The actual shared implementations were added to `code/stock1800/feature.py`
so other teammates can import them from the original operator library.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
if str(FEATURE_DIR) not in sys.path:
    sys.path.insert(0, str(FEATURE_DIR))

from feature import pn_CrossResidual, pn_Rank, ts_Cov, ts_Percentage  # noqa: E402,F401


__all__ = ["pn_Rank", "pn_CrossResidual", "ts_Cov", "ts_Percentage"]
