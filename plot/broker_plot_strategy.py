import plotly.graph_objs as go
import pandas as pd
from plot.plot_strategy import PlotStrategy

class BrokerPlotStrategy(PlotStrategy):
    def plot(self, fig, strategy, data, portfolio):
        # Get the analysis data from the custom analyzer
        analysis = strategy.analyzers.broker_analyzer.get_analysis()

        # Convert cash and value data to DataFrame
        df_analysis = pd.DataFrame({
            'Date': pd.to_datetime(analysis['datetime']),
            'Cash': analysis['cash'],
            'Value': analysis['value']
        })
        df_analysis.set_index('Date', inplace=True)

        # Plot the broker value line
        fig.add_trace(go.Scatter(
            x=df_analysis.index,
            y=df_analysis['Value'],
            mode='lines',
            name='Broker Value',
            line=dict(color='blue')
        ), row=3, col=1)

        # Plot the cash line
        fig.add_trace(go.Scatter(
            x=df_analysis.index,
            y=df_analysis['Cash'],
            mode='lines',
            name='Cash',
            line=dict(color='orange')
        ), row=3, col=1)

        # Prepare PnL data
        pnl_dates, pnl_values = zip(*analysis['pnl']) if analysis['pnl'] else ([], [])
        pnl_dates, trade_ids = zip(*analysis['trade_id']) if analysis['trade_id'] else ([], [])
        pnl_dates, stock_names = zip(*analysis['stock']) if analysis['stock'] else ([], [])

        current_stock_name = data._name  # Assuming this gives the name of the current stock data

        # Define marker colors for current and other data stocks
        marker_colors = [
            'green' if pnl > 0 and stock_name == current_stock_name else 'red' if stock_name == current_stock_name
            else 'lightgray' if pnl > 0 else 'darkgray'
            for pnl, stock_name in zip(pnl_values, stock_names)
        ]

        # Plot trade profit and loss as dots
        fig.add_trace(go.Scatter(
            x=pnl_dates,
            y=pnl_values,
            mode='markers',
            marker=dict(
                color=marker_colors,
                size=10,
                symbol='circle'
            ),
            hovertext=[f"Trade ID: {trade_id}<br>P&L: ${pnl:,.2f}<br>Stock: {stock_name}"
                for trade_id, pnl, stock_name in zip(trade_ids, pnl_values, stock_names)],
            hoverinfo='text',
            name='Trade P&L'
        ), row=2, col=1)


    @staticmethod
    def equity_curve(fig, strategy):
        # Get the analysis data from the custom analyzer
        analysis = strategy.analyzers.broker_analyzer.get_analysis()

        # Convert cash and value data to DataFrame
        df_analysis = pd.DataFrame({
            'Date': pd.to_datetime(analysis['datetime']),
            'Cash': analysis['cash'],
            'Value': analysis['value']
        })
        df_analysis.set_index('Date', inplace=True)

        fig.add_trace(go.Scatter(
            x=df_analysis.index,
            y=df_analysis['Value'],
            mode='lines', name=strategy.name,
            line=dict(width=2)
        ))
