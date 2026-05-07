# ts_daily

`ts_daily` 是一个以本地 `pickle` 数据仓库为中心的 A 股日频量化研究项目。仓库当前的代码主要完成三件事：

1. 通过 Tushare 拉取日频行情、财务报表和申万行业数据。
2. 将原始表格数据整理成面板矩阵、TTM 财务数据和研究股票池数据。
3. 在一个由中证 500 和中证 1000 成分股拼接得到的股票池上做因子构造、回测和简单优化。

项目是“脚本驱动”的研究仓库，不是一个封装好的 Python 包，也没有命令行入口或单元测试。你通常按脚本顺序逐步运行。

## 目录结构

```text
ts_daily/
├─ code/
│  ├─ updateData/     # 拉取 Tushare 原始数据
│  ├─ combine/        # 清洗、合并、矩阵化、TTM 化
│  └─ stock1800/      # 股票池构建、因子测试、因子组合优化
├─ data/
│  ├─ config.json     # Tushare Token 和数据路径配置
│  ├─ dates.pkl       # 交易日历
│  ├─ px/             # 行情原始数据、宽表、矩阵
│  ├─ fin/            # 财务原始数据、清洗表、TTM 数据
│  ├─ hy/             # 申万行业分类与行业矩阵
│  └─ stock1800_px/   # 研究股票池对应的价格矩阵和财务 TTM
└─ README.md
```

## 当前仓库里已有的数据

仓库已经包含大量本地数据文件，可直接用于查看和复现。

- `data/px/raw/` 当前目录名范围是 `20100104` 到 `20251114`
- `data/fin/raw/` 当前目录名范围是 `20100331` 到 `20251231`
- `data/px/matrix/` 已包含 `close/open/high/low/amount/vol/turnover_rate/pe_ttm/pb/ps_ttm/totalRet/overnightRet` 等常用矩阵
- `data/stock1800_px/indexBase.csv` 当前股票池记录数为 `1500`

## 环境要求

建议使用独立虚拟环境，至少安装下面这些依赖：

```bash
pip install pandas numpy tushare matplotlib scipy optuna
```

项目代码里明确依赖了以下库：

- `pandas`
- `numpy`
- `tushare`
- `matplotlib`
- `scipy`
- `optuna`

## 配置

核心配置文件是 [`data/config.json`](data/config.json)。

当前脚本真正会用到的是：

- `api.key`：Tushare Pro Token
- `paths.*`：各类数据目录

`database` 字段目前没有在现有脚本中使用。

注意两点：

1. 现有配置使用的是 Windows 绝对路径，默认指向 `D://ts_daily//...`。如果你的仓库不在 `D:\ts_daily`，需要先修改配置。
2. 财务拉取脚本调用了 `balancesheet_vip`、`income_vip`、`cashflow_vip`，因此不仅需要 Tushare Token，还需要对应接口权限。

## 主流程

建议从仓库根目录执行下面这些脚本。

### 1. 拉取原始数据

```bash
python code/updateData/v1_datePx.py
python code/updateData/v2_dateFin.py
python code/updateData/v3_dateSW.py
```

脚本职责：

- [`code/updateData/v1_datePx.py`](code/updateData/v1_datePx.py)：更新交易日历、日行情、复权因子、日频基础指标
- [`code/updateData/v2_dateFin.py`](code/updateData/v2_dateFin.py)：更新资产负债表、利润表、现金流量表原始数据
- [`code/updateData/v3_dateSW.py`](code/updateData/v3_dateSW.py)：更新申万 2021 一级行业及行业矩阵

### 2. 清洗与矩阵化

```bash
python code/combine/v1_c_Px.py
python code/combine/v2_c_fin.py
python code/combine/v3_c_adjFactor.py
```

脚本职责：

- [`code/combine/v1_c_Px.py`](code/combine/v1_c_Px.py)：把日行情原始表整理到 `dfs` 和 `matrix`
- [`code/combine/v2_c_fin.py`](code/combine/v2_c_fin.py)：清洗财务表并生成 TTM 数据
- [`code/combine/v3_c_adjFactor.py`](code/combine/v3_c_adjFactor.py)：基于复权因子生成 `adj_close`、`totalRet`、`overnightRet`

### 3. 构建研究股票池

```bash
python code/stock1800/v0_getPxData.py
```

这个脚本会：

- 获取当前股票池成分及权重
- 从全市场矩阵中截取对应股票池的价格矩阵
- 从全市场 TTM 财务表中截取股票池对应的财务数据

### 4. 因子研究与优化

```bash
python code/stock1800/v1_dataToFactor.py
python code/stock1800/v2_factorOptComp.py
```

脚本职责：

- [`code/stock1800/v1_dataToFactor.py`](code/stock1800/v1_dataToFactor.py)：构造单因子，计算多空收益、分组收益、IC、换手率和简单交易成本影响
- [`code/stock1800/v2_factorOptComp.py`](code/stock1800/v2_factorOptComp.py)：用 `optuna` 调参，并对多个因子做等权、收益加权和 Markowitz 组合

这两个脚本都会直接画图，适合本地研究环境交互式运行。

## 主要数据产物

### 行情数据

- `data/px/raw/<trade_date>/daily.pkl`
- `data/px/raw/<trade_date>/adj_factor.pkl`
- `data/px/raw/<trade_date>/daily_basic.pkl`
- `data/px/dfs/daily.pkl`
- `data/px/dfs/adj_factor.pkl`
- `data/px/dfs/daily_basic.pkl`
- `data/px/matrix/*.pkl`

### 财务数据

- `data/fin/raw/<period>/balance.pkl`
- `data/fin/raw/<period>/income.pkl`
- `data/fin/raw/<period>/cash.pkl`
- `data/fin/clean/balance.pkl`
- `data/fin/clean/income.pkl`
- `data/fin/clean/cash.pkl`
- `data/fin/ttm/balance_ttm.pkl`
- `data/fin/ttm/income_ttm.pkl`
- `data/fin/ttm/cash_ttm.pkl`

### 行业与股票池数据

- `data/hy/sw21.pkl`
- `data/hy/sw21.csv`
- `data/hy/matrix/sw21l1.pkl`
- `data/stock1800_px/indexBase.pkl`
- `data/stock1800_px/matrix/*.pkl`
- `data/stock1800_px/finTTM/*_ttm.pkl`

## 代码里的几个重要约束

这些不是抽象建议，而是当前仓库真实存在的实现约束。

### 1. `stock1800` 目录名和实际股票池不完全一致

[`code/stock1800/v0_getPxData.py`](code/stock1800/v0_getPxData.py) 当前抓取的是：

- `000905.SH` 中证 500
- `000852.SH` 中证 1000

拼接后当前股票池规模是 `1500`。也就是说，这部分代码的实际口径更接近“中证 500 + 中证 1000”，而不是标准定义下的“中证 1800”。

### 2. 价格合并脚本依赖 `data/px/dates_raw.pkl`

[`code/combine/v1_c_Px.py`](code/combine/v1_c_Px.py) 和 [`code/combine/v3_c_adjFactor.py`](code/combine/v3_c_adjFactor.py) 读取的是 [`data/px/dates_raw.pkl`](data/px/dates_raw.pkl)，但 [`code/updateData/v1_datePx.py`](code/updateData/v1_datePx.py) 更新交易日历时写入的是 [`data/dates.pkl`](data/dates.pkl)。

仓库当前已经存在 `data/px/dates_raw.pkl`，所以现有数据可以直接用；如果你在全新环境重跑，需要自己确认这两个文件的衔接关系，或直接改代码统一文件名。

### 3. 股票池权重抓取日期窗口是写死的

[`code/stock1800/v0_getPxData.py`](code/stock1800/v0_getPxData.py) 里 `index_weight` 的查询窗口当前写死为：

- `start_date='20250601'`
- `end_date='20250822'`

如果你要在别的时间点刷新股票池，请先改这个窗口。

### 4. 代码是研究脚本，不是稳定接口

仓库里存在不少直接写死的起始日期、样本区间、成本参数和画图逻辑，例如：

- 单因子研究从 `2016-01-01`、绩效观察从 `2017-01-01`
- 调参样本内区间使用 `2017-01-01` 到 `2022-01-01`
- 默认单边成本写死为 `0.0005`

如果你打算把这里的逻辑接成批处理或生产流程，建议先抽象配置项和函数入口。

## 研究辅助资料

[`code/stock1800/report_Daily`](code/stock1800/report_Daily) 下保存了多份量化因子相关研报，可作为当前因子构造思路的参考资料。

## 后续建议

如果你准备继续维护这个项目，优先值得补的是：

1. 统一 `dates.pkl` / `dates_raw.pkl` 的命名和流转。
2. 把股票池定义从“目录名”与“脚本实际逻辑”统一起来。
3. 增加 `requirements.txt` 或 `environment.yml`。
4. 把研究脚本改造成可配置的函数或 CLI。
