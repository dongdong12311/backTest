# -*- coding: utf-8 -*-
"""
Created on Mon May 21 13:50:41 2018

@author: Administrator
"""

from stock_database.API_TradeDays  import TDays
from abc import ABCMeta, abstractmethod
import datetime
# 用于交易的时间管理模块

class TimeModule(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def UpdateTime(self):
        
        #更新当前的时间
        
        raise NotImplementedError("Should implement UpdateTime")
        
        
        
class BackTestTimeModule(TimeModule):
    '''
    回测时间管理模块
    回测不同于实盘交易在于回测必须初始化 end 日期
    '''
    def __init__(self,logger,tradelogger,start,end):
        self.start = start
        self.tradelogger = tradelogger
        self.end = end
        self.__logger = logger
        self.timeIndex = 0
        
    def initTradeDays(self):
        
        #初始化交易日历
        td = TDays()
        
        #获取交易日期
        self.tradedays = td.GetTradeDays(self.start,self.end)        

        self.timeLength  = len(self.tradedays)
        
        self.__logger.write("交易日历初始化完成")
        self.__logger.write("开始日期： " + self.start)
        self.__logger.write("结束日期：" + self.end)
        
        if self.timeLength == 0:
            raise IndexError("初始化的日期数据有误！")
        self.today = self.tradedays[self.timeIndex][0]
        
    def todaystr(self):
        return datetime.datetime.strftime(self.today,"%Y-%m-%d")
        
    def UpdateTime(self):
        #更新日期，如果不能更新返回0 
        
        if self.timeIndex == self.timeLength-1:
            return False
        self.timeIndex+=1
        self.today = self.tradedays[self.timeIndex][0]
        s =  "当前日期" + datetime.datetime.strftime(self.today,"%Y-%m-%d")
        self.__logger.write(s)
        self.tradelogger.write(s)
        return True
            
        
        
        
        
    
    