import backtrader as bt

# Custom commission class for fixed $1 per order
class FixedCommission(bt.CommInfoBase):
    def getcommission(self, size, price):
        return 1.0  # Return a fixed commission of $1 for the whole order