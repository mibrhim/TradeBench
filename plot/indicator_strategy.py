import pandas as pd
import plotly.graph_objs as go
import backtrader as bt

from plot.plot_strategy import PlotStrategy


class IndicatorPlotStrategy(PlotStrategy):
    def plot(self, fig, strategy, data, portfolio):
        ticker = data._name
        added_indicators = set()

        for attr_name in dir(strategy):
            attr = getattr(strategy, attr_name)

            if not isinstance(attr, dict):
                continue

            for data_feed, indicator in attr.items():
                if not isinstance(data_feed, bt.feeds.pandafeed.PandasData):
                    continue

                if not isinstance(indicator, bt.Indicator):
                    continue

                if data_feed._name != ticker:
                    continue

                ind_params = {
                    k: v for k, v in indicator.params._getkwargs().items()
                    if isinstance(v, (int, float))
                }
                ind_key = f'{indicator.__class__.__name__} ({", ".join([f"{k}={v}" for k, v in ind_params.items()])})'

                if ind_key in added_indicators:
                    continue

                added_indicators.add(ind_key)

                # Get stock data from the Portfolio
                stock_data = portfolio.get_stock(ticker)
                df = pd.DataFrame(stock_data)
                df.reset_index(inplace=True)
                df.rename(columns={'index': 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)

                # Loop through all lines of the indicator
                for i, line in enumerate(indicator.lines):
                    line_name = f"line_{i}"
                    ind_values = list(line.array)

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=ind_values,
                        mode='lines',
                        name=f'{ind_key} - {line_name}'
                    ), row=1, col=1)

