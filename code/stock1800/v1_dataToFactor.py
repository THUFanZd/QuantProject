import pandas as pd 
import numpy as np
import os
import tushare as ts
import tools as tl
from feature import *
import matplotlib.pyplot as plt

#%% 读取配置文件
config = tl.read_json_config()
pro = ts.pro_api(config['api']['key'])


#%% 地址
path1800 = config['paths']['S1800'] + 'matrix//'

sd = '2016-01-01'
sd_per = '2017-01-01'

#%% 获取matrix数据
totalPool = pd.read_pickle(config['paths']['S1800'] + 'indexBase.pkl')
matrixList = os.listdir(path1800)

dt = {}
for v in matrixList:
    tmp = pd.read_pickle(path1800 + v)
    tmp = tmp[tmp.index >= sd]
    tmp = tmp[totalPool['con_code']]
    tmpName = v[:-4]
    dt[tmpName] = tmp
    tmp.index = pd.to_datetime(tmp.index)
    # print(tmpName,tmp.shape )


# delete the new listed stocks: 30 days
listed = dt['vol'].copy()
listed[listed.isna()] = 0 
listed = (listed.cumsum() > 0)  #  get the cumsum values 
listed = listed.shift(40)
listed.sum(axis=1).plot()
plt.title('list stock number')
plt.show()
for v in dt.keys():
    dt[v][listed == 0] = np.nan


# 行情数据说明：https://tushare.pro/document/2?doc_id=27
# 基础数据说明：https://tushare.pro/document/2?doc_id=32

# vol	float	成交量 （手）
# amount	float	成交额 （千元）
dt['amount'] = (dt['amount'] * 1000).round(2)
dt['vol'] = (dt['vol'] * 100).round(0)
dt['vwap'] = (dt['amount']/dt['vol']).round(4)
dt['high'] = (dt['high'] ).round(2)
dt['low'] = (dt['low'] ).round(2)
dt['open'] = (dt['open'] ).round(2)
dt['close'] = (dt['close'] ).round(2)

dt['totalRet'][dt['totalRet'].abs() > 0.2] = np.nan
dt['totalRet'] = dt['totalRet'].round(6)
IndexRet = dt['totalRet'].mean(axis = 1)
IndexRets = Repmat(dt['totalRet'],IndexRet)
dt['exRet'] = (dt['totalRet'] - IndexRets ).round(6)


#%%  因子计算和因子收益
# 计算因子值
f1 = -1*ts_Decay((ts_Decay(dt['close'],10)-ts_Decay(dt['vwap'],10))/dt['vwap']*(dt['high']-dt['low']),40)
# f1 = -1*ts_Decay(dt['vwap']/dt['close']*(dt['high']-dt['low'])/dt['close']*(dt['vol']/ts_Delay(dt['vol'],1)),10)
# f1 = -1*ts_Decay(dt['exRet']*(dt['vol']/ts_Delay(dt['vol'],1)),40)
# f1 = -1*ts_Decay(dt['exRet']*(dt['high']-dt['low'])/dt['close']*(dt['vol']/ts_Delay(dt['vol'],1)),60)
# f1 = -1*ts_Decay((ts_Decay(dt['close'],10)-ts_Decay(dt['vwap'],10))/dt['vwap']*(dt['high']-dt['low'])/dt['close'],20)
# print(f1.tail(1))

f1[listed == 0] = np.nan
f1_stand = pn_TransNorm(f1.copy())
# print(f1_stand.tail(1))
# 从因子到持仓
port_pos, port_neg = get_ls_post(f1_stand.copy())
f1_stand_port = port_pos + port_neg 
# print(f1_stand_port.tail(1))
# 因子收益计算
rets = (f1_stand_port.copy().shift(2) * dt['totalRet']).sum(axis=1)
rets = rets[rets.index >= sd_per]
rets.cumsum().plot()

# 业绩评价指标
sr = rets.mean() / rets.std() * (250)**0.5  # sharpe
ar = rets.mean()  * (250)                   # annual return

ics = (f1_stand_port.copy().shift(2).corrwith(dt['totalRet'], axis=1))
ics = ics[ics.index >= sd_per]
ic_mean = ics.mean() * 250
ic_ir = ics.mean() / ics.std() * (250)**0.5

print(sr,ar,ic_mean, ic_ir)


#%% 因子收益二 多头和空头, 分组收益

ret_ave = dt['totalRet'].copy()
ret_ave[listed==0] = np.nan
ret_ave = ret_ave.mean(axis=1)

rets_both = (f1_stand_port.shift(2) * dt['totalRet']).sum(axis=1)
rets_pos = (port_pos.shift(2) * dt['totalRet']).sum(axis=1) - ret_ave
rets_neg = (port_neg.shift(2) * dt['totalRet']).sum(axis=1) + ret_ave
rs = pd.DataFrame()
rs['ls'] = rets.copy()
rs['pos'] = rets_pos.copy()
rs['neg'] = rets_neg.copy()
rs = rs[rs.index > sd_per ]
rs.cumsum().plot()
plt.show()

f_qr = f1.copy()
f_qr[listed == 0] = np.nan
qr = tl.GetQuantileRet(f_qr,dt['totalRet'],5,2)
qr = qr[qr.index > sd_per ]
qr.cumsum().plot()
plt.show()

(qr.mean()*250).plot()


#%% 因子收益三 持仓收益 

hold_pos, hold_neg = get_portFromFactor_both(f1_stand.copy(),50)

ret_ave = dt['totalRet'].copy()
ret_ave[listed==0] = np.nan
ret_ave = ret_ave.mean(axis=1)

rs = pd.DataFrame()
rs['ls'] =  ((hold_pos + hold_neg).shift(2) * dt['totalRet']).sum(axis=1)
rs['pos'] = (hold_pos.shift(2) * dt['totalRet']).sum(axis=1) - ret_ave
rs['neg'] = (hold_neg.shift(2) * dt['totalRet']).sum(axis=1) + ret_ave
rs = rs[rs.index > sd_per ]
rs.cumsum().plot()
plt.show()


pos_hold = pd.DataFrame()
pos_hold['strategy'] = ((hold_pos ).shift(2) * dt['totalRet']).sum(axis=1)
pos_hold['average'] =  ret_ave
pos_hold['excessRet'] = pos_hold['strategy'] - pos_hold['average'] 
pos_hold = pos_hold[pos_hold.index > sd_per ]
pos_hold.cumsum().plot()
plt.title('Positive hold: AR '+  str(round(pos_hold['excessRet'].mean() * 250,2)))
plt.show()

neg_hold = pd.DataFrame()
neg_hold['strategy'] = (( -1*hold_neg ).shift(2) * dt['totalRet']).sum(axis=1)
neg_hold['average'] =  ret_ave
neg_hold['excessRet'] = neg_hold['average'] - neg_hold['strategy']
neg_hold = neg_hold[neg_hold.index > sd_per ]
neg_hold.cumsum().plot()
plt.title('Negtive hold: AR '+  str(round(neg_hold['excessRet'].mean() * 250,2)))
plt.show()




#%% 忽略了什么?
# 交易成本
costRate = 0.0005 # 单边成本 : 印花税0.0005， 佣金0.0002 * 2， 冲击成本

# 换手
turnoverRateDaily = (f1_stand_port - f1_stand_port.shift(1)).abs().sum(axis = 1)
turnoverRateDaily = turnoverRateDaily[turnoverRateDaily.index > sd_per]
turnoverRateDaily.plot()
turnoverRate = round(turnoverRateDaily.mean(),3)
plt.title('Factor turnoverRate: '+ str(turnoverRate) )
plt.show()

# 加上成本之后的因子收益
rets_both = (f1_stand_port.shift(2) * dt['totalRet']).sum(axis=1)
turnoverRateDaily = (f1_stand_port - f1_stand_port.shift(1)).abs().sum(axis = 1)
costPct = turnoverRateDaily * costRate
rets_both_withCost = rets_both - costPct

rs = pd.DataFrame()
rs['noCost'] = rets_both
rs['withCost'] = rets_both_withCost

rs = rs[rs.index > sd_per]
rs.cumsum().plot()


#  加上成本的持仓收益

hold_pos, hold_neg = get_portFromFactor_both(f1_stand.copy(),50)

pos_hold = pd.DataFrame()
pos_hold['straNoCost'] = ((hold_pos ).shift(2) * dt['totalRet']).sum(axis=1)
pos_hold = pos_hold[pos_hold.index > sd_per]

turnoverRateDaily = (hold_pos - hold_pos.shift(1)).abs().sum(axis = 1)
turnoverRateDaily = turnoverRateDaily[turnoverRateDaily.index > sd_per]

turnoverRate = round(turnoverRateDaily.mean(),3)
pos_hold['straWithCost'] = pos_hold['straNoCost'] - turnoverRateDaily * costRate

pos_hold.cumsum().plot()



#%% 其他数据开发因子
'''
dict_keys(['adj_close', 'amount', 'change', 'circ_mv', 'close', 'dv_ttm', 
           'float_share', 'free_share', 'high', 'low', 'open', 'overnightRet', 
           'pb', 'pct_chg', 'pe_ttm', 'pre_close', 'ps_ttm', 'totalRet', 
           'total_mv', 'total_share', 'turnover_rate', 'turnover_rate_f',
            'vol', 'vwap', 'exRet'])
'''

f1 = -1 * dt['turnover_rate']
f1[listed == 0] = np.nan
f1_stand = pn_TransNorm(f1.copy())
# print(f1_stand.tail(1))
# 从因子到持仓
port_pos, port_neg = get_ls_post(f1_stand.copy())
f1_stand_port = port_pos + port_neg 
# print(f1_stand_port.tail(1))
# 因子收益计算
rets = (f1_stand_port.copy().shift(2) * dt['totalRet']).sum(axis=1)
rets = rets[rets.index >= sd_per]
rets.cumsum().plot()

# 业绩评价指标
sr = rets.mean() / rets.std() * (250)**0.5  # sharpe
ar = rets.mean()  * (250)                   # annual return

ics = (f1_stand_port.copy().shift(2).corrwith(dt['totalRet'], axis=1))
ics = ics[ics.index >= sd_per]
ic_mean = ics.mean() * 250
ic_ir = ics.mean() / ics.std() * (250)**0.5

print(sr,ar,ic_mean, ic_ir)


#%% 财务数据

# https://tushare.pro/document/2?doc_id=36  资产负债表
# https://tushare.pro/document/2?doc_id=44  现金流量表
# https://tushare.pro/document/2?doc_id=33  利润表

# 已经清洗ttm化，
# 数据获取：D:\ts_daily\code\updateData\v2_dateFin.py
# 数据清洗和年化：D:\ts_daily\code\combine\v2_c_fin.py

balance_ttm = pd.read_pickle(config['paths']['S1800'] + 'finTTM//' + 'balance_ttm.pkl')
income_ttm = pd.read_pickle(config['paths']['S1800'] + 'finTTM//' + 'income_ttm.pkl')
cash_ttm = pd.read_pickle(config['paths']['S1800'] + 'finTTM//' + 'cash_ttm.pkl')

# 数据清洗
balance_ttm['ann_date_last'] = balance_ttm[['f_ann_date','ann_date']].max(axis = 1)
income_ttm['ann_date_last'] = income_ttm[['f_ann_date','ann_date']].max(axis = 1)
cash_ttm['ann_date_last'] = cash_ttm[['f_ann_date','ann_date']].max(axis = 1)

balance_ttm['ann_date_last'] = pd.to_datetime(balance_ttm['ann_date_last'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')
income_ttm['ann_date_last'] = pd.to_datetime(income_ttm['ann_date_last'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')
cash_ttm['ann_date_last'] = pd.to_datetime(cash_ttm['ann_date_last'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')


# 财务因子开发


def get_fit2mat(df_test2,colname,datestr,baseMatrix):  # turn fixed table data back to matrix
    df_test = df_test2.copy()
    df = df_test[[datestr,'ts_code',colname] ]
    df = df.drop_duplicates(subset=['ts_code', 'ann_date_last'], keep='last')
    data4=df.set_index([datestr,'ts_code'])
    data5=data4.unstack()
    indx = list(data5.index)
    a = list(data5.columns)
    code = list()
    for v in a:
        code.append(v[1])
    out = pd.DataFrame(data5.values)
    out.index = pd.to_datetime(indx)
    out.columns = code

    common_rows = out.index.union(baseMatrix.index)  
    common_cols = out.columns.union(baseMatrix.columns) 
    c = out.reindex(index=common_rows, columns=common_cols)
    c = c.ffill()
    c = c[baseMatrix.columns]
    c = c[c.index.isin(baseMatrix.index)]
    return c


c = get_fit2mat(balance_ttm,'money_cap','ann_date_last',dt['close'])
c2 = get_fit2mat(income_ttm,'revenue','ann_date_last',dt['close'])
c3 = get_fit2mat(cash_ttm,'c_fr_sale_sg','ann_date_last',dt['close'])

f1 = c2/c2
f1[listed == 0] = np.nan
f1_stand = pn_TransNorm(f1.copy())
# print(f1_stand.tail(1))
# 从因子到持仓
port_pos, port_neg = get_ls_post(f1_stand.copy())
f1_stand_port = port_pos + port_neg 
# print(f1_stand_port.tail(1))
# 因子收益计算
rets = (f1_stand_port.copy().shift(2) * dt['totalRet']).sum(axis=1)
rets = rets[rets.index >= sd_per]
rets.cumsum().plot()

