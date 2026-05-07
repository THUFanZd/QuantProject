import pandas as pd 
import numpy as np
import os
import tushare as ts
import tools as tl


#%% 读取配置文件
config = tl.read_json_config()
pro = ts.pro_api(config['api']['key'])

#%% 地址

raw_path = config['paths']['fin'] + 'raw//'
df_path = config['paths']['fin'] + 'clean//'
matrix_path = config['paths']['fin'] + 'clean//'
close = pd.read_pickle(config['paths']['px'] + '//matrix//close.pkl')
sw21  = pd.read_pickle(config['paths']['hy'] + 'sw21.pkl')
sw21 = sw21[sw21['ts_code'].str[-2:].isin(['SZ', 'SH'])]

#%% 在table级别清洗数据：
'''
删除北交所
删除重复项
''' 

balance_table = []
income_table = []
cash_table = []
for v in os.listdir(raw_path):
    
    tmp1 = pd.read_pickle(raw_path + v + '//balance.pkl')
    tmp1 = tmp1[tmp1['ts_code'].str[-2:].isin(['SZ', 'SH'])]
    tmp1 = tmp1.sort_values(['update_flag'])
    tmp1 = tmp1.drop_duplicates(subset=['ts_code'], keep='first')
    tmp1 = tmp1.fillna(0)

    tmp2 = pd.read_pickle(raw_path + v + '//income.pkl')
    tmp2 = tmp2[tmp2['ts_code'].str[-2:].isin(['SZ', 'SH'])]
    tmp2 = tmp2[tmp2[['oper_cost', 'int_exp','comm_exp','sell_exp','admin_exp']].sum(axis = 1) > 0]
    tmp2 = tmp2.sort_values(['update_flag'])
    tmp2 =  tmp2.drop_duplicates(subset=['ts_code'], keep='first')
    tmp2 = tmp2.fillna(0)

    tmp3 = pd.read_pickle(raw_path + v + '//cash.pkl')
    tmp3 = tmp3[tmp3['ts_code'].str[-2:].isin(['SZ', 'SH'])]
    tmp3 = tmp3.sort_values(['update_flag'])
    tmp3 = tmp3.drop_duplicates(subset=['ts_code'], keep='first')
    tmp3 = tmp3.fillna(0)

    common_cols = list(set(tmp1['ts_code']) & set(tmp2['ts_code']))
    common_cols = list(set(tmp1['ts_code']) & set(common_cols))

    tmp1 = tmp1[tmp1['ts_code'].isin(common_cols)]
    tmp2 = tmp2[tmp2['ts_code'].isin(common_cols)]
    tmp3 = tmp3[tmp3['ts_code'].isin(common_cols)]
    print(v, len(tmp1),len(tmp2),len(tmp2))

    balance_table.append(tmp1)
    income_table.append(tmp2)
    cash_table.append(tmp3)

balance_table = pd.concat(balance_table)
income_table = pd.concat(income_table)
cash_table = pd.concat(cash_table)

balance_table.to_pickle(df_path + 'balance.pkl')
income_table.to_pickle(df_path + 'income.pkl')
cash_table.to_pickle(df_path + 'cash.pkl')


#%% 财务年化

ttm_path = config['paths']['fin'] + 'ttm//'

balance_table = pd.read_pickle(df_path + 'balance.pkl')
income_table = pd.read_pickle(df_path + 'income.pkl')
cash_table = pd.read_pickle(df_path + 'cash.pkl')

# sw21hy = pd.read_pickle(config['paths']['hy'] + 'sw21.pkl')
# sw21hy.index = sw21hy['ts_code']
# balance_table.index = balance_table['ts_code']
# balance_table['sw1'] = sw21hy['l1_name']

balance_ttm = []
income_ttm = []
cash_ttm = []
# v = '603288.SH'
n = 0
for v in balance_table['ts_code'].unique():
    n = n +1 
    print(n ,v)
    balance__ = balance_table[balance_table['ts_code'] == v].copy()
    income__ = income_table[income_table['ts_code'] == v].copy()
    cash__ = cash_table[cash_table['ts_code'] == v].copy()
    balanceA,incomeA,cashA  = tl.clean_fin(balance__,income__,cash__)
    balance_ttm.append(balanceA)
    income_ttm.append(incomeA)
    cash_ttm.append(cashA)


balance_ttm = pd.concat(balance_ttm)
income_ttm = pd.concat(income_ttm)
cash_ttm = pd.concat(cash_ttm)

balance_ttm.to_pickle(ttm_path + 'balance_ttm.pkl')
income_ttm.to_pickle(ttm_path + 'income_ttm.pkl')
cash_ttm.to_pickle(ttm_path + 'cash_ttm.pkl')
