import pandas as pd 
import os
import tushare as ts
import tools as tl



#%%
'''
缺： 财报预告数据，业绩快报，分红送股
'''

#%% 读取配置文件
config = tl.read_json_config()
# if config:
#     print("配置数据:", config)

pro = ts.pro_api(config['api']['key'])

sw1 = pro.index_classify(level='L1', src='SW2021')
swhy = []
for v in sw1['index_code']:
    df = pro.index_member_all(l1_code=v)
    swhy.append(df)
sw21hy = pd.concat(swhy)
sw21hy = sw21hy[sw21hy['is_new'] == 'Y']
sw21hy.to_pickle(config['paths']['hy'] + 'sw21.pkl')
sw21hy.to_csv(config['paths']['hy'] + 'sw21.csv')


#%% 按照px里面的格式，把数据matrix化
pxIndex = pd.read_pickle(config['paths']['px'] + 'matrix//close.pkl')
pxIndex = pxIndex.fillna(0) * 0

for c in pxIndex.columns:
    if c in list(sw21hy['ts_code']) :
        print(c)
        hy_code = (sw21hy[sw21hy['ts_code'] == c])['l1_code'].values[0]
        pxIndex[c] = int(hy_code[:6])

pxIndex.to_pickle(config['paths']['hy'] + 'matrix//sw21l1.pkl')
pxIndex.to_csv(config['paths']['hy'] + 'matrix//sw21l1.csv')

