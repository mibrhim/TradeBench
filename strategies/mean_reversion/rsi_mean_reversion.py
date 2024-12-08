import backtrader as bt

from strategies.strategy import Strategy

class MeanReversionRSIWithRanking(Strategy):
    params = (
        ('rsi_period', 9),         # Period for RSI
        ('rsi_entry', 20),          # RSI entry threshold
        ('rsi_exit', 70),           # RSI exit threshold
        ('sma_period', 200),        # Period for 200-day Simple Moving Average
        ('atr_period', 14),         # Period for ATR (optional stop loss)
        ('stop_loss_atr_multiple', 2),      # Multiplier for ATR stop loss
        ('max_hold_days', 10),      # Maximum holding period in days
    )

    def _indicators(self):
        # Create a dictionary to store RSI indicators for each data feed (stock)
        self.rsi = {d: bt.indicators.RSI(d, period=self.p.rsi_period) for d in self.datas}
        self.market_sma = bt.indicators.SimpleMovingAverage(self.market.close, period=self.p.sma_period)
        self.sma = {d: bt.indicators.SimpleMovingAverage(d.close, period=self.p.sma_period) for d in self.datas}
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atr_period) for d in self.datas}

        # self.crossover = {d: bt.indicators.CrossOver(self.rsi[d], self.p.rsi_entry) for d in self.datas}
        self.bar_executed = {}  # Track bar index when position is opened
        

    def _rank(self, datas):
        return sorted(datas, key=lambda d: self.rsi[d][0])  # Sort by RSI (lowest RSI first)
    

    def _filter(self, data):
        return all([
                    # self.market.close[0] > self.market_sma[0],
                    # data.close[0] > self.sma[data][0],
                    # 0.04 > (data.close[0] - data.close[-14]) / data.close[-14]> -0.04,
                    self.atr[data][0] / data.close[0] > 0.02
                ])

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:

        return all([
            self.rsi[stock][0] < self.p.rsi_entry
            # self.crossover[stock][0] > 0,
        ])


    def _stop_loss(self, order) -> int:
        self.bar_executed[order.data] = len(self)  # Record the bar index
        
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])


    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        if stock not in self.bar_executed:
            return False
        
        return any([
            self.rsi[stock][0] > self.params.rsi_exit,
            len(self) - self.bar_executed[stock] >= self.p.max_hold_days
        ])
 