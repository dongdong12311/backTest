# -*- coding: utf-8 -*-
"""
Created on Mon May 21 15:29:05 2018

@author: Administrator
"""


from abc import ABCMeta, abstractmethod

# 用于交易的时间管理模块

class TimeModule(object):
    def UpdateTime(self):
        raise NotImplementedError("Should implement UpdateTime")
        
class B(TimeModule):
    def __init__(self):
        pass

#必须实现pay方法,否则报错NotImplementedError
    # def pay(self):
    #     print("ApplePay pay")

a=B()