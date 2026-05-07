import pandas as pd 
import numpy as np
import os
import tushare as ts
import tools as tl


#%% 读取配置文件
config = tl.read_json_config()
# if config:
#     print("配置数据:", config)

pro = ts.pro_api(config['api']['key'])


#%% 更新交易日


raw_path = config['paths']['px'] + 'raw//'
raw_date_path = config['paths']['px'] + 'dates_raw.pkl'

df_path = config['paths']['px'] + 'dfs//'
px_date_path = config['paths']['px'] + 'dates_px.pkl'

matrix_path = config['paths']['px'] + 'matrix//'

raw_date = pd.read_pickle(raw_date_path)



#%% 更新px_dfs

# daily 
# ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
# adj_factor
# ['adj_factor']
# daily_basic
# ['ts_code', 'trade_date', 'close', 'turnover_rate', 'turnover_rate_f',  
#  'volume_ratio', 'pe_ttm', 'pb', 'ps_ttm', 'dv_ratio', 'dv_ttm',
# 'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv']

# daily
raw_date_trade = raw_date[raw_date['is_open'] == 1]

daily = tl.combine_rawDt(raw_date_trade,raw_path,df_path,'daily')
daily = daily[daily['ts_code'].str[-2:].isin(['SZ', 'SH'])]
daily_basic = tl.combine_rawDt(raw_date_trade,raw_path,df_path,'daily_basic')
adj_factor = tl.combine_rawDt(raw_date_trade,raw_path,df_path,'adj_factor')

daily_col = ['close', 'pre_close','open']
daily_dict = {}
for v in daily_col:
    daily_dict[v] = tl.table2mat(daily,v,'trade_date')


daily_basic_col = ['close']
daily_basic_dict = {}
close = daily_dict['close'].copy()
for v in daily_basic_col:
    tmp = tl.table2mat(daily_basic,v,'trade_date')
    common_cols = list(set(close.columns) & set(tmp.columns))
    tmp2 = pd.DataFrame(np.nan,index = close.index, columns = close.columns)
    tmp2[common_cols] = tmp[common_cols]
    daily_basic_dict[v]  = tmp2

#  复权因子 和 复权价格： 实际的totalRet 和实际的overnightRet
close = daily_dict['close'].copy()
tmp = tl.table2mat(adj_factor,'adj_factor','trade_date')
common_cols = list(set(close.columns) & set(tmp.columns))
adj_factor = pd.DataFrame(np.nan,index = close.index, columns = close.columns)
adj_factor[common_cols] = tmp[common_cols]
adj_factor = adj_factor.fillna(1)
daily_dict['adj_close'] = adj_factor * daily_dict['close'] 
daily_dict['totalRet'] = daily_dict['adj_close'] / daily_dict['adj_close'].shift(1) - 1
daily_dict['overnightRet'] =  (daily_dict['open'] * adj_factor) / (daily_dict['close'] * adj_factor).shift(1) - 1


#%%  matrix

for v in ['adj_close','totalRet','overnightRet']:
    daily_dict[v].to_pickle(matrix_path + v + '.pkl')

a = pd.read_pickle(matrix_path + 'amount' + '.pkl')












