# -*- coding: utf-8 -*-
"""
Created on Tue May 22 17:30:39 2018

@author: Administrator
"""

from abc import ABCMeta, abstractmethod
from event import OrderEvent


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        raise NotImplementedError("Should implement update_fill()")
        
        
class NaivePortfolio(Portfolio):
    """
    The NaivePortfolio object is designed to send orders to
    a brokerage object with a constant quantity size blindly,
    i.e. without any risk management or position sizing. It is
    used to test simpler strategies such as BuyAndHoldStrategy.
    """
    
    def __init__(self, logger,tradelogger,Market,events, initial_capital=1000000.0):
        self.__logger = logger 
        self.__market = Market
        self.tradelogger = tradelogger
        self.events = events
        self.__money = initial_capital
        self.today =  Market.timemodule.today
        self.__basic ={'账户余额':initial_capital,'负债金额':0}
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
    def todaystr(self):
        return self.__market.todaystr()
    def ShowPosition(self):
        n = len(self.__position.keys())

        self.__logger.write("账户明细")
        
        s = '日期： %s\t账户余额：%.2f\t负债金额：%.2f'%(self.todaystr(),self.__basic['账户余额'],self.__basic['负债金额'])
        self.__logger.write(s)
        if n == 0 :
            return 
        self.__logger.write("持仓明细：")
        self.__logger.write('%.9s\t\t%5s    %5s    %5s    %5s    %5s    %5s    %5s    %5s    '%('code',self.__position_names['code'][0],
                                                                                  self.__position_names['code'][1],
                                                                                  self.__position_names['code'][2],
                                                                                  self.__position_names['code'][3],
                                                                                  self.__position_names['code'][4],
                                                                                  self.__position_names['code'][5],
                                                                                  self.__position_names['code'][6],
                                                                                  self.__position_names['code'][7]))
        for code in self.__position:
                self.__logger.write('%.9s\t%10s    %6s\t     %2d\t   %5d\t   %5d   \t              %.2f\t     %.2f\t    %.2f'
                      %(code,
                        self.__position[code][0],
                        str(self.__position[code][1]),
                        self.__position[code][2],
                        self.__position[code][3],
                        self.__position[code][4],
                        self.__position[code][5],
                        self.__position[code][6],
                        self.__position[code][7])) 
        self.__logger.write("")
                
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            if order_event is not None:    
                self.events.put(order_event) 
            
    def generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order_type='MKT' 
        price  = signal.price
        symbol = signal.symbol
        quantity = signal.quantity
        direction = signal.direction
        
        #(symbol, order_type, quantity,price, direction)
        if price and self.__money > price*signal.quantity:
            order = OrderEvent(symbol, order_type, quantity , price ,direction)      
            return order 
        return None
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_holdings_from_fill(event)
            self.update_positions_from_fill(event)
            
    def cal_debt(self):
        debt = 0
        for code in self.__position.keys():
            if self.__position[code][3]==-1:
                debt +=self.__position[code][7]
        self.__basic['负债金额'] = debt        
    def update_after_close(self):
        self.today = self.__market.timemodule.today
        self.update_positions_from_market()
        self.cal_debt()

    def update_positions_from_market(self):
        for code in self.__position.keys():
            # 更新现在的价格
            self.__position[code][4] += 1 
            try:
                price = self.__market.data[self.today].loc[code]['CLOSE']
                self.__position[code][6] = price 
                self.__position[code][7]  = self.__position[code][2]*price
                self.__position[code][5] = self.__position[code][3]*(price - self.__position[code][1])/self.__position[code][1]*100
            except:
                pass    
            
    def update_positions_from_fill(self,event):
        # 股票代码 已经存在
        code = event.symbol
        tradeside = event.direction
        price = event.price 
        amount = event.quantity
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
            self.__position[code]=[self.todaystr(), price,amount,tradeside, 0,0.0,price,price*amount]
            
        #写日志    
        if tradeside == 1:
            self.tradelogger.write("买入%s %d股，买入价格 %.2f 市值 %.2f  资金余额 %.2f "%(code,amount,price,price*amount,self.__basic['账户余额']))
        else:
            self.tradelogger.write("卖出%s %d股  卖出价格 %.2f 市值 %.2f  资金余额 %.2f "%(code,amount,price,price*amount,self.__basic['账户余额']))
    
    def update_holdings_from_fill(self,event):
        self.__basic['账户余额'] -= event.price * event.direction * event.quantity
        return 
    