import sys

import tkinter
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from UIeilson import Ui_MainWindow
from Data_convert import *
# import config
from  GetConfig import config as cfg
import fuzzyfinder
from utility import *
from Gain_lose import *
from Earning_Compare import earning_Compare
from Fetch_stock_data import Fetch_stock_data
from CandlestickItem import CandlestickItem
from AmountstickItem import AmountstickItem


class Main(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        global ui,config
        ui = Ui_MainWindow()
        ui.setupUi(self)

        config=cfg()
        config.readConfigIni()

        self.setMouseTracking(True)  # 设定鼠标坐标可追踪
        ui.custom_edit.textChanged.connect(self.custom_edit_textChanged)  # 监测文本框内文字是否变化
        ui.listWidget.itemClicked.connect(self.listWidget_selectionChange)  # 股票列表点击
        ui.listWidget.itemSelectionChanged.connect(self.listWidget_selectionChange)
        ui.listWidget_2.itemClicked.connect(self.listWidget2_selectionChange)  # 自选股票列表点击
        ui.listWidget_2.itemSelectionChanged.connect(self.listWidget2_selectionChange)  # 自选股票列表点击

        ui.listWidget_4.itemClicked.connect(self.listWidget4_selectionChange)  # 推荐股票列表点击
        ui.listWidget_4.itemSelectionChanged.connect(self.listWidget4_selectionChange)  # 推荐股票列表点击

        ui.pushButton_5.clicked.connect(self.SaveInterestStockList)  # 保存自选股列表到config.ini

        ui.pushButton.clicked.connect(self.AppendToInterestStockList)  # 添加到自选股
        ui.pushButton_2.clicked.connect(self.MoveFromInterestStockList)  # 移除自选股
        ui.pushButton_3.clicked.connect(self.recommendStockCal)  # 荐股计算
        ui.pushButton_4.clicked.connect(self.OptionalStockGainLoseCal)  # 自选股收益计算

        # 添加自选股
        ui.listWidget_2.clear()
        rec = config.interestingStockList
        if rec:
            for i in range(len(rec)):
                ui.listWidget_2.addItem(list(rec.keys())[i])

        # 添加荐股清单
        rec = config.recommendStock
        if rec:
            for i in range(len(rec)):
                ui.listWidget_4.addItem(list(rec.keys())[i])

        # 添加股票代码
        rec = config.Stock_list
        if rec:
            for i in range(len(rec)):
                ui.listWidget.addItem(list(rec.keys())[i])

        root = tkinter.Tk()  # 创建一个Tkinter.Tk()实例
        root.withdraw()  # 将Tkinter.Tk()实例隐藏

        """header 表头  stock_data 数据类型 int(t), str(trade_date), float(open), float(close), float(low),
        float(high), float(vol), float(change), float(pct_chg)) """

    def SaveInterestStockList(self): #保存自选股列表到config.ini
        
        config.writeConfigIni()




    def MyMouseEvent(self, event):
        pos = event.pos()
        self.d.vLine.setPos(int(pos.x()))
        self.cdst.vLine.setPos(int(pos.x()))

    # 自选股收益计算
    @staticmethod
    def recommendStockCal():
        ec = earning_Compare()
        db = ec.CalculateForspecStock(config.recommendStock)
        ui.listWidget_3.clear()
        for i in range(len(db)):
            sumlist = db[i][0]
            detail = db[i][1]
            ui.listWidget_3.addItem("-" * 20)
            ui.listWidget_3.addItem(f"{detail[1][1]} {detail[1][1]}")
            ui.listWidget_3.addItem("-" * 20)
            ui.listWidget_3.addItem(f"总收益:{db[i][0] - 100000}  {(int(db[i][0] - 100000) / 100000) * 100}%")
            ui.listWidget_3.addItem("-" * 20)
            ui.listWidget_3.addItem(f"--{detail[0][3:6]}")
            ui.listWidget_3.addItem(f"--{detail[len(detail) - 1][7:10]}")
            ui.listWidget_3.addItem("-" * 20)
            amount = 0
            for c in range(len(detail)):
                amount = amount + detail[c][11]
                ui.listWidget_3.addItem(f"{detail[c][0] - 1}： 累计收益:{amount} : {detail[c][3:]}")

    # 保存自选股名单
    @staticmethod
    def AppendToInterestStockList():
        text = ui.listWidget.currentItem().text()
        ui.listWidget_2.addItem(text)
        v=config.Stock_list[text]
        config.interestingStockList[text]=v
        #         # "王府井":"600859.SH",
        
        # l[text]=v

    # 移除自选股列表
    @staticmethod
    def MoveFromInterestStockList():
        # 返回对应项的内容
        text = ui.listWidget_2.currentItem().text()
        # 查找对应item并移除
        for i in range(ui.listWidget_2.count()):
            item = ui.listWidget_2.item(i).text()
            if text == item:
                ui.listWidget_2.takeItem(i)
                break
        
        config.interestingStockList.pop(text)

        
        




    # 模糊查询
    def custom_edit_textChanged(self, event):
        try:
            rec = fuzzyfinder.fuzzyfinder(event, config.Stock_list.keys())
            ui.listWidget.clear()
            if rec:
                for i in range(len(rec)):
                    ui.listWidget.addItem(rec[i])
            else:
                self.setText(event)
        except Exception:
            pass

    # 股票列表点击
    def listWidget_selectionChange(self):
        text = ui.listWidget.currentItem().text()
        self.Stock_Click(text, ui.verticalLayout_2)

    # 自选股列表点击
    def listWidget2_selectionChange(self):
        text = ui.listWidget_2.currentItem().text()
        self.Stock_Click(text, ui.listWidget_5)

    # 推荐列表股票点击
    def listWidget4_selectionChange(self):
        text = ui.listWidget_4.currentItem().text()
        self.Stock_Click(text, ui.listWidget_3)

    def Stock_Click(self, text, ListWidget):
        Data_list = Fetch_stock_data()
        Data_list.ini(config.Stock_list[text])

        Moving_datum = Data_list.Data_form_list.Moving_datum  # 移动平均线数据
        Candle_datum = Data_list.Data_form_list.Candle_datum  # 蜡烛图数据
        Amount_datum = Data_list.Data_form_list.Amount_datum  # 交易量数据
        Gain_lose_datum = Calculation(Moving_datum)  # 收益损失数据

        self.Candle_Chart = CandlestickItem(Candle_datum, Moving_datum)
        self.Amount_Chart = AmountstickItem(Amount_datum)
        self.Earning_Chart = Mat_picture(Gain_lose_datum.earning_x, Gain_lose_datum.earning_y, Moving_datum)

        self.Candle_Chart.sigMouseMoveChanged.connect(self.MyMouseEvent)  # K线图鼠标同步事件
        self.Earning_Chart.sigMouseMoveChanged.connect(self.MyMouseEvent)  # K线图鼠标同步事件

        if ui.verticalLayout.count() == 0:
            # ui.verticalLayout.addWidget(self.Candle_Chart.plt)
            ui.verticalLayout.addWidget(self.Amount_Chart.plt)
            ui.verticalLayout_2.addWidget(self.Candle_Chart.plt)
            ui.verticalLayout_2.addWidget(self.Earning_Chart.plt)
        else:
            # 清除Layout内所有的图
            for i in range(ui.verticalLayout.count()):
                ui.verticalLayout.itemAt(i).widget().deleteLater()
            for i in range(ui.verticalLayout_2.count()):
                ui.verticalLayout_2.itemAt(i).widget().deleteLater()
            ui.verticalLayout.addWidget(self.Amount_Chart.plt)
            ui.verticalLayout_2.addWidget(self.Candle_Chart.plt)
            ui.verticalLayout_2.addWidget(self.Earning_Chart.plt)

        if ListWidget!=None:
            self.SingleStockGainLoseCal(text,ListWidget)
        

    def SingleStockGainLoseCal(self: 'spam', StockCode: str, listWidget):
        ec = earning_Compare()
        key, value = [], []
        key.append(StockCode)
        value.append(config.Stock_list[StockCode])
        list = dict(zip(key, value))

        db = ec.CalculateForspecStock(list)
        wg = listWidget
        wg.clear()
        self.WriteGainLoseToWidget(db, wg)

    def OptionalStockGainLoseCal(self):
        ec = earning_Compare()
        key, value = [], []
        for i in range(ui.listWidget_2.count()):
            item = ui.listWidget_2.item(i).text()
            key.append(item)
            value.append(config.Stock_list[item])
        list = dict(zip(key, value))

        db = ec.CalculateForspecStock(list)
        wg = ui.listWidget_5
        wg.clear()
        self.WriteGainLoseToWidget(db, wg)

    def WriteGainLoseToWidget(self, db, wg: QtWidgets):
        for i in range(len(db)):
            sumlist = db[i][0]
            detail = db[i][1]
            wg.addItem(f"-----------------------------------")
            wg.addItem(f"{detail[1][1]} {detail[1][1]}")
            wg.addItem(f"-----------------------------------")
            wg.addItem(f"总收益:{db[i][0] - 100000}  {(int(db[i][0] - 100000) / 100000) * 100}%")
            wg.addItem(f"-----------------------------------")
            wg.addItem(f"--{detail[0][3:6]}")
            wg.addItem(f"--{detail[len(detail) - 1][7:10]}")
            wg.addItem(f"-----------------------------------")
            amount = 0
            for c in range(len(detail)):
                amount = amount + detail[c][11]
                wg.addItem(f"{detail[c][0] - 1}： 累计收益:{amount} : {detail[c][3:]}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
