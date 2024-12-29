import backtrader as bt

from strategies.strategy import Strategy

class MeanReversionRSIWithRanking(Strategy):
    params = (
        ('rsi_period', 9),         # Period for RSI
        ('rsi_entry', 40),          # RSI entry threshold
        ('rsi_exit', 70),           # RSI exit threshold
        ('sma_period', 200),        # Period for 200-day Simple Moving Average
        ('atr_period', 14),         # Period for ATR (optional stop loss)
        ('stop_loss_atr_multiple', 2),      # Multiplier for ATR stop loss
        ('max_hold_days', 10),      # Maximum holding period in days

        ('min_volume', 50000000),  # $50M
    )

    def _indicators(self):
        # Create a dictionary to store RSI indicators for each data feed (stock)
        self.rsi = {d: bt.indicators.RSI(d, period=self.p.rsi_period) for d in self.datas}
        self.macd = {d: bt.indicators.MACDHisto(d) for d in self.datas}
        self.atr = {d: bt.indicators.AverageTrueRange(d, period=self.p.atr_period) for d in self.datas}
        
        self.volume_sma = {d: bt.indicators.SimpleMovingAverage(d.volume, period=30) for d in self.datas}

        # self.bar_executed = {d: 0 for d in self.datas}

    
    def _filter(self, data):
        return True
        # return all([
        #             self.volume_sma[data][0] > self.p.min_volume, 
        #         ])

    def _rank(self, datas):
        return sorted(datas, key=lambda d: -self.rsi[d][0])  # Sort by RSI (lowest RSI first)
    

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:

        return all([
            # self.rsi[stock][0] < 40,
            # self.rsi[stock][0] > self.rsi[stock][-1]
            self.macd[stock][0] > self.macd[stock][-1]
        ])


    def _stop_loss(self, order) -> int:
        # self.bar_executed[order.data] = len(self)  # Record the bar index
        
        # pyramid
        self.close(tradeid=order.tradeid,
                data=order.data,
                exectype=bt.bt.Order.Limit,
                price=self.get_trade_target_price(order.data, 1),
                oco=order)


        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])
        


    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:
        # if stock not in self.bar_executed:
        #     return False
        
        return False
        # return any([
        #     self.rsi[stock][0] > self.params.rsi_exit,
        #     self.get_trade_profit_percentage(stock) > 1,
        #     # len(self) - self.bar_executed[stock] >= self.p.max_hold_days
        # ])
 


    def get_trade_profit_percentage(self, data):
        """
        Calculate the current active trade profit percentage for a specific stock.

        Args:
            data (bt.feeds): The data feed for the specific stock.

        Returns:
            float: Profit percentage of the current active trade. None if no trade is active.
        """
        # Get the position size for the specific stock
        position = self.broker.getposition(data)
        if position.size == 0:  # No active position for this stock
            return None

        # Calculate the entry price and current price
        entry_price = position.price  # Entry price
        current_price = data.close[0]  # Current closing price

        # Calculate profit percentage
        profit_percentage = ((current_price - entry_price) / entry_price) * 100
        return profit_percentage

    def get_trade_target_price(self, data, target_profit_percentage=1):
        """
        Calculate the price where the profit percentage would reach the specified value for a specific stock.

        Args:
            data (bt.feeds): The data feed for the specific stock.
            target_profit_percentage (float): Desired profit percentage.

        Returns:
            float: The target price to achieve the specified profit percentage. None if no trade is active.
        """
        # Get the position size for the specific stock
        position = self.broker.getposition(data)
        if position.size == 0:  # No active position for this stock
            return None

        # Get the entry price
        entry_price = position.price

        # Calculate the target price
        target_price = entry_price * (1 + target_profit_percentage / 100)
        return target_price
