import pathlib
import json
from datetime import datetime, time, timedelta
import pandas as pd 

# 获取config文件
def read_json_config():
    # 构建配置文件路径
    current_dir = pathlib.Path(__file__).parent
    config_path = current_dir.parent.parent / "data" / "config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        print(f"配置文件不存在: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        return None
    except Exception as e:
        print(f"读取配置文件时出错: {e}")
        return None
    


# 获取当日日期
def get_trade_date():
    """获取交易日（以22:00为分界）"""
    now = datetime.now()
    
    # 如果当前时间小于22:00，则使用昨日
    if now.time() < time(22, 0):
        now = now - timedelta(days=1)
    
    return now.strftime('%Y%m%d')


def add_fin(balance_, income_,cash_, q,pro,today, balance_col, name):
    union_set = set(balance_['ts_code']) | set(income_['ts_code']) | set(cash_['ts_code'])
    balance_need = list(set(union_set) - set(balance_['ts_code']))
    # income_need = list(set(union_set) - set(income_['ts_code']))
    # cash_need = list(set(union_set) - set(cash_['ts_code']))
    # 如果漏了，就加上，如果确实没有，在别的地方删除这个
    b_add = []
    for code in balance_need:
        df = pro(ts_code=code, start_date='20100101', end_date=today, fields=balance_col)
        df = df[df['end_date'] == q]
        if len(df) > 0 :
            b_add.append(df)
            print(code, 'add',q,name)
        else:
            income_ = income_[~income_['ts_code'].isin([code])]
            cash_ = cash_[~cash_['ts_code'].isin([code])]
            print(code, 'delete',q,name)
    if len(b_add) > 0:
        b_add = pd.concat(b_add)
        balance_ = pd.concat([balance_, b_add],axis = 0)
    return balance_, income_,cash_


# 使用示例 
# trade_date = get_trade_date()
# print(f"交易日: {trade_date}")


# daily_basic
# close	float	当日收盘价
# turnover_rate	float	换手率（%）
# turnover_rate_f	float	换手率（自由流通股）
# volume_ratio	float	量比
# pe_ttm	float	市盈率（TTM，亏损的PE为空）
# pb	float	市净率（总市值/净资产）
# ps_ttm	float	市销率（TTM）
# dv_ratio	float	股息率 （%）
# dv_ttm	float	股息率（TTM）（%）
# total_share	float	总股本 （万股）
# float_share	float	流通股本 （万股）
# free_share	float	自由流通股本 （万）
# total_mv	float	总市值 （万元）
# circ_mv	float	流通市值（万元）