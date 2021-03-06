#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:lucky,time:2019-06-10

import configparser
import config as cfg
from configobj import ConfigObj

#config.py 与config.ini 之间相互转换
class config():    
    def __init__(self):
        # global Stock_list
        cfg1 = "config.ini"
        self.conf = ConfigObj(cfg1,encoding='utf-8')
        self.Stock_list=[]
        self.interestingStockList=[]
        self.recommendStock=[]
        self.dbPath=''
        self.StockDataDays=0
        # self.write_Config_py_To_ini()  
        self.readConfigIni()  
             

    # def write_Config_py_To_ini(self):
        
    #     self.conf['Stock_list']= self.Stock_list
    #     self.conf['interestingStockList']= self.interestingStockList
    #     self.conf['recommendStock']= self.recommendStock
    #     self.conf['tushare']= self.tushare

    #     self.conf['Path']['dbPath']= self.dbPath
    #     self.conf['Parameter']['StockDataDays']= self.StockDataDays

    #     self.conf.write()
    
    def readConfigIni(self):
        
        self.Stock_list=self.conf['Stock_list']
        self.interestingStockList=self.conf['interestingStockList']
        self.recommendStock=self.conf['recommendStock']
        self.tushare=self.conf['tushare']

        self.dbPath=self.conf['Path']['dbPath']
        self.StockDataDays=self.conf['Parameter']['StockDataDays']

    def writeConfigIni(self):
        
        self.conf['Stock_list']= self.Stock_list
        self.conf['interestingStockList']= self.interestingStockList
        self.conf['recommendStock']= self.recommendStock
        self.conf['tushare']= self.tushare

        self.conf['Path']['dbPath']= self.dbPath
        self.conf['Parameter']['StockDataDays']= self.StockDataDays

        self.conf.write()

# if __name__ == '__main__':
#     c=config()
       