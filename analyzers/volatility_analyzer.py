import backtrader as bt
import numpy as np


class VolatilityAnalyzer(bt.Analyzer):
    def __init__(self):
        self.daily_returns = []
        self.previous_value = None

    def next(self):
        # Get the current portfolio value
        value = self.strategy.broker.get_value()

        # Calculate the daily return if there is a previous value
        if self.previous_value is not None:
            daily_return = (value - self.previous_value) / self.previous_value
            self.daily_returns.append(daily_return)

        # Update the previous value for the next iteration
        self.previous_value = value

    def get_analysis(self):
        # Calculate annual volatility
        annual_volatility = np.std(self.daily_returns) * np.sqrt(252) * 100
        return {'annual_volatility': annual_volatility}
