# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:07:40 2018

@author: Administrator
"""

from Market import Market 


start = '2018-01-01'
end = '2018-02-01'
market = Market()
market.init(start,end)
market.init_data() 
market.CreateAccount()

market.account.buy("600232.SH",7.62,1000)
market.account.buy("000001.SZ",12.0,1000,-1)
market.account.ShowPosition()

market.tomorrow()
market.account.ShowPosition()

market.tomorrow()
market.account.ShowPosition()
del market       
