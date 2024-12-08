# system_builder.py
from system.system import System


class SystemBuilder:
    def __init__(self, name=None):
        self._strategy = None
        self._name = name
        self._sizer = None
        self._params = {}
        self._opt_params = {}
        self._combine_flag = False
        self._portfolio = None

    def name(self, name):
        self._name = name
        return self

    def strategy(self, strategy):
        self._strategy = strategy
        return self

    def sizer(self, sizer):
        self._sizer = sizer
        return self

    def params(self, params):
        self._params = params
        return self

    def optimize(self, params):
        self._opt_params.update(params)
        return self

    def combine(self):
        self._combine_flag = True
        return self

    def portfolio(self, portfolio):
        self._portfolio = portfolio
        return self

    def build(self):
        if not self._strategy:
            raise ValueError("Strategy must be set")
        if not self._sizer:
            raise ValueError("Sizer must be set")

        return System(self._name, self._strategy, self._sizer, self._params, self._opt_params,
                      self._combine_flag, self._portfolio)
