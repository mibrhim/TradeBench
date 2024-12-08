from datetime import datetime
from backtrader import Cerebro
import backtrader as bt
from backtrader.analyzers import SharpeRatio, DrawDown, Returns, TradeAnalyzer

from analyzers.broker_analyzer import BrokerAnalyzer
from analyzers.trades_logger import TradeLogger
from analyzers.volatility_analyzer import VolatilityAnalyzer
from commission.fixed_comission import FixedCommission
from helper.utlis import clear_folder
from metrics.metric_calculator import MetricsCalculator
from metrics.metrices_implementation import AnnualPnLStrategy, BasicCalculations, DrawdownCalculation
from metrics.trades_extractor import TradesExtractor
from plot.report_generator import ReportGenerator


class Trader:
    def __init__(self, portfolio, cash):
        self.portfolio = portfolio
        self.systems = []
        self.cash = cash
        self.optimize = False
        self.charts = False
        self.commission_info = FixedCommission()

    def add_system(self, system):
        self.systems.append(system)

    def run(self, optimize=False, max_cpus=None, combine=False):
        if max_cpus is None:
            max_cpus = 1  # Default to single-threaded unless specified

        self.optimize = optimize
        results = []

        for system in self.systems:
            cerebro = Cerebro() #(optdatas=True, preload=True, runonce=True)
            cerebro.broker.setcash(self.cash)
            cerebro.broker.set_slippage_perc(perc=0.01, slip_open=True)
            cerebro.broker.addcommissioninfo(self.commission_info)

            if optimize and system.has_optimize():
                system.optimize(cerebro)
            else:
                system.apply(cerebro)

            portfolio = system.get_portfolio() if system.get_portfolio() is not None else self.portfolio
            for stock in portfolio.stocks:
                cerebro.adddata(stock.data, stock.symbol)
                self._add_analyzers(cerebro)

            print(f"Data Feed Added To System {system.name}")

            result = cerebro.run(maxcpus=max_cpus) if optimize else cerebro.run()
            results.append(result)

        if not combine:
            self._generate_reports(results)
            return results

        cerebro = Cerebro() #(optdatas=True, preload=True, runonce=True)
        cerebro.broker.setcash(self.cash)
        cerebro.broker.set_slippage_perc(perc=0.01, slip_open=True)
        cerebro.broker.addcommissioninfo(self.commission_info)

        for system in self.systems:
            if system.is_combine():
                system.apply(cerebro)

        for stock in self.portfolio.stocks:
            cerebro.adddata(stock.data, stock.symbol)
            self._add_analyzers(cerebro)

        result = cerebro.run(maxcpus=max_cpus) if optimize else cerebro.run()
        results.append(result)

        self._generate_reports(results)

        return results

    def _add_analyzers(self, cerebro):
        cerebro.addanalyzer(SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(DrawDown, _name='drawdown')
        cerebro.addanalyzer(Returns, _name='returns')
        cerebro.addanalyzer(TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(TradeLogger, _name='logger')
        cerebro.addanalyzer(BrokerAnalyzer, _name='broker_analyzer')
        cerebro.addanalyzer(VolatilityAnalyzer, _name='volatility_analyzer')
        # Add the TimeReturn analyzer to get monthly and yearly returns
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn', timeframe=bt.TimeFrame.Months)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='yearly_return', timeframe=bt.TimeFrame.Years)


    def _generate_reports(self, results):
        clear_folder("html")

        # Calculate metrics
        metrics_calculator = MetricsCalculator()
        trade_extractor = TradesExtractor()
        metrics_calculator.add_metric(BasicCalculations())
        metrics_calculator.add_metric(DrawdownCalculation())
        metrics_calculator.add_metric(AnnualPnLStrategy())
    

        metrics_calculator.extract_metrics(results, self.portfolio, self.systems)
        trades_data, orders_data = trade_extractor.extract_trades(results, self.systems)
        metrics_calculator.save(trades_data, orders_data)

        # Generate and save reports
        report_generator = ReportGenerator()

        if not self.optimize and self.charts:
            report_generator.plot_stock_data(self.portfolio, results, self.systems)
            report_generator.save_report()

    def show_charts(self):
        self.charts = True
