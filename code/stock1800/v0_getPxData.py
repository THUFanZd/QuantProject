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


#%% 地址


raw_path = config['paths']['px'] + 'raw//'
raw_date_path = config['paths']['px'] + 'dates_raw.pkl'

matrix_path = config['paths']['px'] + 'matrix//'

path1800 = config['paths']['S1800']


#%% 获取成份股和权重

raw_date = pd.read_pickle(raw_date_path)

index500 = pro.index_weight(index_code='000905.SH', start_date='20250601', end_date='20250822')
index500 = index500[index500['trade_date'] == index500['trade_date'].max()]
index1000 = pro.index_weight(index_code='000852.SH', start_date='20250601', end_date='20250822')
index1000 = index1000[index1000['trade_date'] == index1000['trade_date'].max()]
totalPool = pd.concat([index500,index1000])
totalPool['code'] = [s[:6] for s in totalPool['con_code']]

totalPool.to_pickle(path1800 + 'indexBase.pkl')
totalPool.to_csv(path1800 + 'indexBase.csv')

#%% 更新px_dfs

totalPool = pd.read_pickle(path1800 + 'indexBase.pkl')
matrixList = os.listdir(matrix_path)
matrixListName = [s[:-4] for s in matrixList]


for v in matrixList:
    tmp = pd.read_pickle(matrix_path + v)
    tmp = tmp[totalPool['con_code']]
    tmpName = v[:-4]
    tmp.to_pickle(path1800 + 'matrix//' + v )
    print(tmpName,tmp.shape )




#%% 财务数据清洗

basic1800 = pd.read_pickle(config['paths']['S1800'] + 'indexBase.pkl')

ttm_path = config['paths']['fin'] + 'ttm//'

balance_ttm = pd.read_pickle(ttm_path + 'balance_ttm.pkl')
income_ttm = pd.read_pickle(ttm_path + 'income_ttm.pkl')
cash_ttm = pd.read_pickle(ttm_path + 'cash_ttm.pkl')


balance_ttm = balance_ttm[balance_ttm['ts_code'].isin(basic1800['con_code'])]
income_ttm = income_ttm[income_ttm['ts_code'].isin(basic1800['con_code'])]
cash_ttm = cash_ttm[cash_ttm['ts_code'].isin(basic1800['con_code'])]

balance_ttm.to_pickle(config['paths']['S1800'] + 'finTTM//' + 'balance_ttm.pkl')
income_ttm.to_pickle(config['paths']['S1800'] + 'finTTM//'  + 'income_ttm.pkl')
cash_ttm.to_pickle(config['paths']['S1800'] + 'finTTM//'  + 'cash_ttm.pkl')

