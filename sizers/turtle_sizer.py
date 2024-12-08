import math

import backtrader as bt

from sizers.risk_manager import RiskManager


#
class TurtleSizer(bt.Sizer):
    params = (
        ('risk', 1),  # 1% of account equity per trade
    )

    def __init__(self):
        self.positions = {}
        self.atr_period = None
        self.n_factor = None

        self.risk = RiskManager()
        self.max_active_units = 0

    def _get_risk_amount(self,):
        return (self.p.risk/100) * self.broker.get_value()
    
    # 
    def _get_size_per_strategy(self, strategy, data, max_allocated_per_unit):

        # Calculate the position size based on the risk tolerance
        risk_amount = self._get_risk_amount()

        position_size = math.floor(risk_amount / (self.strategy.atr[data][0] * self.n_factor))
        max_position_size = (max_allocated_per_unit) / data.close[0]

        # take the min of the risk adjusted position and max allowed position
        position_size = min(position_size, max_position_size)

        # ensure there are enough cash
        if strategy.broker.get_cash() < position_size * data.close[0]:
            position_size = strategy.broker.get_cash() / data.close[0]

        return int(position_size)


    def _get_size(self, strategy, data):
        account_value = strategy.broker.get_value()
       
        # the allocated amount for each strategy is equal.
        strategy_allocated_value = account_value / self.strategies_count

        max_allocated_per_unit = strategy_allocated_value / self.max_active_units
        # get the size for the strategy
        size = self._get_size_per_strategy(strategy, data, max_allocated_per_unit)


        available_size = min(size, strategy.broker.get_cash() // data.close[0])
            
        return available_size

    #
    def _getsizing(self, comminfo, cash, data, isbuy):
        self.max_active_units = self.risk._max_active_units_per_strategy[self.strategy.name]

        # return if not buy as we support only buy
        if not isbuy:
            print(f"[Sizer] Sell ****************************************")
            return 0
        
        # confirm with risk manager to take more units
        if not self.risk.take_more(self.strategy, data):
            return 0

        # initialize the sizing parameters
        self.atr_period = self.strategy.p.atrPeriod
        self.n_factor = self.strategy.p.stop_loss_atr_multiple
        self.strategies_count = len(self.strategy.cerebro.strats)

        return self._get_size(self.strategy, data)


    #
    def notify_order(self, order):
        if not order.isbuy():
            return
        
        if order.status not in [order.Completed]:
            return
        
        print(f"[SIZER] New Order has been executed for {order.data._name}")
        
        # add more positions to the cuurrent position
        self.risk.add(self.strategy, order.data)

    #
    def notify_trade(self, trade):

        if trade.isclosed:
            print(f"[SIZER] Inside closed trade trade {trade.data._name}")
            self.risk.remove(self.strategy, trade.data)
