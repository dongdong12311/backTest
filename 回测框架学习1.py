# -*- coding: utf-8 -*-
"""
Created on Wed May 16 14:16:46 2018

@author: Administrator
"""

# Declare the components with respective parameters


from queue import Queue
from Logger import BacktestLogger
from Strategy import RandomStrategy
from TimeModule import BackTestTimeModule
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler
#from DataHandler import BackTestDataHandler
from Market import BackTestMarket



events = Queue()
start = '2016-01-01'
end = '2017-01-10'

#管理日志
backtestlogger =  BacktestLogger('回测记录.txt')
tradelogger = BacktestLogger('交易记录.txt')

#管理交易日历
timemodule = BackTestTimeModule(backtestlogger,start,end)
timemodule.initTradeDays()

# 管理市场信息
market = BackTestMarket(backtestlogger,tradelogger,timemodule,events)
market.initdata()


# 策略模块
strategy = RandomStrategy(backtestlogger,market,events)

# 持仓模块
portfolio = NaivePortfolio(backtestlogger,market,events)

# 执行模块
excution = SimulatedExecutionHandler(backtestlogger,events)

print("start")

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    market.update()
    if market.cotinue_backtest == False:
        break
    # Handle the events
 
    while True:
        # 获取待处理的事件，如果队列空就结束循环
        if  events.qsize() == 0:
            break
        else:
            event = events.get(False)
        
        # 计算信号    
        if event.type == 'MARKET':
            strategy.calculate_signals(event)
        # 产生信号
        elif event.type =='SIGNAL':
            portfolio.update_signal(event)
        # 执行订单
        elif event.type =='ORDER':   
            excution.execute_order(event)
        # 更新持仓
        elif event.type == 'FILL':
            portfolio.update_fill(event) 

            
    #一天结束了 我们要更新持仓一下
    portfolio.update_after_close()
    
    #看看持仓吧~
    portfolio.ShowPosition()            

backtestlogger.delete()
tradelogger.delete()