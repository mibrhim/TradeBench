import backtrader as bt

from helper.trade_management import TradesManager
from indicators.safe_rsi import SafeRSI

class WeeklyRotationStrategy(bt.Strategy):
    params = (
        ('sma_period', 200),   # Period for the 200-day Simple Moving Average
        ('rsi_period', 3),     # Period for the 3-day RSI
        ('roc_period', 100),   # Period for the Rate of Change
        ('max_positions', 10), # Max number of positions to hold
        ('volume_filter', 10000000),  # Minimum volume filter
        ('price_filter', 1),   # Minimum price filter
        # ('sma_buffer', 0.98),   # 2% below the 200-day SMA band
        ('stop_loss_atr_multiple', 2),
        ('atrPeriod', 14),

        #filters
        ('dmi_filter', False),
    )

    def __init__(self):
        self.name = "Weekly Rotation Strategy"
        self.market = self.getdatabyname('SPY')  # Get SPY data feed
        self.trades = TradesManager(self.__class__)
        self.stop_loss = {d: None for d in self.datas}

        # Keep track of the SPY 200-day SMA and create SMA with buffer
        self.spy_sma = bt.indicators.SimpleMovingAverage(self.market.close, period=self.params.sma_period)
        # self.spy_sma_band = self.spy_sma * self.params.sma_buffer

        # Create indicators for each stock
        # self.rsi = dict((d, SafeRSI(d.close, period=self.params.rsi_period)) for d in self.datas)
        self.roc = dict((d, bt.indicators.RateOfChange(d.close, period=self.params.roc_period)) for d in self.datas)
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atrPeriod) for d in self.datas}

        self.dmi = {d: bt.indicators.DirectionalMovementIndex(d) for d in self.datas} 

        self.week_counter = 0  # To track when to trade
        self.data_name = {d._name: d for d in self.datas}

    def next(self):
        # Only execute trades on the last trading day of the week (Friday)
        if not self.data.datetime.date().weekday() == 4:  # 4 is Friday
            return

        self.week_counter += 1

        # Check SPY condition (above 200-day SMA band)
        if self.market.close[0] < self.spy_sma[0]:
            return  # Skip if SPY is not above the 200-day SMA band

        # Filter stocks based on volume and price
        candidates = []
        for d in self.datas:
            if d == self.market:  # Skip SPY
                continue

            if d.volume[0] < self.params.volume_filter or d.close[0] < self.params.price_filter:
                continue

            # if not self.rsi[d][0] > 70:  # RSI filter
            #     continue

            if not (self.dmi[d].plusDI[0] > self.dmi[d].minusDI[0] and self.dmi[d].adx[0] > 20) and self.p.dmi_filter:
                continue

            candidates.append(d)

        # Select top 10 stocks based on highest ROC
        candidates = sorted(candidates, key=lambda d: self.roc[d][0], reverse=True)[:self.params.max_positions]

        # Sell stocks not in the top 10 ROC list anymore
        for position in self.positionsbyname.keys():
            data = self.data_name[position]

            trade_id = self.trades.get_current_trade(data)
            if data not in candidates and self.trades.is_in_trade(data):
                self.close(tradeid=trade_id, 
                           size=self.trades.get_position(data),
                           data=data)

        # Enter new positions
        for data in candidates:

            trade_id = self.trades.generate_trade_id(data)
            if not self.trades.is_in_trade(data):
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
        stop_loss_price = order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])

        # if order.data in self.stop_loss:
        #     self.cancel(self.stop_loss[order.data])

        # # Create stop loss order
        # self.stop_loss[order.data] = self.close(tradeid=order.tradeid, data=order.data, exectype=bt.bt.Order.Stop,
        #                                         price=stop_loss_price,
        #                                         size=self.trades.get_position(order.data),
        #                                         oco= order)

    #
    def notify_trade(self, trade):
        if hasattr(self.sizer, 'notify_trade'):
            self.sizer.notify_trade(trade)