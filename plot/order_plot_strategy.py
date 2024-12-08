import pandas as pd
import plotly.graph_objs as go

from plot.plot_strategy import PlotStrategy


class OrderPlotStrategy(PlotStrategy):
    def plot(self, fig, strategy, data, portfolio):
        ticker = data._name
        orders = pd.DataFrame(strategy.analyzers.logger.get_analysis()['orders'])
        if "stock" not in orders:
            return
        
        orders = orders[orders['stock'] == ticker]
        buy_orders = orders[orders['buy']]
        sell_orders = orders[~orders['buy']]

        fig.add_trace(go.Scatter(
            x=buy_orders['date'],
            y=buy_orders['price'],
            mode='markers+text',
            marker=dict(
                color='green',
                size=15,
                symbol='triangle-up'
            ),
            hovertext=[f"Size: {size}<br>Amount: ${amount:,.0f}<br>ID: {tradid}" for size, amount, tradid in
                        zip(buy_orders['size'], buy_orders['amount'], buy_orders['tradeid'])],
            hoverinfo='text',
            name='Buy Orders'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=sell_orders['date'],
            y=sell_orders['price'],
            mode='markers',
            marker=dict(
                color='red',
                size=15,
                symbol='triangle-down'
            ),
            hovertext=[f"Size: {size}<br>Amount: ${amount:,.0f}<br>ID: {tradid}" for size, amount, tradid in
                        zip(sell_orders['size'], sell_orders['amount'], sell_orders['tradeid'])],
            hoverinfo='text',
            name='Sell Orders'
        ), row=1, col=1)
