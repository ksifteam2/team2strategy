
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 23:19:00 2018

@author: kongms
"""
#%%
import pandas as pd
import numpy as np
import datetime as dt
from collections import OrderedDict
import utils

def big_price_dataframe(df1,df2):
    dic = {}
    df1 = df1.fillna(0)
    df2 = df2.fillna(0)
    for i in df1.columns:
        dic[i] = df1[i] < df2[i]
    big_price_firms = pd.DataFrame(dic)  
    return big_price_firms

def true_firm(bool_dataframe,from_date, to_date): #날짜는 string으로 입력
    period = bool_dataframe[from_date:to_date]
    true_firm_dict = OrderedDict()
    
    for i in range(len(period)): 
        if i == len(period) - 1 : continue
        true_firm_list = []
        for j in range(len(bool_dataframe.columns)):
            if bool_dataframe.iloc[i][j]==True:
                true_firm_list.append(bool_dataframe.columns[j])        
        #period.index = datetime.fromtimestamp(int(period.index[0]))
        #true_firm_dic[period.index[i]] = true_firm_list
        from_date = dt.datetime.strptime(str(period.index[i]), '%Y-%m-%d %H:%M:%S')
        to_date = dt.datetime.strptime(str(period.index[i+1]), '%Y-%m-%d %H:%M:%S') - dt.timedelta(days=1)
        true_firm_dict[(from_date, to_date)] = true_firm_list
        
    return true_firm_dict  
        
#컨센서스 적정주가와 종가 데이터 불러오기
consensus = './data/consensus price.csv'
df_con = pd.read_csv(consensus, index_col=0, parse_dates=[0])

closed = './data/closed price.csv'
df_real = pd.read_csv(closed, index_col=0, parse_dates=[0])

#main 함수
bool_data = big_price_dataframe(df_real, df_con)
consensus = true_firm(bool_data, '2016-01-01', '2017-12-31')
print(consensus)
utils.backtesting(consensus, './data/Adjusted Price_daily.csv')
