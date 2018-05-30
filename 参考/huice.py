# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 19:57:15 2017

@author: Administrator
"""

import pandas as pd
from dateutil.parser import parse
import os
import datetime
import sys
import numpy as np
import tdays as td
try:
    import information as In
except:
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    os.chdir(dirname)
    import information as In
import pickle
import logging
from RZRQ import RZRQ
logger = logging.getLogger()
logger.setLevel(0)
fh = logging.FileHandler('example.txt', mode='w')
formatter = logging.Formatter(' %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# logging.disable(logging.INFO)


class Engine():
    def __init__(self, year, source):
        self.td = td.TDays()
        self.RZRQ = RZRQ().getcode()
        self.data = {}
        self.year = year
        self.debt = 1
        self.source = os.path.join(
            source, self.year + '.pkl')
        self.start = parse(self.year + '0101')
        self.end = parse(self.year + '1231')
        self.tradeday = self.td.getdata(self.start, self.end)
        self.money = 1000000
        logger.info('初始资金:' + str(self.money))
        # code buytime  cost  rate  持仓数量
        self.position = {}
        pkl_file = open(self.source, 'rb')
        self.data = pickle.load(pkl_file)
        info = self.year + '年数据加载完毕,' + '数据源:' + str(self.source) + '\n'
        logger.info(info)
        pkl_file.close()
        self.dates = list(self.data.keys())
        self.num = len(self.dates)
        self.dates.sort()
        self.index = 0
        self.date = self.dates[self.index]
        logger.info(self.date)

    def nextday(self):
        self.index = self.index + 1
        self.date = self.dates[self.index]
        logger.info('\n' + self.date)
        for code in self.position.keys():
            self.position[code]['inposition_day'] += 1

    def buy(self, code, price, money=50000, tradeside=1):
        if code in self.position.keys():
            info = code + ' 已经存在'
            logger.info(info)
            return
        if self.money < money:
            logger.info('金钱不足，当前金钱:' + str(self.money))
        if tradeside == -1 and (self.money - self.debt) / (self.debt + 1) < 2.3:
            logger.info('保证金不足，当前负债:%.2f\n\t当前金钱:%.2f' %
                        (self.debt, self.money))
            return
        amount = (money // price // 100) * 100
        if amount <= 0:
            return
        self.money = self.money - amount * price * tradeside
        self.position[code] = {'date': self.date,
                               'price': price, 'rate': 0,
                               'amount': amount, 'now_price': self.getClose(code),
                               'tradeside': tradeside,
                               'inposition_day': 1}
        if tradeside == 1:
            logger.info('买入:%s\t  买入数量:%d\t买入价格:%.2f\t资金剩余%d' %
                        (code, amount, price, self.money))
        else:
            logger.info('卖空:%s\t  卖空数量:%d\t卖空价格:%.2f\t资金剩余%d' %
                        (code, amount, price, self.money))

    def getClose(self, code):
        return self.data[self.date].loc[code]['CLOSE']

    def sell(self, code, price=0):
        if price == 0:
            try:
                price = self.getClose(code)
            except:
                logger.info(code + '\t当天停牌,不能交易')
                return
        amount = self.position[code]['amount']
        chenben = self.position[code]['price']
        tradeside = self.position[code]['tradeside']
        change = (price - chenben) / chenben * 100 * tradeside
        self.money = self.money + amount * price * tradeside
        if tradeside == 1:
            logger.info('卖出:%s\t  卖出数量%d\t成本价格%.2f\t卖出价格%.2f\t资金剩余%d\t浮动盈亏%.2f%%' %
                        (code, amount, chenben, price, self.money, change))
        else:

            logger.info('平仓:%s\t  买入数量%d\t成本价格%.2f\t买入价格%.2f\t资金剩余%d\t浮动盈亏%.2f%%' %
                        (code, amount, chenben, price, self.money, change))

        del self.position[code]

    def ShowPosition(self):
        logger.info('剩余资金：' + str(self.money))
        keys = self.position.keys()
        if len(keys) == 0:
            return
        logger.info('当前的持仓为: ')
        s = '%.10s\t%.10s\t%.4s\t%.4s\t%4.4s%%\t%s  %s  %s'
        logger.info(s %
                    ('代码     ', '购买日期', '成本', '现价', '浮动盈亏', '持仓数量', 'tradeside', '持仓天数'))
        s = '%.10s\t%.10s\t%.2f\t%.2f\t%8.2f%%\t%  d\t%5d\t\t%d'
        self.debt = 1
        for index, value in self.position.items():
            logger.info(s %
                        (index, value['date'], (value['price']),
                         value['now_price'], value['rate'] * 100,
                            value['amount'], value['tradeside'], value['inposition_day']
                         ))

            if value['tradeside'] == -1:
                self.debt = self.debt + \
                    value['now_price'] * value['amount']
        logging.info('今日负债数量:%.2f\n' % (self.debt))

    def refresh_after_close(self):
        for code in self.position.keys():
            try:
                price = self.data[self.date].loc[code]['CLOSE']
            except:
                logger.info(code + '\t当天停牌')
                continue
            self.position[code]['now_price'] = price
            chenben = self.position[code]['price']
            tradeside = self.position[code]['tradeside']
            self.position[code]['rate'] = (
                (price - chenben) / chenben) * tradeside

    def trick_TURN_RATE(self):
        temp = self.data[self.date]
        ss = temp[temp['TURN'] > 10]
        ss = ss[(ss['PCT_CHG'] > -9.75) & (ss['PCT_CHG'] < 9)]
        for code in ss.index:
            if code in self.RZRQ:
                price = ss.loc[code]['CLOSE']
                self.buy(code, price, tradeside=-1)

    def Zhisun(self):
        a = list(self.position.keys())
        for code in a:
            if abs(self.position[code]['rate']) >= 0.8:
                self.sell(code)

    def trick_HIGH_OPEN_LOW_CLOSE(self):
        if self.index == 0:
            return
        global ss
        ss = self.data[self.date]
        ss = ss[(ss['PCT_CHG'] < 9.75) & (ss['PCT_CHG'] > -9.75)]
        ss = ss[(ss['PCT_CHG'] > 2) & (ss['HIGH'] > ss['CLOSE']
                                       * 1.01) & (ss['OPNE'] > ss['CLOSE'])]
        for code in ss.index:
            if code in self.RZRQ:
                price = ss.loc[code]['CLOSE']
                self.buy(code, price, tradeside=-1)

    def SellALL(self):
        a = list(self.position.keys())
        for code in a:
            self.sell(code)
        self.debt = 0
        logger.info('资金剩余:%.2f' % (self.money))
        logger.info('负债:' + str(self.debt))


if __name__ == '__main__':
    a = Engine('2015', 'tusharedata_sliceDataset')
    for i in range(a.num - 1):
        if i % 20 == 0:
            a.SellALL()
        a.trick_HIGH_OPEN_LOW_CLOSE()
        a.Zhisun()
        a.refresh_after_close()
        a.ShowPosition()
        a.nextday()

    a.refresh_after_close()
    a.SellALL()
    a.ShowPosition()
    logging.shutdown()
