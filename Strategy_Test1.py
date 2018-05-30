# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:59:55 2018

@author: Administrator
"""
import random
from Strategy import Strategy
from event import SignalEvent

#测一只股票 买入 卖出
class Test1(Strategy):
    #策略模块生成随机数然后买入
    def __init__(self,logger,Market,events):
        self.__logger = logger 
        self.__market = Market
        self.__data = self.__market.data
        self.__events = events
        # 随机初始化一个股票进行购买
        n = random.randint(1,1000)
        self.code = self.__data[self.__market.todaydatetime()]['CODE'][n]
    def calculate_signals(self,event):
        if event.type == 'MARKET':
            temp = self.__data[self.__market.todaydatetime()]
            self.tradeside = 1
            # 记录到日志
            try:
                price = temp.loc[self.code]['CLOSE']
            except:
                return 
            #self.__logger.write("买入%s"%(code))
            signal = SignalEvent(self.code,self.__data,100,price, self.tradeside)
            self.__events.put(signal)      
            signal = SignalEvent(self.code,self.__data,100,price, -self.tradeside)
            self.__events.put(signal)
            
class RandomStrategy(Strategy):
    
    #策略模块生成随机数然后买入
    def __init__(self,logger,Market,events):
        self.__logger = logger 
        self.__market = Market
        self.__data = self.__market.data
        self.__events = events
        n  = 2
        self.code = self.__data[self.__market.todaydatetime()]['CODE'][n]
    def calculate_signals(self,event):
        if event.type == 'MARKET':
            temp = self.__market.todayData()
            if random.randint(1,100) > 50:
                tradeside = 1
            else:
                tradeside = -1
            # 记录到日志
            price = temp.loc[self.code]['CLOSE']
            #self.__logger.write("买入%s"%(code))
            signal = SignalEvent(self.code,self.__data,100,price,tradeside)
            self.__events.put(signal)
