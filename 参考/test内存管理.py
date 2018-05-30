# -*- coding: utf-8 -*-
"""
Created on Thu May 17 10:31:30 2018

@author: Administrator
"""
import pandas as pd
class A:
    def __init__(self,bigdata):
        self.bigdata = bigdata
        print(id(self.bigdata))
        
bigdata = pd.DataFrame([range(1,1000)])
print("bigdata的内存地址为" )
print(id(bigdata))
a = A(bigdata)