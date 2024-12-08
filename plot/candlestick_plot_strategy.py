import pandas as pd
import plotly.graph_objs as go

from plot.plot_strategy import PlotStrategy


class CandlestickPlotStrategy(PlotStrategy):
    def plot(self, fig, strategy, data, portfolio):
        # Extract stock data from the Portfolio
        ticker = data._name
        data_feed = portfolio.get_stock(ticker)
        df = pd.DataFrame(data_feed)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        ), row=1, col=1)
