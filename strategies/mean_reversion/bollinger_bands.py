import backtrader as bt

from strategies.strategy import Strategy

class BollingerBandsStrategy(Strategy):
    params = (
        ('boll_period', 5),
        ('boll_dev', 2),
        ('sma_period', 10),
        ('rsi_period', 9),
        ('rsi_entry', 30),
        ('rsi_exit', 70),

        ('stop_loss_atr_multiple', 2)
    )

    def _indicators(self):
        self.boll = {d: bt.indicators.BollingerBands(d, period=self.params.boll_period, devfactor=self.params.boll_dev) for d in self.datas}
        # self.sma_trend = {d: bt.indicators.SMA(d,  period=self.params.sma_period) for d in self.datas}
        self.market_sma = bt.indicators.SMA(self.market, period=self.params.sma_period)
        self.rsi = {d: bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period) for d in self.datas}

        self.corss_mid = {d: bt.indicators.CrossOver(d.close, self.boll[d].mid) for d in self.datas}

        self.corss_bottom = {d: bt.indicators.CrossOver(d.close, self.boll[d].bot) for d in self.datas}


        self.roc = {d: bt.indicators.RateOfChange(d.close, period=100) for d in self.datas}

            

    def _filter(self, data):
        period = -21
        return all([
                    # self.market.close[0] > self.market_sma[0],
                    # self.boll[data].lines.top[-1] - self.boll[data].lines.mid[-1] == self.boll[data].lines.mid[-1] - self.boll[data].lines.bot[-1],
                    # 0.04 > (data.close[0] - data.close[period]) / data.close[period]> -0.04,
                    # self.atr[data][0] / data.close[0] > 0.02
                    # (self.boll[data].lines.top[-1] - self.boll[data].lines.bot[-1]) / data.close[0] > 0.05,
                ])


    def _rank(self, datas):
        # return sorted(datas, key=lambda d: (self.rsi[d], -self.roc[d]), reverse=False)  # Sort by RSI (lowest RSI first)
        return sorted(datas, key=lambda d: (self.rsi[d]), reverse=False)  # Sort by RSI (lowest RSI first)
    

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:

        return all([
            # stock.close[0] < self.boll[stock].lines.bot[-1],
            self.corss_bottom[stock] > 0
            # self.rsi[stock] < self.params.rsi_entry,
            # self.boll[stock].lines.mid[0] - self.boll[stock].lines.bot[0] > self.atr[stock][0] * 4
        ])


    def _stop_loss(self, order) -> int:

        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])


    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:  
        return any([
            # stock.close > self.boll[stock].lines.top[-1], 
            stock.close > self.boll[stock].lines.top[-1], 
            self.corss_mid[stock] < 0,
            # stock.close[0] > self.sma[stock][0], 
            # self.rsi[stock] > self.params.rsi_exit,
        ])