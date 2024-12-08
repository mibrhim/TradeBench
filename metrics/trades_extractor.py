from metrics.metric_calculator import MetricsCalculator


class TradesExtractor:
    @staticmethod
    def extract_trades(results, systems):
        trades_data = []
        orders_data = []
        index = 0
        for strategy in results:
            for result in strategy:
                if not isinstance(result, list):  # In case of optimization, results will be a list of lists
                    result = [result]

                for strat in result:
                    logger = strat.analyzers.logger.get_analysis()
                    params = ""
                    if index < len(systems):
                        params = MetricsCalculator.print_optimized_params(systems[index], strat)

                    strategy_name = 'Unnamed Strategy'
                    if hasattr(strat, 'name'):
                        strategy_name = strat.name

                    for trade in logger['trades']:
                        trades_data.append({
                            'System': systems[index].get_name() if index < len(systems) else f"Combined Strategy", # ({strategy_name})",
                            'Params': params,
                            'Stock': trade['stock'],
                            'Trade ID': trade['trade_id'],
                            'Date In': trade['date_in'],
                            'Date Out': trade['date_out'],
                            'Size': trade['size'],
                            'PnL': trade['pnl'],
                            'Net PnL': trade['net_pnl'],
                            'orders': trade['orders']
                        })

                    for order in logger['orders']:
                        order["System"] = systems[index].get_name() if index < len(systems) else f"Combined Strategy" # ({strategy_name})"
                        orders_data.append(order)

                    trades_data = sorted(trades_data, key=lambda trade: (trade["Date Out"]), reverse=False)
                    orders_data = sorted(orders_data, key=lambda order: (order["date"]), reverse=False)
                    

            index += 1
        return trades_data, orders_data
