from abc import abstractmethod
import backtrader as bt
from backtrader.indicators import Highest, Lowest
from helper.trade_management import TradesManager
from helper import logger

class Strategy(bt.Strategy):
    params = (
        ('atrPeriod', 14),
    )

    def __init__(self):
        self.market = self.getdatabyname('SPY')  # Get SPY data feed

        print(f"Initiating {self.__class__.__name__}")
        self.name = self.__class__.__name__
        self.stop_loss = {d: None for d in self.datas}
        self.trades = TradesManager(self.__class__)
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atrPeriod) for d in self.datas}
        self.data_name = {d._name: d for d in self.datas}
        self._indicators()
        print(f"Finish Initiating {self.__class__.__name__}")

    def next(self):
        # Check for any exit
        for d in self.positionsbyname.keys():
            if d == self.market:  # Skip SPY
                continue

            data = self.data_name[d]
            trade_id = self.trades.get_current_trade(data)

            if self._exit(data) and self.trades.is_in_trade(data):
                self.broker.cancel(self.stop_loss[data])

                self.close(tradeid=trade_id, data=data, price=data.close[0],
                           size=self.trades.get_position(data),
                           oco=self.stop_loss[data])


        filtered_data = []
        for data in self.datas:
            if data == self.market:  # Skip SPY
                continue

            # Filter data
            if self._filter(data):
                filtered_data.append(data)      

        # Rank data
        ranked_datas = self._rank(filtered_data)

        # Check for entry
        for data in ranked_datas:
            if data == self.market:  # Skip SPY
                continue

            trade_id = self.trades.get_current_trade(data)
            if self._pyramid(data) and self.trades.is_in_trade(data):
                self.buy(tradeid=trade_id, data=data)

            trade_id = self.trades.generate_trade_id(data)
            if self._setup(data) and not self.trades.is_in_trade(data):
                self.buy(tradeid=trade_id, data=data)

    def notify_order(self, order):
        # notify sizer if required
        if hasattr(self.sizer, 'notify_order'):
            self.sizer.notify_order(order)

        if not order.isbuy() and order.status in [order.Completed]:
            self.trades.close_trade(order.data)
            print(f"Trade closed with ID: {order.tradeid}")

        if not order.isbuy():
            return

        if order.status not in [order.Completed]:
            return

        if not self.trades.is_in_trade(order.data):
            self.trades.add_trade(order.data)

        self.trades.add_position(order.data, order.size)

        # Calculate stop loss price
        stop_loss_price = self._stop_loss(order)

        logger.log(order.data,
                   f"order {bt.Order.Status[order.status]} size: {order.executed.size}, total position: {self.getposition(order.data).size} for {order.data}")

        if order.data in self.stop_loss:
            self.cancel(self.stop_loss[order.data])

        # Create stop loss order
        self.stop_loss[order.data] = self.close(tradeid=order.tradeid, data=order.data, exectype=bt.bt.Order.Stop,
                                                price=stop_loss_price,
                                                size=self.trades.get_position(order.data),
                                                oco= order)


    #
    def notify_trade(self, trade):
        if hasattr(self.sizer, 'notify_trade'):
            self.sizer.notify_trade(trade)
        


    # Setup condition
    @abstractmethod
    def _rank(self, stocks) -> list:
        return []
    
    # Setup condition
    @abstractmethod
    def _filter(self, stock) -> bool:
        return True

    # Setup condition
    @abstractmethod
    def _setup(self, stock) -> bool:
        return False

    # Pyramid condition
    @abstractmethod
    def _pyramid(self, stock) -> bool:
        return False

    # Exit condition
    @abstractmethod
    def _exit(self, stock) -> bool:
        return False
    
    def _stop_loss(self, order) -> int:
        return 0
