# sizers/sizer_example.py
import backtrader as bt


class ExampleSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        # Implement your sizing logic
        return 10  # For example, 10 shares
