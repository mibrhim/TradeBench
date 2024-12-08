from strategies.strategy import Strategy
import backtrader as bt


class MomentumStrategy(Strategy):
    params = (
        ('fast_sma', 50),     # 25
        ('slow_sma', 100),     #50
        ('sma_trend', 100),
        ('roc_period', 50),
        ('atr_period', 20),
        ('stop_loss_atr_multiple', 4),
        ('trailing_stop_pct', 0.15),
        ('min_price', 1.00),
        ('min_volume', 50000000),  # $50M
    )

    def _indicators(self):
        self.fast_sma = {d: bt.indicators.SimpleMovingAverage(d.close, period=self.p.fast_sma) for d in self.datas}
        self.slow_sma = {d: bt.indicators.SimpleMovingAverage(d.close, period=self.p.slow_sma) for d in self.datas}
        self.roc = {d: bt.indicators.RateOfChange(d.close, period=self.p.roc_period) for d in self.datas}
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atr_period) for d in self.datas}
        self.volume_sma = {d: bt.indicators.SimpleMovingAverage(d.volume, period=10) for d in self.datas}

        self.sma_market = bt.indicators.SimpleMovingAverage(self.market.close, period=self.p.sma_trend)

    #
    def _filter(self, data) -> bool:
        return all([
                    # data.volume[0] > self.p.min_volume,                 # get stocks with high volume         
                    self.volume_sma[data][0] > self.p.min_volume,        
                    self.market.close[0] > self.sma_market[0],          # we aren't going to buy anything if the market is down
                ])
    

     #
    def _rank(self, datas) -> bool:
        return sorted(datas, key=lambda data: (self.roc[data][0], self.atr[data][0]), reverse=True)

    #
    def _setup(self, data) -> bool:
        return self.fast_sma[data][0] > self.slow_sma[data][0]

    #
    def _stop_loss(self, order) -> int:
        self.close(tradeid=order.tradeid,
                data=order.data,
                exectype=bt.Order.StopTrail,
                trailpercent=self.p.trailing_stop_pct,
                size=self.trades.get_position(order.data),
                # size=order.executed.size,
                oco=order)
        
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])

     # no exit required here
    def _exit(self, stock) -> bool:
        return any([
            self.market.close[0] < self.sma_market[0],
        ])