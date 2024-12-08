import backtrader as bt

class AccumulationDistribution(bt.Indicator):
    lines = ('ad',)
    
    def __init__(self):
        # Calculate money flow multiplier and money flow volume
        mfm = ((self.data.close - self.data.low) - (self.data.high - self.data.close)) / (self.data.high - self.data.low + 1e-9)
        mfv = mfm * self.data.volume
        # Accumulate the money flow volume to get the A/D line
        self.lines.ad = bt.indicators.SumN(mfv, period=1)