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




import optuna
from optuna.visualization import plot_contour
# import plotly


def get_factorRt(f1_stand_port,TotalRet,delayNum,costRate,SDate,EDate):
    rets_both = (f1_stand_port.shift(delayNum) * TotalRet).sum(axis=1)
    turnoverRateDaily = (f1_stand_port - f1_stand_port.shift(1)).abs().sum(axis = 1)
    costPct = turnoverRateDaily * costRate
    rets_both_withCost = rets_both - costPct
    rets_both_withCost = rets_both_withCost.loc[SDate:EDate]
    turnoverRateDaily = turnoverRateDaily.loc[SDate:EDate]
    sr = round(rets_both_withCost.mean() / rets_both_withCost.std() * (250)**0.5 ,2) # sharpe
    ar = round(rets_both_withCost.mean()  * (250) ,2) 
    to = round(turnoverRateDaily.mean() ,2)
    print(sr,ar ,to)
    return rets_both_withCost,sr , ar, to          # annual return

    
def objective(trial): 
    # 1 define the parameter: the range and the type
    x = trial.suggest_int("x",2,20)
    y = trial.suggest_int("y", 10,50)  # trial.suggest_float
    # 2 get the output of the function:  Sharpe ratio
    f1 = -1*ts_Decay((ts_Decay(dt['close'],x)-ts_Decay(dt['vwap'],x))/dt['vwap']*(dt['high']-dt['low']),y)
    f1[listed == 0] = np.nan
    f1_stand = pn_TransNorm(f1.copy())
    port_pos, port_neg = get_ls_post(f1_stand.copy())
    f1_stand_port = port_pos + port_neg 

    costRate = 0.0005
    delayNum = 2
    TotalRet = dt['totalRet']
    SDate,EDate = '2017-01-01','2022-01-01'  # the IS
    [rets_both_withCost,sr , ar, to] = get_factorRt(f1_stand_port,TotalRet,delayNum,costRate,SDate,EDate)
    return sr

# run the study, set the trial round be 15.
study = optuna.create_study(direction="maximize") 
study.optimize(objective, n_trials = 15 )


optuna.visualization.matplotlib.plot_contour(study)

optuna.visualization.matplotlib.plot_param_importances(study)

best_params = study.best_params
print(best_params)

SDate,EDate = '2017-01-01','2022-01-01'  # the OTS
costRate = 0.0005
delayNum = 2
TotalRet = dt['totalRet']

print('Before optimization ')
x, y = 10 , 40
f1 = -1*ts_Decay((ts_Decay(dt['close'],x)-ts_Decay(dt['vwap'],x))/dt['vwap']*(dt['high']-dt['low']),y)
f1[listed == 0] = np.nan
f1_stand = pn_TransNorm(f1.round(4))
port_pos, port_neg = get_ls_post(f1_stand.copy())
f1_stand_port = port_pos + port_neg 
[rets_both_withCost1,sr1 , ar1, to1] = get_factorRt(f1_stand_port,TotalRet,delayNum,costRate,SDate,EDate)

# After optimization 
print('After optimization ')
x = best_params["x"]
y = best_params["y"]
f2 = -1*ts_Decay((ts_Decay(dt['close'],x)-ts_Decay(dt['vwap'],x))/dt['vwap']*(dt['high']-dt['low']),y)
f2[listed == 0] = np.nan
f2_stand = pn_TransNorm(f2.round(4))
port_pos, port_neg = get_ls_post(f2_stand.copy())
f2_stand_port = port_pos + port_neg 
[rets_both_withCost2,sr2 , ar2, to2] = get_factorRt(f2_stand_port,TotalRet,delayNum,costRate,SDate,EDate)

rets_both_withCost1.cumsum().plot()
rets_both_withCost2.cumsum().plot()


# 查看样本外
SDate,EDate = '2022-01-01','2026-01-01'  # the OTS
costRate = 0.0005
delayNum = 2
TotalRet = dt['totalRet']

x, y = 10 , 40
f1 = -1*ts_Decay((ts_Decay(dt['close'],x)-ts_Decay(dt['vwap'],x))/dt['vwap']*(dt['high']-dt['low']),y)
f1[listed == 0] = np.nan
f1_stand = pn_TransNorm(f1.round(4))
port_pos, port_neg = get_ls_post(f1_stand.copy())
f1_stand_port = port_pos + port_neg 
[rets_both_withCost1,sr1 , ar1, to1] = get_factorRt(f1_stand_port,TotalRet,delayNum,costRate,SDate,EDate)

# After optimization 
print('After optimization ')
x = best_params["x"]
y = best_params["y"]
f2 = -1*ts_Decay((ts_Decay(dt['close'],x)-ts_Decay(dt['vwap'],x))/dt['vwap']*(dt['high']-dt['low']),y)
f2[listed == 0] = np.nan
f2_stand = pn_TransNorm(f2.round(4))
port_pos, port_neg = get_ls_post(f2_stand.copy())
f2_stand_port = port_pos + port_neg 
[rets_both_withCost2,sr2 , ar2, to2] = get_factorRt(f2_stand_port,TotalRet,delayNum,costRate,SDate,EDate)

rets_both_withCost1.cumsum().plot()
rets_both_withCost2.cumsum().plot()



#%% 因子组合
forms = ["-1*ts_Decay((ts_Decay(dt['close'],10)-ts_Decay(dt['vwap'],10))/dt['vwap']*(dt['high']-dt['low']),40)",
        "-1*ts_Decay(dt['vwap']/dt['close']*(dt['high']-dt['low'])/dt['close']*(dt['vol']/ts_Delay(dt['vol'],1)),10)",
        "-1*ts_Decay(dt['exRet']*(dt['vol']/ts_Delay(dt['vol'],1)),40)",
        "-1*ts_Decay(dt['exRet']*(dt['high']-dt['low'])/dt['close']*(dt['vol']/ts_Delay(dt['vol'],1)),60)",
        "-1*ts_Decay((ts_Decay(dt['close'],10)-ts_Decay(dt['vwap'],10))/dt['vwap']*(dt['high']-dt['low'])/dt['close'],20)"]

SDate,EDate = '2017-01-01','2026-01-01'  # the OTS
costRate = 0  # 单个因子测试需要加上成本来检查，组合的时候因为可以多因子组合降低还手
delayNum = 2 
TotalRet = dt['totalRet']
frs = pd.DataFrame()
fvs = {}
for f in forms:
    f1 = eval(f)
    f1[listed == 0] = np.nan
    f1_stand = pn_TransNorm(f1.round(4))
    port_pos, port_neg = get_ls_post(f1_stand.copy())
    f1_stand_port = port_pos + port_neg 
    [rets_both_withCost,sr , ar, to] = get_factorRt(f1_stand_port,TotalRet,delayNum,costRate,SDate,EDate)
    frs[f] = rets_both_withCost
    fvs[f] = f1_stand_port


frs_IS = frs.loc[SDate:'2022-01-01']
frs_IS.cumsum().plot(legend=False)
ars_IS = frs_IS.mean()*250
srs_IS = frs_IS.mean() / frs_IS.std() * (250)**0.5 
print(ars_IS)
print(srs_IS)


#%% 简单因子组合
def get_compFactor(fvs,weights):
    factorName = list(fvs.keys())
    out = fvs[factorName[0]].copy().fillna(0)* 0   # initital
    for v in factorName:
        out = out + fvs[v].fillna(0) * weights[v]  # value * wgt
    f1_stand = pn_TransNorm(out.round(4))
    port_pos, port_neg = get_ls_post(f1_stand.copy())
    f1_stand_port = port_pos + port_neg 
    return f1_stand_port

equal_weight = pd.Series(1/len(fvs.keys()),index = fvs.keys())
cf_equal = get_compFactor(fvs,equal_weight)
cf_ar = get_compFactor(fvs,ars_IS/ars_IS.sum())
cf_sr = get_compFactor(fvs,ars_IS/srs_IS.sum())

SDate,EDate = '2017-01-01','2026-01-01' 
fr_comps = pd.DataFrame()
[fr_comps['rets_equal'],sr , ar, to] = get_factorRt(cf_equal,TotalRet,delayNum,costRate,SDate,EDate)
[fr_comps['rets_ar'],sr , ar, to] = get_factorRt(cf_ar,TotalRet,delayNum,costRate,SDate,EDate)
[fr_comps['rets_sr'],sr , ar, to] = get_factorRt(cf_sr,TotalRet,delayNum,costRate,SDate,EDate)
fr_comps.loc[SDate:'2022-01-01'].cumsum().plot()
plt.title('In sample compare')
plt.show()

fr_comps.loc['2022-01-01':EDate].cumsum().plot()
plt.title('out of sample compare')
plt.show()

#%% 因子相关性
CorrRet = frs_IS.corr()

fvs_IS = pd.DataFrame()
for v in fvs.keys():
    fvs_IS[v] = fvs[v].loc[SDate:'20220101'].stack()

CorrVal = fvs_IS.corr()

print('factor correlation')
print(CorrRet.round(3).values)
print(CorrVal.round(3).values)



#%% 马科维茨方法

import scipy.optimize as sco

def Markowitz(A_return,A_cov):
    # A_return = retLs.mean()
    # A_cov = retLs.cov().to_numpy()
    def sharp(w):
        Rf = 0.00
        Rp_opt = np.sum(np.dot(w, A_return))
        Vp_opt = np.sqrt(np.dot(np.dot(w, A_cov), w.T))
        SR = (Rp_opt-Rf)/Vp_opt
        return (-SR)
    # optimazing constrain:  sum(weight ) = 1
    cons =  ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})    
    bnds = tuple((0, 1) for x in range(len(A_return)))   # ***  0
    result_sr = sco.minimize(sharp, len(A_return) * [1.0 / len(A_return), ], method='SLSQP', bounds=bnds,
                                          constraints=cons)
    w_mar = result_sr.x
    return  pd.Series(w_mar,index = A_return.keys())

w_mark = Markowitz(frs_IS.mean(), frs_IS.cov().to_numpy())
print(w_mark)
cf_mark = get_compFactor(fvs,w_mark)
[fr_comps['rets_mark'],sr , ar, to] = get_factorRt(cf_mark,TotalRet,delayNum,costRate,SDate,EDate)

fr_comps.loc[SDate:'2022-01-01'].cumsum().plot()
plt.title('In sample compare')
plt.show()

fr_comps.loc['2022-01-01':EDate].cumsum().plot()
plt.title('out of sample compare2')
plt.show()


w_mark2 = Markowitz(frs_IS.mean(), fvs_IS.cov().to_numpy())
cf_mark2 = get_compFactor(fvs,w_mark2)
[fr_comps['rets_mark2'],sr , ar, to] = get_factorRt(cf_mark2,TotalRet,delayNum,costRate,SDate,EDate)
fr_comps.loc['2022-01-01':EDate].cumsum().plot()
plt.title('out of sample compare3')
plt.show()

print(fr_comps.loc['2022-01-01':EDate].mean() / fr_comps.loc['2022-01-01':EDate].std() * (250**0.5))