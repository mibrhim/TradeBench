from collections import defaultdict
from datetime import datetime


class BaseMetric:
    def calculate(self, strategy):
        raise NotImplementedError("Subclasses should implement this method.")


class BasicCalculations(BaseMetric):
    def calculate(self, strategy):
        broker = strategy.analyzers.broker_analyzer.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
        volatility = strategy.analyzers.volatility_analyzer.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()

        
        cagr = broker.cagr if not isinstance(broker, dict) else broker['cagr']
        
        total_return = broker.total_return if not isinstance(broker, dict) else broker['total_return']

        total_trades = trades.total.closed if 'closed' in trades.total else 0
        won_trades = trades.won.total if 'won' in trades and 'total' in trades.won else 0
        win_percentage = (won_trades / total_trades * 100) if total_trades else 0
        avg_win_amount = trades.won.pnl.average if 'won' in trades and 'pnl' in trades.won else 0
        avg_loss_amount = trades.lost.pnl.average if 'lost' in trades and 'pnl' in trades.lost else 0
        win_loss_ratio = (avg_win_amount / abs(avg_loss_amount)) if avg_loss_amount else float('inf')
        average_days_in_trade = trades.len.average if 'len' in trades and 'average' in trades.len else 0
        annual_volatility = broker.annual_volatility if not isinstance(broker, dict) else broker['annual_volatility']
        
        # Access winning and losing streaks
        winning_streak = trades.streak.won.longest if 'streak' in trades and 'won' in trades.streak else 0
        losing_streak = trades.streak.lost.longest if 'streak' in trades and 'lost' in trades.streak else 0

        mar = (cagr) / drawdown.max.drawdown if drawdown.max.drawdown != 0 else float('inf')

        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0) or 0
        return {
                'CAGR': cagr, 
                'Sharpe Ratio': sharpe,
                'MAR': round(abs(mar), 2),
                'Win(%)': round(win_percentage, 2),
                'Win/Loss': round(win_loss_ratio, 2),
                'Win Streak': winning_streak,
                'Loss Streak': losing_streak,
                'Trades': round(total_trades, 2),
                'Annual Volatility': annual_volatility, #volatility['annual_volatility']),
                'Average Days in Trade': round(average_days_in_trade, 2),
                'Total Return': total_return,
            }

class DrawdownCalculation(BaseMetric):
    def calculate(self, strategy):
        drawdown = strategy.analyzers.drawdown.get_analysis()
        return {
                'Max Drawdown': drawdown.max.drawdown, 
                'Longest Drawdown': drawdown.max.len / 30.5
            }


class AnnualPnLStrategy(BaseMetric):
    def calculate(self, strategy):
        # Initialize a dictionary to store PnL and PnL % for each year and month
        annual_pnl = {}
        # Extract the results from the analyzers
        monthly_returns = strategy.analyzers.timereturn.get_analysis()
        yearly_returns = strategy.analyzers.yearly_return.get_analysis()

        for dt, ret in yearly_returns.items():
            year = dt.year
            annual_pnl[year] = {"pnl": ret* 100, "months": {}}

        for dt, ret in monthly_returns.items():
            year = dt.year
            month = dt.month
            
            # If the year isn't already in the dictionary, initialize it with "pnl" and "months"
            if year not in annual_pnl:
                annual_pnl[year] = {"pnl": 0, "months": {}}
            
            # Add the month and return to the "months" dictionary for that year
            annual_pnl[year]["months"][month] = ret * 100

        return {'AnnualPnL': annual_pnl}