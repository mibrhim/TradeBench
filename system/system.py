# system.py
class System:
    def __init__(self, name, strategy, sizer, params, opt, combine, portfolio):
        self.strategy = strategy
        self.sizer = sizer
        self.params = params
        self.name = name
        self.opt = opt
        self._combine_flag = combine
        self._portfolio = portfolio

    def apply(self, cerebro):
        # When adding the strategy to Cerebro, parameters will be optimized by Backtrader
        print(f"Adding System {self.name}")
        idx = cerebro.addstrategy(self.strategy,**self.params)
        cerebro.addsizer_byidx(idx, self.sizer)

    def optimize(self, cerebro):
        # Add the strategy to Cerebro with optimization parameters
        if self.opt:
            cerebro.optstrategy(self.strategy, **self.opt)
        else:
            raise "No optimization parameters provided"
        cerebro.addsizer(self.sizer)

    def has_optimize(self):
        return self.opt


    def is_combine(self):
        return self._combine_flag

    def get_portfolio(self):
        return self._portfolio

    def get_name(self):
        return self.name