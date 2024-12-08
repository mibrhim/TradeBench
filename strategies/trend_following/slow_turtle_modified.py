import backtrader as bt
from backtrader.indicators import Highest, Lowest

from helper import logger
from helper.trade_management import TradesManager
from strategies.strategy import Strategy


class SlowTurtleStrategyModified(Strategy):
    params = (
        ('entry', 100),  #100
        ('exit', 50),  #55
        ('sma_trend', 200),
        ('atrPeriod', 14),
        ('roc_period', 200),
        ('stop_loss_atr_multiple', 4),
        ('pyramidN', 1),
        ('min_volume', 50000000),  # $50M

        #filters
        ('dmi_filter', True),
    )

    def _indicators(self):
        self.last_price = {d: 0 for d in self.datas}
        self.new_pyramid_high = False

        # highest indicator
        self.long_entry_level = {d: Highest(d.high, period=self.p.entry) for d in self.datas}
        self.long_exit_level = {d: Lowest(d.low, period=self.p.exit) for d in self.datas}
        self.roc = {d: bt.indicators.RateOfChange(d.close, period=self.p.roc_period) for d in self.datas}
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atrPeriod) for d in self.datas}
        self.volume_sma = {d: bt.indicators.SimpleMovingAverage(d.volume, period=30) for d in self.datas}

        self.sma_market = bt.indicators.SimpleMovingAverage(self.market.close, period=self.p.sma_trend)

        # self.dmi = {d: bt.indicators.DirectionalMovementIndex(d, period=14) for d in self.datas} 


    def _filter(self, data):
        return all([
                    self.volume_sma[data][0] > self.p.min_volume,             
                    self.market.close[0] > self.sma_market[0],         
                ])


    def _rank(self, datas):
        return sorted(datas, key=lambda data: (self.roc[data][0], self.atr[data][0]), reverse=True)
    

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:
        """ Close of the SPY is above the 100-day simple moving average
            (SMA). This indicates a trend in the overall index.
            The close of the 25-day simple moving average is above the
            close of the 50-day simple moving average."""
        return all([
            stock.close > stock.open,
            stock.high[0] > self.long_entry_level[stock][-1],
            #+ (0.1 * self.atr[stock][0]),
            stock.volume[0] > self.volume_sma[stock][0],
        ])


    def _stop_loss(self, order) -> int:

        # # pyramid
        # self.buy(tradeid=order.tradeid,
        #         data=order.data,
        #         exectype=bt.bt.Order.Stop,
        #         price=order.executed.price + (self.p.pyramidN*self.atr[order.data][0]),
        #         oco=order)

        self.new_pyramid_high = False
        if order.executed.size > 0:
            self.last_price[order.data] = order.executed.price

        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])

    def _pyramid(self, stock):

        if stock.high[0] < self.long_entry_level[stock][-1]:
            self.new_pyramid_high = True

        return all([
            stock.close > stock.open,
            stock.high[0] > self.long_entry_level[stock][-1],
            #+ (0.1 * self.atr[stock][0]),
            stock.volume[0] > self.volume_sma[stock][0],
            self.new_pyramid_high,
        ])

    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        return any([
            stock.low[0] < self.long_exit_level[stock][-1],
            self.market.close[0] < self.sma_market[0],
        ])

