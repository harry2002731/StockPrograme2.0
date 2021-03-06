import config
from Fetch_stock_data import *
from utility import *

class DataFacory():

    def __init__(self):
        self.stockName=''
        self.stockCode=''
        self.stockHistoryDatum_Webdata=[]    #网络爬取的数据
        self.stockHistoryDatum=[]             #转换后的股票历时交易数据，开收盘价、成交量等
        self.stockHistoryDatumHeader=[]       #数据表头
        self.stockTradingDatum=[]        #交易日期列表
        self.stockHistoryMovingDatum=[]          #移动平均线数据
        self.stockHistoryDesDatum=[]         #决策后数据 买卖点，日期，交易数量

        self.StockList_interesting=[]       #自选股列表
        self.StockList_SH=[]                 #A股列表
        self.StockList_SZ=[]                 #深圳股列表
        self.StockList_H=[]                 #H股列表 港股
        self.StockList_Ind=[]               #指数列表

                
        self.ChartCandleDatum=[]             #蜡烛图数据
        self.ChartAmountDatum=[]             #成交量数据
        self.ChartGainLoseDatum=[]           #收益图数据

    def setStockName(self,stockName):       #设置股票名称
        self.stockName=stockName
        self.stockCode=config.Stock_list[stockName]

    def setStockCode(self,stockCode):       #设置股票名称
        self.stockCode=stockCode       
        k=config.Stock_list.keys()
        v=config.Stock_list.values()
        new=dict(zip(v,k))
        self.stockName=new[stockCode]

    def fillSqlData(self):        #返回SQL数据，数据表头
        server = DataServer_Sqlite3()
        server.Connecting_database()
        server.Sql_execution(sql="DELETE FROM \"temp\"")
        server.Sql_execution(
            f"""INSERT INTO temp({config.tushare["Column"]}) SELECT {config.tushare["Column"]} FROM "stock" where stock.ts_code == '{self.stockCode}' """)
        server.Sql_execution("select * from temp")
        server.Fetch_data()
        self.stockHistoryDatum_Webdata = server.data  # 获取表内数据
        
        Header = []                           # 获取表头信息
        for index in server.header:
            Header.append(index[0])
        
        self.stockHistoryDatumHeader = Header  

    def FillAnalysisData(self):
        data=self.stockHistoryDatum_Webdata
        
        t = 0
        for (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount, avgprice, avg5day,
                avg10day, avg20day, avg60day) in data:
            All_datum = (str(ts_code), str(trade_date), float(open), float(close), float(low), float(high),float(vol),float(change),float(pct_chg), float(pre_close), float(amount)), float(avgprice), float(avg5day), float(avg10day), float(avg20day), float(avg60day)
            Candle_datum = (int(t), str(trade_date), float(open), float(close), float(low), float(high),float(avgprice),float(avg5day), float(avg10day), float(avg20day), float(avg60day))
            Moving_datum = [str(ts_code), str(trade_date), float(avgprice), float(avg5day), float(avg10day)]
            Amount_datum = (int(t), str(trade_date), float(open), float(close), float(vol))

            self.stockHistoryDatum.append(All_datum)
            self.ChartCandleDatum.append(Candle_datum)
            self.stockHistoryMovingDatum.append(Moving_datum)
            self.ChartAmountDatum.append(Amount_datum)
            t += 1
    
    def FillDecisionData(self):
        self.stockHistoryDesDatum= Calculation(self.stockHistoryMovingDatum)        #决策后数据 买卖点，日期，交易数量
        a=0
    def GetDecisionList(self)->list:
        pass






class Trading():                #交易类
    def __init__(self):
        self.stockName=''       #股票名称
        self.stockCode=''       #股票代码
        self.TradingList=[]     #交易记录 append TradingRec
    
    def Buy(self,stockName,price,qty):
        rec=TradingRec()
        rec.stockName=stockName
        rec.stockCode=config.Stock_list[stockName]
        rec.price=price
        rec.qty=qty
        self.TradingList.append(rec)
        return rec

    def Sale(stockName,price,qty):
        rec=TradingRec()
        rec.stockName=stockName
        rec.stockCode=config.Stock_list[stockName]
        rec.price=price
        rec.qty=qty
        self.TradingList.append(rec)
        return rec

    def TradingRecToList(Tradingrec):
        rec=Trading()
        rec=Tradingrec
        list=[
            rec.stockName,
            rec.stockCode,
            rec.tradingDate,
            rec.tradingName,
            rec.price,
            rec.qty,
            rec.amount,
            rec.status,
            rec.account,
            ]
        
        return list



class EvaluateGainLose():                                   #收益评估
    def __init__(self):  
        self.DecisionList=[]
        self.Decision_gainList=[]                                    #盈利
        self.Decision_loseList=[]                                    #损失
        self.MaxGain=''                                     #最大收益
        self.MinGain=''                                     #最小收益

    def append(Decision):
        self.DecisionList.append(Decision)



class Calculation():
    def __init__(self, datum):
        # self.amount
        self.datum=datum
        self.hold_vol = 0
        self.final_amount = 0
        self.hold_amount = StockAcount().initInvestAmount *StockAcount().unitRedio
        # self.trade_datum = []
        # self.Buy_rec, self.Sale_rec = [], []
        self.Descison = Descison()                              #创建决策
        self.Descison.runDecision(datum)          #根据移动平均线计算买卖点 返回交易点
        self.tradingPointList = self.Descison.tradingPointList


    # def Decision(self):
    #     stock_inf = [self.tradingPoint.ID, self.tradingPoint.Name, self.tradingPoint.code]
    #     if self.tradingPoint.Decision == 'buy':
    #         self.Buying()
    #         self.Buy_rec = [self.tradingPoint.DateToBuy, self.tradingPoint.PriceBuy, self.tradingPoint.QtyBuy,
    #                         self.tradingPoint.AmountBuy]


    #     if self.tradingPoint.Decision == "sale":
    #         self.Selling()
    #         if self.tradingPoint.ID != 1:
    #             gainlose = self.tradingPoint.AmountSale - self.Buy_rec[3] # AmountBuy
    #             if self.tradingPoint.AmountBuy == 0:
    #                 self.tradingPoint.AmountBuy = 1

    #             self.Sale_rec = [self.tradingPoint.DateToSale, self.tradingPoint.PriceSale,self.tradingPoint.QtySale,
    #                                  self.tradingPoint.AmountSale, gainlose, round(gainlose*100 / self.Buy_rec[3],2)]
                   
    #             rec = stock_inf + self.Buy_rec + self.Sale_rec
    #             self.trade_datum.append(rec)

    # def Buying(self):
    #     trade_date = self.tradingPoint.DateToBuy
    #     self.avg_price = self.tradingPoint.PriceBuy
    #     vol=self.tradingPoint.QtyBuy
    #     # vol = int(self.hold_amount / (self.avg_price * 1.003))
    #     # cost = -(self.avg_price * 1.003) * vol
    #     cost=-self.tradingPoint.AmountBuy
    #     self.Hold_amount(trade_date, cost)
    #     self.Hold_vol(trade_date, vol)
    #     self.Earning(trade_date)

    # def Selling(self):
    #     trade_date = self.tradingPoint.DateToSale
    #     self.avg_price = self.tradingPoint.PriceSale
    #     vol=-self.tradingPoint.QtySale
    #     # vol = -int(self.hold_vol * QtySale)
    #     # cost = (self.avg_price * 0.997) * -vol
    #     cost=self.tradingPoint.AmountSale
    #     self.Hold_amount(trade_date, cost)
    #     self.Hold_vol(trade_date, vol)
    #     self.Earning(trade_date)

    # def Hold_amount(self, trade_date, cost):  # 手中持有的金额
    #     self.hold_amount += cost
    #     self.amount_x.append(trade_date)
    #     self.amount_y.append(self.hold_amount)

    # def Hold_vol(self, trade_date, vol):  # 持有量
    #     self.hold_vol += vol
    #     self.vol_x.append(trade_date)
    #     self.vol_y.append(self.hold_vol)

    # def Earning(self, trade_date):
    #     self.earning_x.append(trade_date)
    #     self.earning_y.append(self.hold_amount + (self.hold_vol * self.avg_price))

    # def Final_amount(self):  # 最终总计金额，包括未被抛出的股票。
    #     self.final_amount = self.hold_amount + (self.hold_vol * self.avg_price)
    #     return self.final_amount


   

class TradingHistory():
    def __init__(self):
        self.TradingList=[]


    def load():                                     #从数据库加载历史交易记录
        pass

    
    def append(self,tradingRec):
        self.TradingList.append(tradingRec)    





if __name__ == '__main__':
    df=DataFacory()
    df.stockName='东山精密'
    df.stockCode=config.Stock_list[df.stockName]  
    df.fillSqlData()                              #从数据库读取数据
    df.FillAnalysisData()                         #生成图表及分析数据
   
    df.FillDecisionData()



    # app = QtWidgets.QApplication(sys.argv)
    # window = Main()
    # window.show()
    # sys.exit(app.exec_())