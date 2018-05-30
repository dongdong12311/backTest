# -*- coding: utf-8 -*-
"""
Created on Mon May 21 15:10:58 2018

@author: Administrator
"""
import sys
import datetime
import pandas as pd
from stock_database.API_winddata_slice import WindData_sliceDB 
from event import MarketEvent
class Market:
    def __init__(self):
        pass
    


class BackTestMarket(Market):
    def __init__(self,logger,timemodule,events):
        self.timemodule = timemodule
        self.events = events
        self.cotinue_backtest = True
        self.__logger = logger
        self.data = {}

    def todaystr(self):
        return self.timemodule.todaystr()
    
    def todaydatetime(self):
        return self.timemodule.today
    
    def bar(self,num, total):
        alls = 50
        rate = float(num) / total
        rate_num = int(rate *alls)
        r = '\r%.2f%% |%s%s|'% (rate*100,"■"*(rate_num)," "*(alls-rate_num))
        print(r,end='')
        
    def initdata(self):
        self.db = WindData_sliceDB()
        # 初始化交易数据 
        # 类型：字典
        #获取所有 start 到 end 的交易日数据
        print("回测进度：")
        total = len(self.timemodule.tradedays)  
        for i,date in enumerate(self.timemodule.tradedays):
            self.bar(i+1,total)
            date = date[0]
            datestr = datetime.datetime.strftime(date,"%Y-%m-%d")
            self.data[date] = pd.DataFrame(list(self.db.readData(datestr)))
            
            self.data[date].columns=['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'CHG', 'PCT_CHG',
                           'ADJFACTOR', 'TURN', 'VOL_RATIO', 'INDUSTRY_CSRC12', 'FREE_TURN',
                           'PE_TTM', 'PB_LF', 'CODE']
            self.data[date].index=self.data[date]['CODE']
        print("\n正在进行计算...")
        
    def update(self): 
        self.cotinue_backtest = self.timemodule.UpdateTime()
        if self.cotinue_backtest:
            marketevent = MarketEvent()
            self.events.put(marketevent)
            
    def todayData(self,N=1):
        return self.data[self.timemodule.today]
        
    