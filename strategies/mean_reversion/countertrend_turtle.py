import backtrader as bt
from backtrader.indicators import Highest, Lowest

from helper import logger
from helper.trade_management import TradesManager
from strategies.strategy import Strategy


class TurtleCTStrategy(Strategy):
    params = (
        ('up_level', 10),  #100
        ('down_level', 10),  #55
        ('sma_trend', 200),
        ('atrPeriod', 14),
        ('adx_period', 21),
        ('rsi_period', 14),
        ('stop_loss_atr_multiple', 2),
        ('min_volume', 10000000),  # $50M
        ('filter',True),  # $50M
    )

    def _indicators(self):

        # highest indicator
        self.long_top_level = {d: Highest(d.high, period=self.p.up_level) for d in self.datas}
        self.long_bottom_level = {d: Lowest(d.low, period=self.p.down_level) for d in self.datas}

        self.rsi = {d: bt.indicators.RSI(d, period=self.p.rsi_period) for d in self.datas}
        self.adx = {d: bt.indicators.AverageDirectionalMovementIndex(self.data, period=21) for d in self.datas}

        self.sma_market = bt.indicators.SimpleMovingAverage(self.market.close, period=self.p.sma_trend)
        self.average_volume = {d: bt.indicators.SimpleMovingAverage(d.volume, period=self.p.sma_trend) for d in self.datas}
        self.sma = {d: bt.indicators.SimpleMovingAverage(d.close, period=self.p.sma_trend) for d in self.datas}


    def _filter(self, data):
        return all([     
                    # self.market.close[0] > self.sma_market[0] or not self.p.filter,          # we aren't going to buy anything if the market is down
                    # 0.01 > self.roc[data][0] > 0,
                    # self.atr[data][0] / data.close[0] > 0.02
                    self.sma[data][0] - self.sma[data][-self.p.rsi_period] > 0,
                    # self.adx[data] < 20,
                    # self.rsi[data] < 30,
                ])
    

    def _rank(self, datas):
        return sorted(datas, key=lambda data: (self.atr[data][0], -self.rsi[data]), reverse=True)

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:
        return all({
                    stock.low[0] < self.long_bottom_level[stock][-1],
                    stock.volume[0] < self.average_volume[stock][0]
                })


    def _stop_loss(self, order) -> int:
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])

    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        return stock.high[0] > self.long_top_level[stock][-1] #+ (0.1 * self.atr[stock][0])

