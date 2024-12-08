import os

from metrics.print_html import print_html_report
from plot.broker_plot_strategy import BrokerPlotStrategy
from plot.candlestick_plot_strategy import CandlestickPlotStrategy
from plot.indicator_strategy import IndicatorPlotStrategy
from plot.order_plot_strategy import OrderPlotStrategy
from plotly.subplots import make_subplots  # Import make_subplots for creating subplots
import plotly.offline as pyo
import plotly.graph_objs as go



class ReportGenerator:
    plot_strategies = [
        CandlestickPlotStrategy(),
        OrderPlotStrategy(),
        IndicatorPlotStrategy(),
        BrokerPlotStrategy(),
        # Add more strategies here if needed
    ]

    def __init__(self):
        self.summary_html = ""
        self.chart_files = []

    def plot_stock_data(self, portfolio, results, systems):
        
        index = 0
        equity_fig = go.Figure()

        for result in results:
            if not isinstance(result, list):
                result = [result]

            for strategy in result:
                for data in strategy.datas:
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.01,
                        row_heights=[0.8, 0.1, 0.1],
                        subplot_titles=(
                            f'{data._name} Trading Data with Indicators',
                            'Cash / Value'
                        )
                    )

                    # apply strategies
                    for plot_strategy in ReportGenerator.plot_strategies:
                        plot_strategy.plot(fig, strategy, data, portfolio)

                    fig.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Price',
                        barmode='overlay'
                    )

                    fig.update_layout(
                        xaxis_rangeslider_visible=False,
                        yaxis=dict(autorange=True)
                    )

                    # Prepare the system's name and parameters
                    name = "Combined (" + str(strategy.name) + ")"
                    if index < len(systems):
                        name = systems[index].get_name()

                    strategy_name = name.lower().replace(" ", "_")
                    chart_filename = f'html/{data._name}_{strategy_name}_chart.html'
                    pyo.plot(fig, filename=chart_filename, auto_open=False)
                    self.chart_files.append(chart_filename)
                
                BrokerPlotStrategy.equity_curve(equity_fig, strategy)

            index += 1

        # Customize the layout of the equity curve figure
        equity_fig.update_layout(
            title='Equity Curve for All Strategies',
            xaxis_title='Date',
            yaxis_title='Equity Value',
            showlegend=True
        )

        # Save the combined equity curve plot as a single HTML file
        equity_chart_filename = 'html/equity_curve.html'
        pyo.plot(equity_fig, filename=equity_chart_filename, auto_open=False)
        self.chart_files.append(equity_chart_filename)


    def save_report(self):
        self.summary_html = "<html><head><title>Backtest Results Summary</title></head><body>"
        self.summary_html += "<h1>Backtest Results Summary</h1>"
        self.summary_html += "<ul>"

        for chart_file in self.chart_files:
            self.summary_html += f'<li><a target="_blank" href="{chart_file}">{os.path.basename(chart_file)}</a></li>'

        self.summary_html += "</ul></body></html>"
        with open('backtest_summary.html', 'w') as f:
            f.write(self.summary_html)


    @staticmethod
    def print_optimized_params(result):
        optimized_params = {param_name: param_value for param_name, param_value in result.params._getkwargs().items()}
        return ReportGenerator.dict_to_readable_string(optimized_params)

    @staticmethod
    def dict_to_readable_string(params_dict):
        formatted_pairs = [f"{key}({value})" for key, value in params_dict.items()]
        readable_string = ", ".join(formatted_pairs)
        return readable_string
