import datetime
import pandas as pd


from utility import *
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import numpy as np
import pyqtgraph as pg
import config
from SQLserver import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, QObject

# Interchange_fees = 0.003
# QtySale = 1

# # 连接数据库 获取股票的表头信息和表内数据
# server = DataServer_Sqlite3()
# server.Sql_execution(sql="DELETE FROM \"temp\"")
# server.Sql_execution(
#     f"""INSERT INTO temp({config.tushare["Column"]}) SELECT {config.tushare["Column"]} FROM "stock" where stock.ts_code == '000005.SZ' """)
# server.Sql_execution("select * from temp")
# server.Fetch_data()
# data = server.data  # 获取表内数据
# Data = Data_convert()
# Data.Transfer_data_form(data)
# datum = Data.Moving_datum


class Calculation():
    def __init__(self, datum):
        # self.amount
        self.trade_datum=datum
        self.hold_vol = 0
        self.final_amount = 0
        self.hold_amount = 100000
        self.vol_x, self.vol_y = [], []
        self.amount_x, self.amount_y = [], []
        self.earning_x, self.earning_y = [], []
        self.TradingPairList = []                       #TradingPairList，包含买卖一对交易，
        self.Buy_rec, self.Sale_rec = [], []
        des = Descison()
       
        des.runDecision(datum)                      #计算买卖点
        self.tradingPointList = des.tradingPointList       #返回买卖点列表
        self.iterator()

       
    def iterator(self):
        pass
        Index = 0
        while Index < len(self.tradingPointList):
            self.tradingPoint = self.tradingPointList[Index]
            self.Decision()
            if Index == len(self.tradingPointList) - 1:
                print(int(self.Final_amount())) # 打印最终总收益  类型--int
            Index += 1

    def Decision(self):
        # self.gainlose=[]    #ID,stock,stockcode,buydate，price，qty,amount，saledate ，qty，price,amount ，gainlose$, %
        stock_inf = [self.tradingPoint.ID, self.tradingPoint.Name, self.tradingPoint.code]
        if self.tradingPoint.Decision == 'buy':
            self.Buying()
            self.Buy_rec = [self.tradingPoint.DateToBuy, self.tradingPoint.PriceBuy, self.tradingPoint.QtyBuy,
                            self.tradingPoint.AmountBuy]

        if self.tradingPoint.Decision == "sale":
            self.Selling()
            if self.tradingPoint.ID != 1:
                gainlose = self.tradingPoint.AmountSale - self.Buy_rec[3] # AmountBuy
                if self.tradingPoint.AmountBuy == 0:
                    self.tradingPoint.AmountBuy = 1

                self.Sale_rec = [self.tradingPoint.DateToSale, self.tradingPoint.PriceSale,self.tradingPoint.QtySale,
                                     self.tradingPoint.AmountSale, gainlose, round(gainlose*100 / self.Buy_rec[3],2)]

                rec = stock_inf + self.Buy_rec + self.Sale_rec
                self.TradingPairList.append(rec)

    def Buying(self):
        trade_date = self.tradingPoint.DateToBuy
        self.avg_price = self.tradingPoint.PriceBuy
        vol=self.tradingPoint.QtyBuy
        # vol = int(self.hold_amount / (self.avg_price * 1.003))
        # cost = -(self.avg_price * 1.003) * vol
        cost=-self.tradingPoint.AmountBuy
        self.Hold_amount(trade_date, cost)
        self.Hold_vol(trade_date, vol)
        self.Earning(trade_date)

    def Selling(self):
        trade_date = self.tradingPoint.DateToSale
        self.avg_price = self.tradingPoint.PriceSale
        vol=-self.tradingPoint.QtySale
        # vol = -int(self.hold_vol * QtySale)
        # cost = (self.avg_price * 0.997) * -vol
        cost=self.tradingPoint.AmountSale
        self.Hold_amount(trade_date, cost)
        self.Hold_vol(trade_date, vol)
        self.Earning(trade_date)

    def Hold_amount(self, trade_date, cost):  # 手中持有的金额
        self.hold_amount += cost
        self.amount_x.append(trade_date)
        self.amount_y.append(self.hold_amount)

    def Hold_vol(self, trade_date, vol):  # 持有量
        self.hold_vol += vol
        self.vol_x.append(trade_date)
        self.vol_y.append(self.hold_vol)

    def Earning(self, trade_date):
        self.earning_x.append(trade_date)
        self.earning_y.append(self.hold_amount + (self.hold_vol * self.avg_price))

    def Final_amount(self):  # 最终总计金额，包括未被抛出的股票。
        self.final_amount = self.hold_amount + (self.hold_vol * self.avg_price)
        return self.final_amount


class Mat_picture(pg.GraphicsObject):

    sigMouseMoveChanged = pyqtSignal(QGraphicsSceneMouseEvent)  # 鼠标移动事件

    def __init__(self, x, y,stockHistoryDatum):
        pg.GraphicsObject.__init__(self)
        self.picture = QtGui.QPicture()
        self.stockHistoryDatum=stockHistoryDatum
        
        # self.days=config.StockDataDays
        # if len(self.data)>self.days:
        self.days=len(self.stockHistoryDatum)

        self.y = np.array(y)        
        self.plt = pg.PlotWidget()        
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        des = Descison()       
        des.runDecision(stockHistoryDatum)
        self.x = x  
        self.generatePicture(des.tradingPointList)

        xdict = []
        for i in range(self.days):
            dt = self.stockHistoryDatum[i][1]
            dt = f"{dt[0:4]}-{dt[4:6]}-{dt[6:]}"
            if i % (int(self.days / 15)) == 0 or i == range(self.days):
                xdict.append((i, dt))
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict])
        self.plt = pg.PlotWidget(axisItems={'bottom': stringaxis}, enableMenu=True)

        item = self
        self.plt.addItem(item)  

        self.plt.addItem(self.vLine, ignoreBounds=True)
        self.plt.addItem(self.hLine, ignoreBounds=True)  
           
        self.plt.setLabel('left', '收益(万)')
        self.plt.setLabel('bottom', '日 期')
        self.setFlag(self.ItemUsesExtendedStyleOption)
        self.label = pg.TextItem(text='', color=(255, 255, 255))
        self.plt.addItem(self.label)


    def generatePicture(self,tradingPoint):
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('g'))        
        prePoint = 0
        # i = 0
        
        stockHistoryRecIndex = [i for i in range(len(self.stockHistoryDatum))]
        trade_date=[i[1] for i in self.stockHistoryDatum] 
        trade_datelist = dict(zip(trade_date, stockHistoryRecIndex))

        for i in range(len(self.x)):
            t=trade_datelist[self.x[i]]
            
            if t == config.StockDataDays:
                break
            radio = 1
            yoffset = 0
            if prePoint != 0:

                if tradingPoint[i].Decision == 'buy':
                        p.setPen(pg.mkPen('g'))
                        p.setBrush(pg.mkBrush('g'))
                        # p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2) 

                        p.drawLine(QtCore.QPointF(pre_t-radio, prePoint-yoffset), QtCore.QPointF(pre_t+radio, prePoint-yoffset))
                        p.drawLine(QtCore.QPointF(pre_t, prePoint- radio-yoffset), QtCore.QPointF(pre_t, prePoint+radio-yoffset))

                if tradingPoint[i].Decision == "sale":
                        p.setPen(pg.mkPen('r'))
                        p.setBrush(pg.mkBrush('r'))
                        # p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2)
                        p.drawLine(QtCore.QPointF(pre_t-radio, prePoint-yoffset), QtCore.QPointF(pre_t+radio, prePoint-yoffset))
                        p.drawLine(QtCore.QPointF(pre_t, prePoint- radio-yoffset), QtCore.QPointF(pre_t, prePoint+radio-yoffset))

                if tradingPoint[i].Decision == "sale" and self.y[i]>self.y[i-1]:              #盈利为红线 
                        p.setPen(pg.mkPen('r'))
                        p.setBrush(pg.mkBrush('r'))
                        p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))
                
                if tradingPoint[i].Decision == "sale" and self.y[i]<=self.y[i-1]:           #亏损为绿线
                        p.setPen(pg.mkPen('g'))
                        p.setBrush(pg.mkBrush('g'))                       
                        p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))
                
                        # # p.setPen(pg.mkPen('r'))
                        # # p.setBrush(pg.mkBrush('r'))
                        # p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2)
                
                # if tradingPoint[i].Decision == "sale":
                #         p.setPen(pg.mkPen('r'))
                #         p.setBrush(pg.mkBrush('r'))
                #         p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2)


                #         p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))


                #         # p.setPen(pg.mkPen('r'))
                #         # p.setBrush(pg.mkBrush('r'))
                #         p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2)
                
                # p.setPen(pg.mkPen('g'))
                # p.setBrush(pg.mkBrush('g'))

                # p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))

                # p.setPen(pg.mkPen('r'))
                # p.setBrush(pg.mkBrush('r'))
                # p.drawEllipse(pre_t-1, prePoint-1, 1 * 2, 1 * 2)

            pre_t=t
            prePoint = self.y[i]/10000
            # i =i+1

        i = 0
        radio = 1
        yoffset = 5
        for td in trade_date :
            if prePoint != 0:
                if td == tradingPoint[i].DateToBuy or td == tradingPoint[i].DateToSale:
                    if tradingPoint[i].Decision == 'buy':
                        p.setPen(pg.mkPen('r'))
                        p.setBrush(pg.mkBrush('r'))
                        p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))
                    elif tradingPoint[i].Decision == "sale":
                        p.setPen(pg.mkPen('g'))
                        p.setBrush(pg.mkBrush('g'))
                        p.drawLine(QtCore.QPointF(pre_t, prePoint), QtCore.QPointF(t, self.y[i]/10000))
                    
            pre_t=t
            prePoint = self.y[i]/10000
            if len(tradingPoint) - 1 != i:
                i += 1
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
    def onLClick(self, pos):
        x = pos.x()
        y = pos.y()
        self.vLine.setPos(pos.x())
        self.hLine.setPos(pos.y())
# 手动重画
    # ----------------------------------------------------------------------
    def update(self):
        if not self.scene() is None:
            self.scene().update()

    def mousePressEvent(self, event):
        pos = event.scenePos()
        # if event.button() == QtCore.Qt.RightButton:
        #     self.onRClick(event.pos())
        # elif event.button() == QtCore.Qt.LeftButton:
        #     self.onLClick(event.pos())

    def mouseMoveEvent(self, event):
        pos = event.pos()
        index = int(pos.x())
        xdate = self.stockHistoryDatum[index][1]
        y= 0
        if xdate in self.x and 0 < index < self.days:
            list = dict(zip(self.x, self.y))
            y = list[xdate]/10000
            self.vLine.setPos(pos.x())
            self.hLine.setPos(y)

            a = f"日期: {xdate} \r\n  累计盈利: {int(y)} 万元  "
            self.label.setText(a)
            self.label.setPos(pos.x(), pos.y())

        else:
            self.vLine.setPos(pos.x())
            # self.hLine.setPos(pos.y())

        self.sigMouseMoveChanged.emit(event)

# if __name__ == '__main__':
#     list = Calculation(datum)
#     Mat_picture(list.earning_x, list.earning_y)
