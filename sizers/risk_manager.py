
class RiskManager:
    _instance = None
    RISK_PER_UNIT = 1
    _max_total_active_units = 14
    _max_active_units_per_strategy = {"MomentumStrategy": 6, "SlowTurtleStrategy": 9, "TurtleCTStrategy":20, "MeanReversionRSIWithRanking": 10}
    _max_active_units_per_stock = 3


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RiskManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        if RiskManager._instance is None:
            return

        self._active_units = {}
        self._total_active_units = 0

    def add(self, strategy, data):
        # print(f"* [Added] Inside added {strategy.name}")
        if strategy.name not in self._active_units:
            self._active_units[strategy.name] = {}
        
        if data not in self._active_units[strategy.name]:
            self._active_units[strategy.name][data] = 0

        if not self.take_more(strategy, data):
            return False

        # print(f"** [Added] {self._total_active_units}, {self._active_units[strategy][data]}")
        self._active_units[strategy.name][data] += 1
        self._total_active_units += 1
        # print(f"- [Added] {self._total_active_units}, {self._active_units[strategy][data]}")


    def remove(self, strategy, data):

        # print(f"* [Removed] {self._total_active_units}, {self._active_units[strategy][data]}")
        self._total_active_units -= self._active_units[strategy.name][data]
        self._active_units[strategy.name][data] = 0
        # print(f"- [Removed] {self._total_active_units}, {self._active_units[strategy][data]}")

       

    def get_active_units(self):
        return self._total_active_units

    
    def take_more(self, strategy, data) -> bool:
        if strategy.name not in self._active_units:
            self._active_units[strategy.name] = {}
            return True
        
        if data not in self._active_units[strategy.name]:
            self._active_units[strategy.name][data] = 0
            return True


        # print(f"- [Take More] {self._total_active_units}, {self._active_units[strategy][data]}")
        # if self._total_active_units > 9:
        #     print(f'\n[Take more] Sum of {strategy.__class__.__name__}: {sum(self._active_units[strategy].values())}')
        #     print(f'[Take more] Sum of data {data._name}: {self._active_units[strategy][data]}')
        #     print(f'[Take more] Total Units {self._total_active_units}\n')

        # print(f"- [Take More] {strategy.name}: {sum(self._active_units[strategy.name].values())}, {RiskManager._max_active_units_per_strategy[strategy.name]}")
        if sum(self._active_units[strategy.name].values()) >= RiskManager._max_active_units_per_strategy[strategy.name]:
            return False
        
        if self._active_units[strategy.name][data] >= RiskManager._max_active_units_per_stock:
            return False
        
        if self._total_active_units >= RiskManager._max_total_active_units:
            return False
        
        return True