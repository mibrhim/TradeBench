import backtrader as bt

class SMAminusATR(bt.Indicator):
    lines = ('sma_minus_2atr',)
    params = (('sma_period', 100), ('atr_period', 14),
              ('atr_multiplier', 3),)

    def __init__(self):
        sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)
        atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.lines.sma_minus_2atr = sma - self.params.atr_multiplier * atr