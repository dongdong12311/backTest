# -*- coding: utf-8 -*-
"""
Created on Mon May 14 14:58:15 2018

@author: Administrator
"""
# -*- coding: utf-8 -*-
import logging
import numpy as np
import pandas as pd
import datetime
from stock_database.API_TradeDays  import TDays
from stock_database.API_winddata_slice import WindData_sliceDB
fh = logging.FileHandler('Market运行记录.txt', mode='w')
class Market:
    def __init__(self):
                
        # 初始化 日志
        
        self.logger = logging.getLogger()
        self.logger.setLevel(0)
        formatter = logging.Formatter(' %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    def init(self,start,end):    
        # 获取交易日数据
        
        td = TDays()
        self.tradedays = td.GetTradeDays(start,end)
        self.logger.info("获取交易日数据完成")
        
        
        # 市场基本信息的初始化
        self.__index  = 0 
        self.__length = len(self.tradedays)
        self.today = self.tradedays[self.__index][0] 
        self.end =  self.tradedays[-1][0]      
        self.logger.info("市场基本信息初始化完成")
        self.logger.info("开始日期：" +datetime.datetime.strftime(self.today,"%Y-%m-%d"))
        self.logger.info("结束日期：" +datetime.datetime.strftime(self.end,"%Y-%m-%d"))
    
        
        # 初始化数据库引擎
        
        self.db = WindData_sliceDB()
        self.logger.info("数据信息初始化完成")
        
        
    def init_data(self):
        
        # 初始化交易数据 
        # 类型：字典
        self.data = {}
        #获取所有 start 到 end 的交易日数据
        self.logger.info("开始数据采集")
        for date in self.tradedays:
            date = date[0]
            datestr = datetime.datetime.strftime(date,"%Y-%m-%d")
            self.data[date] = pd.DataFrame(list(self.db.readData(datestr)))
            
            self.data[date].columns=['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'CHG', 'PCT_CHG',
                           'ADJFACTOR', 'TURN', 'VOL_RATIO', 'INDUSTRY_CSRC12', 'FREE_TURN',
                           'PE_TTM', 'PB_LF', 'CODE']
            self.data[date].index=self.data[date]['CODE']
        self.logger.info("数据采集完成")

    def CreateAccount(self):
        datestr = datetime.datetime.strftime(self.today,"%Y-%m-%d")
        self.account = Account()
        self.account.init(datestr)
        
    def tomorrow(self):
        if self.__index < self.__length:
            self.__index += 1
            self.today = self.tradedays[self.__index][0]
        else:
            return 0
        self.todaystr = datetime.datetime.strftime(self.today,"%Y-%m-%d")
        self.__updateAccount()
    
    def InquirePrice(self,code,dtype='CLOSE'):
        if dtype not in ['OPEN','HIGH','LOW','CLOSE']:
            self.logger.info("查询" +code + "价格失败，输入参数为" + dtype)
            return 0
        try:
            return  self.data[self.today].loc[code][dtype]
        except:
            return 0
    def __updateAccount(self):
        dic ={}
        codes = self.account.GetCode()
        for code  in codes:
            price = self.InquirePrice(code)
            if price:
                dic[code] = price
            else:
                dic [code] = -1
        self.account.update(self.todaystr,dic)
    # 析构    
    def __del__(self):
        logging.shutdown()        
        
        
        
        
class Account(Market):
    def __init__(self):
        super(Account,self).__init__()
    def init(self,datestr,money=1000000):
        self.todaystr = datestr
        #初始化持仓记录 
        self.logger.info("持仓初始化")
        self.logger.info("当前日期：" + datestr)
        self.__basic ={'日期':datestr,'账户余额':money,'负债金额':0}
        self.__position={}
        self.__position_names={}
        self.__position_names['code']=['购买日期','购买价格',
    		               '购买数量','交易方向','持仓时间（天）',
    		               '盈亏比例','现价','市值']
        '''
        code       [0]date [1]price [2]amount  [3]tradeside 
        股票代码  购买日期  购买价格  购买数量   交易方向   
        [4]inposition_day     [5]rate      [6]now_price     [7]value                          
        持仓时间（天）         盈亏比例       现价            市值
        '''
    def buy(self,code,price,amount,tradeside=1):
        if amount<=0:
            self.logger.info("买入数量错误！ " + "要求买入" +code +str(amount) +"股")
            return -1
        if (self.__basic['账户余额'] < price*amount):
            self.logger.info("账户资金不足,账户剩余资金 " + str(self.__basic['账户余额']) +
                             " 要求买入:"+code + str(amount)+"股,现价:"+str(price)+" 总额:"+ str(amount*price))
            return -1
        # 股票代码 已经存在
        if (code in self.__position.keys()):
            # 如果交易的方向相同
            if self.__position[code][3]==tradeside:
                # 记录原始的价格
                price0 = self.__position[code][1]
                amount0 = self.__position[code][2]			            
				       # 购买的成本等于加权平均
                self.__position[code][1] = (price0*amount0+price*amount)/(amount0+amount)         
                # 购买的数量等于二者的和			
                self.__position[code][2] += amount		
            # 如果二者的交易方向不相同
            else:
                # 如果买入方向相反 并且 股票代码存在
                # 记录原始的交易信息
                price0 = self.__position[code][1]
                amount0 = self.__position[code][2]
                tradeside0 = self.__position[code][3]
                if (amount0==amount):
                    del self.__position[code]
                else:
                    # 数量等于二者加权之差
                    self.__position[code][2] = amount*tradeside + amount0*tradeside0
                    # 如果卖空大于买入
                    if self.__position[code][2]<0:
                        self.__position[code][3] = -1
                        self.__position[code][2]=-self.__position[code][2]
                    # 如果卖空小于买入
                    else:
                        self.__position[code][3] = 1
        else:
            # 股票代码不存在则创建
            self.__position[code]=[self.__basic['日期'], price,amount,tradeside, 1,0.0,price,price*amount]
        # 更新账户的资金
        self.__basic['账户余额'] -= price*amount*tradeside

        if (tradeside ==  -1):
            self.__basic['负债金额'] += price *amount
        return  0
    def sell(self,code,price,amount,tradeside=1):
        #  1：卖出平仓  -1 买入平仓
        if tradeside != self.__position[code][3]:
            self.logger.info(code + "交易方向不同！")
            self.logger.info("持仓方向："+str(self.__position[code][3]))
            self.logger.info("要求交易的方向：" +str(tradeside))
            return -1            
        if amount <= 0:
            self.logger.info("卖出数量错误！ " + "要求卖出" +code +str(amount) +"股")
            return -1
        if code not in self.__position.keys() :
            self.logger.info("不存在可卖出的证券 " + code)
            return -1
        amount0 = self.__position[code][2]
        if  amount0 < amount:
            self.logger.info(code +"  可卖证券数量不足,持有 " + str(amount0) + "股, 请求卖出 " +str(amount)+" 股")
            return -1
        if amount == amount0:
            del self.__position[code]
        else:
            self.__position[code][2]-=amount
        self.__basic['账户余额'] += price*amount*tradeside
        if (tradeside ==  -1):
            self.__basic['负债金额'] -= price *amount
        return  0
    def ShowPosition(self):
        self.logger.info(" ")
        self.logger.info('日期：' +self.__basic['日期'])
        self.logger.info('账户余额：' +str(self.__basic['账户余额']))
        self.logger.info('负债金额' +str(self.__basic['负债金额']))
        self.logger.info("今日持仓明细：")
        self.logger.info('%.9s\t%5s    %5s    %5s    %5s    %5s    %5s    %5s    %5s    '%('code',self.__position_names['code'][0],
                                                                                  self.__position_names['code'][1],
                                                                                  self.__position_names['code'][2],
                                                                                  self.__position_names['code'][3],
                                                                                  self.__position_names['code'][4],
                                                                                  self.__position_names['code'][5],
                                                                                  self.__position_names['code'][6],
                                                                        self.__position_names['code'][7]))
        
        for code in self.__position.keys():
                self.logger.info('%.9s\t%10s    %.2f\t     %2d\t   %5d\t   %5d   \t              %.2f\t     %.2f\t    %.2f'
                      %(code,
                        self.__position[code][0],
                        self.__position[code][1],
                        self.__position[code][2],
                        self.__position[code][3],
                        self.__position[code][4],
                        self.__position[code][5],
                        self.__position[code][6],
                        self.__position[code][7]))

        
    # 析构    
    def __del__(self):
        logging.shutdown()
        
    #  获取持仓股票的代码    
    def GetCode(self):
        return self.__position.keys()
    
    # 查询持仓信息
    def inquire(self,code):
        if code not in  self.__position[code]:
            return {}
        return  self.__position[code]
    
    #  更新每日的持仓信息
    def update(self,todaystr,codes):
        self.__basic['日期'] = todaystr
        
        for code in codes.keys():
            # 更新持仓时间
            self.__position[code][4] += 1
            
            # 更新现在的价格
            self.__position[code][6] = codes[code]
            
            # 更新市值
            self.__position[code][7] = self.__position[code][6]*self.__position[code][2]
            
            # 更新盈亏比例
            self.__position[code][5] = (self.__position[code][6]-self.__position[code][1])/self.__position[code][1]*100
            
def main():       
    #test
    a= Account()
    a.init('2018-01-01')           
    a.buy('600232',100,100,-1)
    a.ShowPosition()
    a.buy('600232',100,200,1)
    a.buy('600232',100,200,1)
    a.buy('600232',100,200,-1)
    a.sell('600232',100,200) 
    a.ShowPosition() 
    a.sell('600232',100,300) 
    a.buy('600233',100,200,-1)
    a.buy('600233',100,200,-1)
    a.ShowPosition() 
    a.sell('600233',100,400,-1)
    
main()