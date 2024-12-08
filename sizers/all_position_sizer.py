import math

import backtrader as bt

from sizers.risk_manager import RiskManager

class AllPositionSizer(bt.Sizer):
    params = (
        ('risk', 1),
        )
    
    def __init__(self):
        self.risk = RiskManager()
        self.max_active_units = 0

    def _getsizing(self, comminfo, cash, data, isbuy):
        self.max_active_units = self.risk._max_active_units_per_strategy[self.strategy.name]

        if not isbuy:
            return 0

        # confirm with risk manager to take more units
        if not self.risk.take_more(self.strategy, data):
            return 0


        self.n_factor = self.strategy.p.stop_loss_atr_multiple

        # we will need to trade only 6 at the same time
        self.strategy_count = len(self.strategy.cerebro.strats)
        
        # calculate max allowed amount per unit
        allowed_cash_per_strategy = self.broker.get_value() / self.strategy_count

        allowed_cash_per_trade = allowed_cash_per_strategy / self.max_active_units

        # calculate the size based on the risk
        risk_amount = (self.p.risk/ 100) * self.broker.get_value()

        # choose the minimum amount
        allowed_size_per_trade = math.floor(allowed_cash_per_trade/data.close[0])
        risk_size = math.floor(risk_amount/(self.n_factor * self.strategy.atr[data][0]))
        size = min(risk_size, allowed_size_per_trade)
        

        # confirm that the size have available cash
        if size * data.close[0] > cash:
            size = math.floor(cash/(data.close[0]))

        if size > 0:
            self.risk.add(self.strategy, data)

        print(
            f'[Sizer], {self.strategy.name} Size: {size} & amount: {size * data.close} no. of starts: {len(self.strategy.cerebro.strats)}')

        return size


    #
    def notify_trade(self, trade):

        if trade.isclosed:
            print(f"[SIZER] Inside closed trade trade {trade.data._name}")
            self.risk.remove(self.strategy, trade.data)