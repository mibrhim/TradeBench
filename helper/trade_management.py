class TradesManager:
    def __init__(self, strategy):
        self.trades = {}
        self.strategy = strategy.__name__

    def generate_trade_id(self, data_name):
        # Create a unique trade_id using a count
        count = len(self.trades.get((self.strategy, data_name), [])) + 1
        trade_id = f"{self.strategy}_{data_name._name}_{count}"
        return trade_id

    def add_trade(self, data_name):
        trade_id = self.generate_trade_id(data_name)
        self.trades.setdefault((self.strategy, data_name), []).append(0)
        return trade_id

    def add_position(self, data_name, position_size):
        trade_id = self.generate_trade_id(data_name)
        current_size = self.trades[(self.strategy, data_name)][-1]
        self.trades[(self.strategy, data_name)][-1] = current_size + position_size
        return trade_id

    def get_position(self, data_name):
        return self.trades[(self.strategy, data_name)][-1]

    def get_current_trade(self, data_name):
        count = len(self.trades.get((self.strategy, data_name), []))
        trade_id = f"{self.strategy}_{data_name._name}_{count}"
        return trade_id

    def close_trade(self, data_name):
        trades = self.trades.get((self.strategy, data_name), [])
        self.trades[(self.strategy, data_name)][-1] = 0

    def is_in_trade(self, data_name):
        # Check if the last trade is not closed
        if (self.strategy, data_name) not in self.trades:
            return False
        return self.trades[(self.strategy, data_name)][-1] > 0
