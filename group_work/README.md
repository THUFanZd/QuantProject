# Group Work Factor Pipeline

This folder keeps the course assignment code separate from the original
research scripts under `code/stock1800`.

```text
group_work/
├── factor_lib/                 # Reusable factor/data helpers
├── 01_feature_engineering/     # Stage 1 deliverables
└── 02_factor_calculation/      # Stage 2 scripts and outputs
```

Current implemented factors:

- `factor_05_volume_price_divergence_cov`: volume-price divergence covariance.
- `factor_08_liquidity_stability`: negative smoothed amount rank.
- `factor_35_price_spread_momentum`: open-close spread with price momentum rank.
- `factor_38_volatility_difference_proxy`: proxy for volume/residual-volatility percentile spread.
- `factor_42_adjusted_price_reversal`: 30-day adjusted-close reversal.

Run a quick evaluation:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_42_adjusted_price_reversal
```
