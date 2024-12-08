import backtrader as bt

class SafeRSI(bt.Indicator):
    lines = ('rsi',)
    params = (('period', 14),)

    def __init__(self):
        self.addminperiod(self.params.period + 1)  # Ensure enough data for calculation

    def next(self):
        gain = 0
        loss = 0
        
        # Calculate the gains and losses over the period
        for i in range(1, self.params.period + 1):
            change = self.data[-i] - self.data[-i-1]  # Access the data directly, no `.close`
            if change > 0:
                gain += change
            else:
                loss -= change  # loss is positive
        
        avg_gain = gain / self.params.period if gain != 0 else 0.001  # Prevent zero division
        avg_loss = loss / self.params.period if loss != 0 else 0.001  # Prevent zero division
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0.001  # Prevent zero division
        
        # Calculate the RSI value
        self.lines.rsi[0] = 100 - (100 / (1 + rs))
