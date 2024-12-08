import backtrader as bt
from backtrader.indicators import Highest, Lowest

from helper import logger
from helper.trade_management import TradesManager
from strategies.strategy import Strategy


class FastTurtleStrategy(Strategy):
    params = (
        ('entry', 20),  #100
        ('exit', 10),  #55
        ('sma_trend', 200),
        ('atrPeriod', 14),
        ('roc_period', 200),
        ('stop_loss_atr_multiple', 2),
        ('pyramidN', 0.2),
        ('min_volume', 10000000),  # $50M
        ('adxPeriod', 31),  # $50M
    )

    def _indicators(self):
        self.last_price = {d: 0 for d in self.datas}
        self.skip_trade = {d: 0 for d in self.datas}

        # highest indicator
        self.long_entry_level = {d: Highest(d.high, period=self.p.entry) for d in self.datas}
        self.long_exit_level = {d: Lowest(d.low, period=self.p.exit) for d in self.datas}
        self.roc = {d: bt.indicators.RateOfChange(d.close, period=self.p.roc_period) for d in self.datas}
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atrPeriod) for d in self.datas}
        self.adx = {d: bt.indicators.AverageDirectionalMovementIndex(d, period=self.p.adxPeriod) for d in self.datas}

        self.sma_market = bt.indicators.SimpleMovingAverage(self.market.close, period=self.p.sma_trend)


    def _rank(self, datas):
        return sorted(datas, key=lambda data: (self.roc[data][0], self.atr[data][0]), reverse=True)
    

    def _filter(self, data):
        return all([
                    data.volume[0] > self.p.min_volume,                 # get stocks with high volume                
                    # self.market.close[0] > self.sma_market[0],          # we aren't going to buy anything if the market is down
                    not self.skip_trade[data],
                    self.adx[data] > 20
                ])

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:
        """ Close of the SPY is above the 100-day simple moving average
            (SMA). This indicates a trend in the overall index.
            The close of the 25-day simple moving average is above the
            close of the 50-day simple moving average."""
        return stock.high[0] > self.long_entry_level[stock][-1] #+ (0.1 * self.atr[stock][0])


    def _stop_loss(self, order) -> int:

        # pyramid
        self.buy(tradeid=order.tradeid,
                data=order.data,
                exectype=bt.bt.Order.Stop,
                price=order.executed.price + (self.p.pyramidN*self.atr[order.data][0]),
                oco=order)

        self.last_price[order.data] = order.executed.price
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])

    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        condition = stock.low[0] < self.long_exit_level[stock][-1]

        if condition:
            self.skip_trade[stock] = False
        
        return condition


    def notify_trade(self, trade):
        if trade.isclosed:
            self.skip_trade[trade.data] = trade.pnl > 0

        return super().notify_trade(trade)