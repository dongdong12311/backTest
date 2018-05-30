# -*- coding: utf-8 -*-
"""
Created on Mon May 21 14:20:29 2018

@author: Administrator
"""
import logging
import os 
class BacktestTxt:
    def __init__(self,name):
        name = os.path.join("回测报告",name)
        self.file = open(name,'w')
    def write(self,s):
        self.file.write(s)
        self.file.write('\n')
    def __del__(self):       
        self.file.close()
class BacktestLogger:
    def __init__(self,name):
        
        self.logger = logging.getLogger()
        self.logger.setLevel(0)
        formatter = logging.Formatter(' %(message)s')
        fh = logging.FileHandler(name, mode='w')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh) 
        
    def write(self,s):
        
        self.logger.info(s)
        
    def __del__(self):
        logging.shutdown()