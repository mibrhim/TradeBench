import backtrader as bt

from strategies.strategy import Strategy

class MACDDivergenceStrategy(Strategy):
    params = (
        ('stop_loss_atr_multiple', 2),
    )

    def _indicators(self):
        self.macd_histo = {d: bt.indicators.MACDHisto(d) for d in self.datas}
        
        # Track lows for divergence
        self.prev_macd_low = {d: [0, 0] for d in self.datas}
        self.prev_price_low = {d: [0, 0] for d in self.datas}
        self.macd_up = {d: False for d in self.datas}

            

    def _filter(self, data):
        return all([
                    # self.macd_histo[data][0] < 0,
                ])


    def _rank(self, datas):
        # return sorted(datas, key=lambda d: (self.rsi[d], -self.roc[d]), reverse=False)  # Sort by RSI (lowest RSI first)
        # return sorted(datas, key=lambda d: (self.rsi[d]), reverse=False)  # Sort by RSI (lowest RSI first)
        return datas
    

    # ---------------
    # set up condition
    def _setup(self, stock) -> bool:

        # if self.macd_histo[stock][0] > self.macd_histo[stock][-1]:
        #     self.macd_up[stock] = True


        if self.macd_histo[stock][0] > 0:# self.macd_histo[stock][-1] and self.macd_up[stock]:
            self.prev_macd_low[stock].append(0)
            self.prev_price_low[stock].append(stock.close[0])
            self.macd_up[stock] = False
            
        # Update lows
        if self.macd_histo[stock][0] < self.prev_macd_low[stock][-1]: # and not self.macd_up[stock]:  # MACD histogram forms a low
            self.prev_macd_low[stock][-1] = self.macd_histo[stock][0]
        
        if stock.close[0] < self.prev_price_low[stock][-1]: # and not self.macd_up[stock]:  # Price makes a lower low
            self.prev_price_low[stock][-1] = stock.close[0]

        return all([
            self.prev_macd_low[stock][-2] > self.prev_macd_low[stock][-1] , # >  self.prev_macd_low[stock][-2] * 0.1,
            self.prev_price_low[stock][-1] > self.prev_price_low[stock][-2], # > self.prev_price_low[stock][-1] * 0.1,
        ])


    def _stop_loss(self, order) -> int:
        return order.executed.price - (self.p.stop_loss_atr_multiple * self.atr[order.data][0])


    # ---------------
    # no exit required here
    def _exit(self, stock) -> bool:  
        return any([
                self.macd_histo[stock][0] < self.macd_histo[stock][-1],
            ])