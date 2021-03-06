import config
from SQLserver import *
from Data_convert import *


class Descison():                                   #一次决策
    def __init__(self):
        self.tradingPointList = []                  #买卖点的记录保存
        self.QtyBuy = 0
        self.DecisionName='MovingAvgDescision'

    def runDecision(self, datum):     
        #计算买卖点，买卖点的记录保存在tradingPointList
        list = []
        self.hold_amount = 100000
        for i in range(len(datum)):
            if datum[i][4] == 0 or datum[i][3] == 0:
                continue
            if datum[i][4] - datum[i][3] == 0:
                gap = 1
            else:
                gap = abs(datum[i][4] - datum[i][3]) / (datum[i][4] - datum[i][
                    3])  # str(ts_code),str(trade_date),float(avgprice),float(avg5day),float(avg10day)
            list.append([gap, datum[i][0], datum[i][1], datum[i][2]])  # gap,ts_code,trade_date,avgprice

        # 选着跳变的点
        j = 1
        for i in range(len(list) - 1):
            if list[i][0] == 1 and list[i + 1][0] == -1:  # 5MA 上穿  10MA
                ss = BuySaleRec()
                # 第几次交易
                ss.code = datum[i][0]
                ss.Name = self.get_key(config.Stock_list, ss.code)  # 股票名称
                ss.DateToBuy = list[i][2]  # 买入日期
                ss.PriceBuy = list[i][3]  # 买入价格
                ss.QtyBuy = int(self.hold_amount / (list[i][3] * 1.003))  # 买入xxx股
                self.QtyBuy = ss.QtyBuy
                ss.AmountBuy = int(ss.PriceBuy * ss.QtyBuy*1.003)  # 买入金额
                ss.Decision = 'buy'  # 决策
                self.Hold_amount(cost=-self.hold_amount) # 计算手中还有多少钱
                

                ss.tradingRec_Buy.tradingDate=list[i][2]  # 买入日期
                ss.tradingRec_Buy.price=list[i][3]  # 买入价格
                ss.tradingRec_Buy.qty=int(self.hold_amount / (list[i][3] * 1.003))  # 买入xxx股
                ss.tradingRec_Buy.amount=int(ss.tradingRec_Buy.price*ss.tradingRec_Buy.qty) # 买入金额
                ss.tradingRec_Buy.status='buy'

                self.tradingPointList.append(ss)


            elif list[i][0] == -1 and list[i + 1][0] == 1:
                ss = BuySaleRec()
                ss.ID = j  # 第几次交易
                ss.code = datum[i][0]
                ss.Name = self.get_key(config.Stock_list, ss.code)  # 股票名称
                ss.DateToSale = list[i][2]
                ss.PriceSale = list[i][3]
                ss.QtySale = self.QtyBuy
                ss.AmountSale = int(ss.PriceSale * ss.QtySale * 0.997)
                ss.Decision = 'sale'
                
                ss.GainloseAmount = ss.AmountSale - ss.AmountBuy
                if ss.GainloseAmount > 0:
                    ss.GainCount = ss.GainCount + 1
                else:
                    ss.LoseCount = ss.LoseCount + 1
                self.Hold_amount(cost=ss.AmountSale)

                ss.tradingRec_Sale.tradingDate=list[i][2]
                ss.tradingRec_Sale.price=list[i][3]
                ss.tradingRec_Sale.qty=self.QtyBuy
                ss.tradingRec_Sale.amount=int(ss.tradingRec_Sale.price*ss.tradingRec_Sale.qty* 0.997)
                ss.tradingRec_Sale.status='buy'
                
                self.tradingPointList.append(ss)  # 10MA 上穿  5MA

                j += 1

    def get_key(self, dict, value):
        for k, v in dict.items():
            if v == value:
                return k

    def Hold_amount(self, cost):  # 手中持有的金额
        self.hold_amount += cost


class BuySaleRec():       
    #一次买卖记录
    def __init__(self):
        self.ID = ''
        self.Name = ''
        self.code = ''
        self.DateToBuy = ''
        self.PriceBuy = ''
        self.QtyBuy = 0
        self.AmountBuy = 0
        self.DateToSale = ''
        self.PriceSale = ''
        self.QtySale = 0
        self.AmountSale = 0
        self.GainloseAmount = 0
        self.GainCount = 0
        self.LoseCount = 0
        self.Decision = ''
        self.tradingRec_Buy= TradingRec()
        self.tradingRec_Sale= TradingRec()
        self.tradingRecList=[]                  #一次买卖记录并在List里

class TradingRec():
    def __init__(self):
        self.stockName=''       #股票名称
        self.stockCode=''       #股票代码
        self.tradingDate=''     #交易日期
        self.tradingName=''     #'buy'   'sale'
        self.price=''           #交易金额
        self.qty=''             #交易数量
        self.amount=''          #交易金额
        self.status=''          #交易转态  ，申请，撤单，成交，取消
        self.account=''          #交易账户

        self.list=config.interestingStockList
class StockAcount:
    def __init__(self):    
        
        self.initInvestAmount=10                            #初始投资额
        self.unitName='万元'                                #收益单位 万元
        self.unitRedio=10000                                #转换比例
        self.AccountBalance=0                               #账户余额    
        self.currentTradingInitInvestAmount=0               #当比交易的初始投资额
        self.currentTradingInitStockQty=0                   #当前交易初始股票数量
        self.currentTradingInitStockPrice_Buy=0             #当前交易初始股票原始买入价格
        self.currentTradingInitStockAmount=0                #当前交易初始股票原始市值 currentTradingInitStockQty*currentTradingInitStockPrice_Buy
    
        self.securitiesInfo=securitiesInfo()
        self.UserName=self.securitiesInfo.name            #账户名
        self.StockAmount=0                         #股票市值 基于当天的股价计算的市值
        self.StockInitAmount=0                      #股票成本，历史买入价*历史买入数量+历史资金
        self.Accumulate_CommissionAmount=0                     #累计交易成本
        self.CommissionRadio=1.003                  #交易成本比例
        # self.TradingHistory=TradingHistory()                      #历史记忆记录 

    def updateInfo(self):
        #更新数据
        self.AccountBalance=0                               #账户余额    
        self.currentTradingInitInvestAmount=0               #当比交易的初始投资额
        self.currentTradingInitStockQty=0                   #当前交易初始股票数量
        self.currentTradingInitStockPrice_Buy=0             #当前交易初始股票原始买入价格
        self.currentTradingInitStockAmount=0                #当前交易初始股票原始市值 currentTradingInitStockQty*currentTradingInitStockPrice_Buy
class securitiesInfo():
    def __init__(self):
        self.name='张三'                            #开户证券公司名
        self.account='12345678'                         #开户证券公司账户
        self.password='12345678'                        #登录密码
        self.tradingPassword='1236658'                 #委托交易密码
        self.IP='127.0.0.1'                              #远程控制IP地址
        self.Port='4433'                            #远程接入端口号
        self.API='undefinde'                             #远程连接API接口字符串

def Connecting_database(self):
    # 连接数据库 获取股票的表头信息和表内数据
    server = SQLserver()
    server.Sql_execution(sql="DELETE FROM \"temp\"")
    server.Sql_execution(
        f"""INSERT INTO temp({config.tushare["Column"]}) SELECT {config.tushare["Column"]} FROM "stock" where stock.ts_code == '000001.SZ' """)
    server.Sql_execution("select * from temp")
    server.Fetch_data()
    data = server.data  # 获取表内数据
    datum = Data_convert(data).Moving_average_form()
    return datum
# if __name__ == '__main__':
#     datum=Connecting_database("000001.SZ")
#     des=Descison()
#     s = selectedStock()
#     des.selectStock_avg(datum)
#     for s in des.selectedStockList:
#         print(s.DateToBuy,s.DateToSale,s.Decision)
