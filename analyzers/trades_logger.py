from backtrader import Analyzer, num2date

from sizers.risk_manager import RiskManager

class TradeLogger(Analyzer):
    def __init__(self):
        self.trades = []
        self.orders = []
        self.risk = RiskManager()

    def notify_order(self, order):
        if order.status == order.Completed:
            self.orders.append({
                'stock': order.data._name,
                'buy': order.isbuy(),
                'tradeid': order.tradeid,
                'date': num2date(order.executed.dt),
                'size': order.size,
                'price': order.executed.price,
                'amount': abs(order.executed.size * order.executed.price),
                'commission': order.executed.comm,
                'type': order.getordername(),
                'active': self.risk.get_active_units()
            })

    def notify_trade(self, trade):
        if trade.isclosed:
            # Get current capital when trade opened
            broker = self.strategy.broker
            capital_at_entry = broker.getvalue()  # Capital at the time trade opened
 
            # Calculate percentage PnL relative to the total capital at trade entry
            pnl_percentage = (trade.pnl / capital_at_entry) * 100 if capital_at_entry != 0 else 0

            # Log trade details including PnL percentages
            self.trades.append({
                'stock': trade.data._name,
                'date_in': num2date(trade.dtopen),
                'date_out': num2date(trade.dtclose),
                'size': trade.size,
                'price_in': trade.price,
                'trade_id': trade.tradeid,
                'pnl': trade.pnl,
                'net_pnl': trade.pnlcomm,
                'pnl_percentage': pnl_percentage,  # PnL % relative to the trade
                'capital_at_entry': capital_at_entry,  # Record capital at the time of trade
                'orders': [o for o in self.orders if o['tradeid'] == trade.tradeid and
                           o['date'] >= num2date(trade.dtopen) and
                           o['date'] <= num2date(trade.dtclose)]
            })

    def get_analysis(self):
        return {
            'trades': self.trades,
            'orders': self.orders,
        }
