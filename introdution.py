# -*- coding: utf-8 -*-
"""
Created on Tue May 29 22:19:32 2018

@author: Administrator
"""
import time
import os
class introduction:
    def __init__(self,start,end):
        os.system("cls")
        print('欢迎使用本系统')
        print("回测开始...")
        print("回测开始日期：")
        print(start)
        print("回测结束日期")
        print(end)
        print("正在读取数据...")
        self.start = time.time()
        
    def __del__(self):
        print("回测结束，共用时")
        print("%.2f秒"%(time.time()-self.start))
        print("回测报告保持在如下目录:")
        print(os.getcwd())