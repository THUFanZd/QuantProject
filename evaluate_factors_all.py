import sys
sys.path.insert(0, 'group_work/factor_lib')
from factors import FACTOR_REGISTRY
from data_loader import load_dt, load_universe_mask, make_listed_mask
import pandas as pd
import numpy as np

# Load data
print("Loading data...")
dt = load_dt(['close', 'open', 'high', 'low', 'vol', 'amount'])
universe_mask = load_universe_mask(dt['close'])
listed_mask = make_listed_mask(dt['vol'])
mask = ~(universe_mask | ~listed_mask)

print(f"Data shape: {dt['close'].shape}")
print(f"Valid data points: {mask.sum().sum()}")

# Test factors
factors_to_test = ['factor_06_ma_filter_reversal', 'factor_13_main_fund_stability',
                   'factor_26_dual_style_ir_spread', 'factor_41_high_open_momentum_decay',
                   'factor_56_cashflow_price_trend']

for factor_name in factors_to_test:
    if factor_name not in FACTOR_REGISTRY:
        print(f"\n{factor_name}: NOT IMPLEMENTED")
        continue

    print(f"\n{'='*50}")
    print(f"Testing {factor_name}")
    print('='*50)

    try:
        factor_func = FACTOR_REGISTRY[factor_name]
        factor = factor_func(dt)

        # Apply mask
        factor_masked = factor.where(mask)

        # Check coverage
        valid_count = factor_masked.notna().sum().sum()
        total_count = mask.sum().sum()
        coverage = valid_count / total_count * 100 if total_count > 0 else 0
        print(f"Coverage: {coverage:.1f}% ({valid_count}/{total_count})")

        if coverage > 0:
            # Simple IC test
            forward_ret = dt['close'].pct_change(5).shift(-5)
            ic_series = factor_masked.corrwith(forward_ret, axis=1, method='spearman')
            ic_mean = ic_series.mean()
            ic_std = ic_series.std()
            icir = ic_mean / ic_std if ic_std > 0 else 0

            print(f"IC Mean: {ic_mean:.4f}")
            print(f"IC Std: {ic_std:.4f}")
            print(f"ICIR: {icir:.4f}")
            print(f"IC>0 ratio: {(ic_series > 0).mean()*100:.1f}%")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
