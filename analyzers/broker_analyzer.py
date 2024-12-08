import backtrader as bt
import numpy as np
from backtrader import AutoOrderedDict


class BrokerAnalyzer(bt.Analyzer):
    def __init__(self):
        super(BrokerAnalyzer, self).start()

        self.data = {
            'datetime': [],
            'cash': [],
            'value': [],
            'pnl': [],
            'trade_id': [],
            'stock': []
        }


    def create_analysis(self):
        self.rets = AutoOrderedDict()  # dict with . notation

        self.rets.total_return = 0
        self.rets.cagr = 0.0
        self.rets.annual_volatility = 0.0

    def stop(self):
        # Calculate total return
        initial_value = self.data['value'][0]
        final_value = self.data['value'][-1]
        total_return = (final_value - initial_value) / initial_value * 100

        # Calculate CAGR
        start_date = self.data['datetime'][0]
        end_date = self.data['datetime'][-1]
        years = (end_date - start_date).days / 365.25
        cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100

        # Calculate annual volatility
        daily_returns = np.diff(self.data['value']) / self.data['value'][:-1]
        annual_volatility = np.std(daily_returns) * np.sqrt(252) * 100

        self.rets.total_return = total_return
        self.rets.cagr = cagr
        self.rets.annual_volatility = annual_volatility

        self.rets._close()  # . notation cannot create more keys

    def next(self):
        # Track datetime, cash, and value at every iteration
        self.data['datetime'].append(self.strategy.datetime.datetime())
        self.data['cash'].append(self.strategy.broker.get_cash())
        self.data['value'].append(self.strategy.broker.get_value())

    def notify_trade(self, trade):

        # Track profit and loss of closed trades
        if trade.isclosed:
            self.data['pnl'].append((self.strategy.datetime.datetime(), trade.pnl))
            self.data['trade_id'].append((self.strategy.datetime.datetime(), trade.tradeid))
            self.data['stock'].append((self.strategy.datetime.datetime(), trade.data._name))

    def get_analysis(self):
        if not self.data:
            # If there is no value data, return default values or an empty dict
            return super().get_analysis()

        # Calculate total return
        initial_value = self.data['value'][0]
        final_value = self.data['value'][-1]
        total_return = (final_value - initial_value) / initial_value * 100

        # Calculate CAGR
        start_date = self.data['datetime'][0]
        end_date = self.data['datetime'][-1]
        years = (end_date - start_date).days / 365.25
        cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100

        # Calculate annual volatility
        daily_returns = np.diff(self.data['value']) / self.data['value'][:-1]
        annual_volatility = np.std(daily_returns) * np.sqrt(252) * 100

        self.data['total_return'] = total_return
        self.data['cagr'] = cagr
        self.data['annual_volatility'] = annual_volatility

        return self.data
