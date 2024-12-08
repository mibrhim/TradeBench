

from metrics.generate_home_page import generate_home_page
from metrics.generate_strategy_page import generate_strategy_page


class MetricsCalculator:
    
    def __init__(self, strategies=None):
        self.strategies = strategies if strategies else []
        self.annual_pnl = []
        self.sorted_metrics = None


    def add_metric(self, strategy):
        self.strategies.append(strategy)

    def extract_metrics(self, results, portfolio, systems):
        metrics = []
       
        index = 0
        print(f"Inside Extract Metrics")

        for strategy in results:
            for result in strategy:
                if not isinstance(result, list):  # In case of optimization, results will be a list of lists
                    result = [result]

                for strat in result:
                    params = ""
                    print(f"Inside result for strategy")
                    strategy_metrics = {}
                    strategy_pnl = {}

                    for strategy_instance in self.strategies:
                        calculated_metrics = strategy_instance.calculate(strat)
                        strategy_metrics.update(calculated_metrics)
                        
                        # If the strategy is for Annual PnL, store it separately for display
                        if 'AnnualPnL' in calculated_metrics:
                            strategy_pnl = calculated_metrics['AnnualPnL']

                    if index < len(systems):
                        params = self.print_optimized_params(systems[index], strat)
                        strategy_metrics['System'] = systems[index].get_name()
                        strategy_metrics['Params'] = params
                    else:
                        strategy_metrics['System'] = 'Combined Strategy'
                        strategy_metrics['Params'] = params

                    metrics.append(strategy_metrics)
                    if strategy_pnl:
                        self.annual_pnl.append({'System': strategy_metrics['System'], 'AnnualPnL': strategy_pnl})

            index += 1

        self.sorted_metrics = sorted(metrics, key=lambda x: (x['MAR'], x['Sharpe Ratio'], x['CAGR']), reverse=True)


    @staticmethod
    def print_optimized_params(system, result):
        optimized_params = {param: getattr(result.params, param) for param in system.opt.keys()}

        if len(optimized_params) < 1:
            optimized_params = {param_name: param_value for param_name, param_value in result.params._getkwargs().items()}

        return MetricsCalculator.dict_to_readable_string(optimized_params)
    

    @staticmethod
    def dict_to_readable_string(params_dict):
        # Create a list of formatted key-value pairs
        formatted_pairs = [f"{key}({value})" for key, value in params_dict.items()]

        # Join the pairs into a single string with new lines
        readable_string = ", ".join(formatted_pairs)

        return readable_string
    

    def generate_html_report(self, trades_data, orders_data):
        # Step 1: Generate the home page with links to strategy pages
        home_html = generate_home_page(self.sorted_metrics)

        # Step 2: Generate individual pages for each strategy
        for metrics in self.sorted_metrics:
            system_name = metrics['System']
            system_trades = [trade for trade in trades_data if trade['System'] == system_name]
            system_orders = [order for order in orders_data if order['System'] == system_name]
            system_pnl = [pnl for pnl in self.annual_pnl if pnl['System'] == system_name]
            strategy_html = generate_strategy_page(metrics, system_trades, system_pnl, system_orders)
            file_name = f'html/{system_name.replace(" ", "_").lower()}_report.html'
            with open(file_name, 'w') as f:
                f.write(strategy_html)
            
        return home_html


    def save(self, trades_data, orders_data):
        # Step 1: Generate and save the home page
        home_html = self.generate_html_report(trades_data, orders_data)
        with open('index.html', 'w') as f:
            f.write(home_html)
