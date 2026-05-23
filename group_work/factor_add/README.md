# factor_add 新增因子实验

本目录补充 15 个增强因子，分为三类：
1. 中性化/正交化增强
2. 基本面 × 量价/资金流
3. Barra 风格增强

核心通过因子：

factor_add_06_quality_x_flow

公式：
quality = pn_Rank(NetProfitTTMQ1 / NetAssetQ1)
flow = pn_Rank(ts_Sum(net_mf_amount, 20))
factor = quality * flow

评估口径：
复用 group_work/02_factor_calculation/evaluate_factor.py 中的 evaluate_factor()
并使用 pn_TransNorm + get_ls_post 组合方式。

运行方式：
python group_work/factor_add/evaluate_factor_add.py

结果：
AR = 16.25%
SR = 2.01
与 core5 最大相关 = 0.253
