# main.py
import backtrader as backtrader
from backtrader.sizers import AllInSizerInt

from portfolio import Portfolio, PortfolioFactory
from sizers.all_position_sizer import AllPositionSizer
from sizers.turtle_sizer import TurtleSizer
from strategies.mean_reversion.bollinger_bands import BollingerBandsStrategy
from strategies.mean_reversion.countertrend_turtle import TurtleCTStrategy
from strategies.mean_reversion.macd_divergence import MACDDivergenceStrategy
from strategies.mean_reversion.rsi_mean_reversion import MeanReversionRSIWithRanking
from strategies.mean_reversion.selloff_mean_reversion import SelloffMeanReversion
from strategies.trend_following.fast_turtle import FastTurtleStrategy
from strategies.trend_following.rotation_strategy import WeeklyRotationStrategy
from strategies.trend_following.slow_turtle import SlowTurtleStrategy
from strategies.trend_following.momentum_strategy import MomentumStrategy
from trader import Trader
from strategies.benchmarks.buy_and_hold import BuyAndHold
from system.system_builder import SystemBuilder


# test run dates
def main():
    start_date = '2014-10-01'
    # end_date = '1900-01-01'

    sp_portfolio = PortfolioFactory.make(PortfolioFactory.SPY_STOCK, _start_date=start_date)

    portfolio = PortfolioFactory.make(PortfolioFactory.S_AND_P_500, _start_date=start_date)

    # starting Trader
    trader = Trader(portfolio, 100000)
    trader.show_charts()

    # adding_benchmarks(trader, sp_portfolio)

    # add_fast_turtle(trader)
    add_slow_turtle(trader)
    # add_long_momentum(trader)

    # add_rotation_strategy(trader)


    # mean reversion
    # add_selloff_mr(trader)
    # add_rsi_mr(trader)
    # add_bollinger_mr(trader)
    # add_turtle_ct(trader)

    # add_macd_divergence(trader)

    

    # run trader
    trader.run(optimize=False, max_cpus=1, combine=False)



def add_rotation_strategy(trader):
    # 150,50 - 30 , 200
    strategy = SystemBuilder("Rotation Strategy") \
        .strategy(WeeklyRotationStrategy) \
        .optimize({'volume_filter': [50000000]}) \
        .optimize({'roc_period': [20, 50, 100]}) \
        .optimize({'dmi_filter': [True, False]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()
    # .optimize({"sma_trend": [100, 200]}) \

    trader.add_system(strategy)

def add_slow_turtle(trader):
    # 150,50 - 30 , 200
    slow_turtle = SystemBuilder("Slow Turtle") \
        .strategy(SlowTurtleStrategy) \
        .params({"entry": 100, "exit": 50, "stop_loss_atr_multiple": 4, "roc_period": 50}) \
        .optimize({"entry": [50, 100]}) \
        .optimize({"exit": [25, 50]}) \
        .optimize({"min_volume": [10000000, 50000000]}) \
        .optimize({"pyramidN": [1]}) \
        .optimize({"roc_period": [200]}) \
        .optimize({"stop_loss_atr_multiple": [4]}) \
        .sizer(TurtleSizer) \
        .combine() \
        .build()
    # .optimize({"sma_trend": [100, 200]}) \

    trader.add_system(slow_turtle)


def add_fast_turtle(trader):
    # 100,55 -
    fast_turtle = SystemBuilder("Fast Turtle") \
        .strategy(SlowTurtleStrategy) \
        .params({"entry": 20, "exit": 10}) \
        .optimize({"entry": [20]}) \
        .optimize({"exit": [10]}) \
        .optimize({"min_volume": [50000000]}) \
        .optimize({"roc_period": [50]}) \
        .optimize({"stop_loss_atr_multiple": [2]}) \
        .optimize({'dmi_filter': [True, False]}) \
        .sizer(TurtleSizer) \
        .combine() \
        .build()
    # .optimize({"sma_trend": [100, 200]}) \

    trader.add_system(fast_turtle)


def add_long_momentum(trader):
    # Build systems using SystemBuilder with parameter ranges for optimization
    long_momentum = SystemBuilder("Long Momentum") \
        .strategy(MomentumStrategy) \
        .params({"fast_sma": 50, "slow_sma": 100, "trailing_stop_pct": 0.15, "stop_loss_atr_multiple": 4}) \
        .optimize({"fast_sma": [25, 50],
                   "slow_sma": [50, 100],
                   "trailing_stop_pct": [0.15],
                   "stop_loss_atr_multiple": [4],
                   'roc_period': [50, 200],}) \
        .optimize({"min_volume": [10000000, 50000000]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()
    # "sma_trend": [100, 200]}) \

    trader.add_system(long_momentum)


def adding_benchmarks(trader, sp_portfolio):
    sp_holding = SystemBuilder("SP500 Holding").strategy(BuyAndHold) \
        .sizer(AllPositionSizer) \
        .portfolio(sp_portfolio) \
        .sizer(AllInSizerInt) \
        .build()

    # buy_and_hold = SystemBuilder("Buy & Hold").strategy(BuyAndHold) \
    #     .sizer(AllPositionSizer) \
    #     .build()

    # adding systems
    trader.add_system(sp_holding)
    # trader.add_system(buy_and_hold)


def add_selloff_mr(trader):
    test = SystemBuilder("Selloff Mean Reversion").strategy(SelloffMeanReversion) \
        .params({"drawdown": 12.5, "atr_dd": 3, "profit": 6}) \
        .optimize({"drawdown": [8, 12.5],
                   "atr_dd": [3],
                   "profit": [5, 6]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()

    # adding systems
    trader.add_system(test)


def add_rsi_mr(trader):
    test = SystemBuilder("RSI Mean Reversion").strategy(MeanReversionRSIWithRanking) \
        .params({"rsi_period": 14, "rsi_entry": 30, "rsi_exit": 70}) \
        .optimize({"rsi_period": [8, 12.5],
                   "rsi_entry": [30, 50],
                   "rsi_exit": [40, 50, 60]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()

    # adding systems
    trader.add_system(test)

def add_bollinger_mr(trader):
    test = SystemBuilder("Bollinger Band").strategy(BollingerBandsStrategy) \
        .params({"boll_period": 50, "boll_dev": 2}) \
        .optimize({"boll_period": [50, 100],
                   "boll_dev": [2, 3]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()


def add_macd_divergence(trader):
    test = SystemBuilder("MACD Divergence").strategy(MACDDivergenceStrategy) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()

    # adding systems
    trader.add_system(test)

def add_turtle_ct(trader):
    test = SystemBuilder("Turtle CT").strategy(TurtleCTStrategy) \
        .params({"up_level": 50, "down_level": 100}) \
        .optimize({"up_level": [50, 25],
                   "down_level": [50, 100]}) \
        .sizer(AllPositionSizer) \
        .combine() \
        .build()

    # adding systems
    trader.add_system(test)



if __name__ == "__main__":
    main()
