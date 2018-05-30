# -*- coding: utf-8 -*-
"""
Created on Fri May 18 10:51:27 2018

@author: Administrator
"""
from data import DataHandler,BackTestDataHandler
from Strategy import Strategy


data =  BackTestDataHandler()
while True:
    if data.continue_backtest:
       data.update()
    else:
        break
    
    