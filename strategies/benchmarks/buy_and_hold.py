# strategies/buy_and_hold.py
import backtrader as bt


class BuyAndHold(bt.Strategy):
    params = (
        ('param1', 10),  # Default value for param1
        ('param2', 0.1),  # Default value for param2
    )


    def __init__(self):
        self.name = "Buy And Hold"

    def next(self):
        for data in self.datas:
            self.buy(data=data)


    def notify_order(self, order):
        pass


    def notify_trade(self, trade):
        pass


    def notify_store(self, msg, *args, **kwargs):
        print(msg)
