import backtrader as bt
from backtrader.indicators import Highest, Lowest

from helper import logger
from helper.trade_management import TradesManager
from strategies.strategy import Strategy


class SelloffMeanReversion(Strategy):
    # drawdown(12.5), atr_dd(5), profit(4) - proposed
    # drawdown(12.5), atr_dd(3), profit(6) - backtested
    params = (
        ('drawdown', 12.5),  
        ('profit', 4),  
        ('atr_dd', 5),  
        ('wait_exit_level', 5),  
        ('sma_trend', 150),
        ('stop_loss_atr_multiple', 4),
    )

    def _indicators(self):
        self.buy_price = None
        # highest indicator
        self.trend_sma = {d: bt.indicators.SimpleMovingAverage(d, period=self.p.sma_trend) for d in self.datas}



    def _rank(self, datas):
        return sorted(datas, key=lambda data: ((data.close[-3] - data.close[0]) / data.close[-3]) * 100, reverse=True)
    

    def _filter(self, data):
        return all([
                    self.atr[data][0]/data.close[0] >= self.p.atr_dd / 100,
                ])

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:
        
        return all([
                    stock.close[0] > self.trend_sma[stock][0], 
                    (stock.close[-3] - stock.close[0]) / stock.close[-5] >= self.p.drawdown / 100,
                ])


    def _stop_loss(self, order) -> int:
        self.buy_price = order.executed.price
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])


    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        if self.buy_price is None:
            return False
        
        return ((stock.close[0] - self.buy_price) / stock.close[0]) * 100 >= self.p.profit

