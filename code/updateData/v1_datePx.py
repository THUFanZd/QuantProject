import pandas as pd 
import os
import tushare as ts
import tools as tl


#%% 读取配置文件
config = tl.read_json_config()
# if config:
#     print("配置数据:", config)

pro = ts.pro_api(config['api']['key'])


#%% 更新交易日
data_start = '20100101'
endDate = tl.get_trade_date()

cal_date = pro.trade_cal(exchange='', start_date=data_start, end_date=endDate)
cal_date.to_pickle(config['paths']['date'])


#%% 更新px
path_px = config['paths']['px']
path_px_date = path_px + 'dates.pkl'

path_px_data_raw = path_px + 'raw//' 


if os.path.exists(path_px_date):
    dates_px = pd.read_pickle(path_px_date)
    update_dates = cal_date[cal_date['cal_date'] > dates_px['cal_date']]
else:
    update_dates = cal_date

update_dates = update_dates[update_dates['is_open'] == 1]

for date_ in update_dates['cal_date']:
    print(date_)
    path_px_data_raw_dat = path_px_data_raw + date_ + '//'
    if not os.path.exists(path_px_data_raw_dat):
        os.mkdir(path_px_data_raw_dat)
    # 基础的行情数据
    df1_ = pro.daily(trade_date= date_ )
    # 复权因子
    df2_ = pro.adj_factor(trade_date= date_ )
    # 其他日频指标
    df3_ = pro.daily_basic(ts_code='', trade_date= date_, fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe_ttm,pb,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv")
    df1_.to_pickle(path_px_data_raw_dat + 'daily.pkl')
    df2_.to_pickle(path_px_data_raw_dat + 'adj_factor.pkl')
    df3_.to_pickle(path_px_data_raw_dat + 'daily_basic.pkl')




