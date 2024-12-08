def generate_strategy_page(performance_metrics, trades_data, annual_pnl_data, orders_data):
    html = f"""
    <html>
    <head>
        <title>{performance_metrics['System']} Detailed Report</title>"""
    html += """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f9;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                border: 1px solid #ddd;
                text-align: center;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            .negative {
                color: darkred;
            }
            .sell-order {
                background-color: #ffdddd!important;
            }
        </style>
    </head>"""
    
    html += f"""
    <body>
        <h1>{performance_metrics['System']} Detailed Report</h1>
        <h2>Performance Metrics</h2>
        <table>
            <tr>
                <th>CAGR</th>
                <th>Max Drawdown</th>
                <th>Longest Drawdown</th>
                <th>Annual Volatility</th>
                <th>Sharpe Ratio</th>
                <th>MAR</th>
                <th>Win(%)</th>
                <th>Win/Loss</th>
                <th>Trades Count</th>
                <th>Average Days in Trade</th>
                <th>Total Return</th>
            </tr>
            <tr>
                <td>{performance_metrics['CAGR']:.2f}%</td>
                <td>{performance_metrics['Max Drawdown']:.2f}%</td>
                <td>{performance_metrics['Longest Drawdown']:.2f}</td>
                <td>{performance_metrics['Annual Volatility']:.2f}%</td>
                <td>{performance_metrics['Sharpe Ratio']:.2f}</td>
                <td>{performance_metrics['MAR']:.2f}</td>
                <td>{performance_metrics['Win(%)']:.2f}</td>
                <td>{performance_metrics['Win/Loss']:.2f}</td>
                <td>{performance_metrics['Trades']:.2f}</td>
                <td>{performance_metrics['Average Days in Trade']:.2f}</td>
                <td>{performance_metrics['Total Return']:.2f}%</td>
            </tr>
        </table>"""
    
    html += f"""<h2>Other Metrics</h2>
        <table>
            <tr>
                <th>Win Streak</th>
                <th>Loss Streak</th>
            </tr>
            <tr>
                <td>{performance_metrics['Win Streak']:.0f}</td>
                <td>{performance_metrics['Loss Streak']:.0f}</td>
            </tr>
        </table>"""
    
    html += """
        <h2>Monthly / Yearly Profit and Loss</h2>"""

    sorted_months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    for pnl_data in annual_pnl_data:
        system = pnl_data['System']
        pnl_data = pnl_data['AnnualPnL']

        html += f"""
        <h3>{system}</h3>
        <table>
        <tr>
            <th>Year</th>"""

        for index, month in sorted_months.items():
            html += f"<th>{month}</th>"
        
        html += """
            <th>Yearly</th>
        </tr>"""

        for year, months_data in pnl_data.items():
            html += f"<tr><td>{year}</td>"
            for month in sorted_months.keys():
                pnl_value = months_data.get("months", {}).get(month, 0)
                # Apply dark red color for negative values
                pnl_class = "negative" if pnl_value < 0 else ""
                html += f"<td class='{pnl_class}'>{pnl_value:.2f}%</td>"
            html += f"<td>{months_data['pnl']:.2f}%</td></tr>"

        html += "</table>"

    html += f"""
    <h2>Executed Trades</h2>
    <table>
        <tr>
            <th>Stock</th>
            <th>Trade ID</th>
            <th>Date In</th>
            <th>Date Out</th>
            <th>PnL</th>
            <th>Net PnL</th>
            <th>Orders</th>
        </tr>"""
    
    for trade in trades_data:
        html += f"""
            <tr>
                <td>{trade.get('Stock')}</td>
                <td>{trade.get('Trade ID')}</td>
                <td>{trade.get('Date In').strftime('%Y-%m-%d')}</td>
                <td>{trade.get('Date Out').strftime('%Y-%m-%d')}</td>
                <td class='{"negative" if trade.get("PnL", 0) < 0 else ""}'>{trade.get('PnL'):,.2f}</td>
                <td class='{"negative" if trade.get("Net PnL", 0) < 0 else ""}'>{trade.get('Net PnL'):,.2f}</td>
                <td>
                    <table>"""

        # Display orders related to this trade
        if 'orders' in trade and trade['orders']:
            html += """<tr>
                            <td>Date</td>
                            <td>Size</td>
                            <td>Price</td>
                            <td>Amount</td>
                            <td>Commission</td>
                        </tr>"""
            for order in trade['orders']:
                order_date = order.get('date', 'N/A').strftime('%Y-%m-%d') if order.get('date') else 'N/A'
                html += f"""
                        <tr>
                            <td>{order_date}</td>
                            <td>{order.get('size'):,}</td>
                            <td>{order.get('price'):,.2f}</td>
                            <td>{order.get('amount'):,.0f}</td>
                            <td>{order.get('commission')}</td>"""
            html += "</tr>"
            html += """</table>
            </td>
        </tr>"""

    html += """
        </table>
        """

    html += """
        <h2>Executed Orders</h2>
        <table>
            <tr>
                <th>Stock</th>
                <th>Trade ID</th>
                <th>Date</th>
                <th>Active</th>
                <th>Size</th>
                <th>Price</th>
                <th>Amount</th>
                <th>Order Type</th>
            </tr>"""

    for order in orders_data:
        order_type = 'Buy' if order.get('size', 0) > 0 else 'Close'
        order_class = 'sell-order' if not order.get('buy') else ''
        html += f"""
            <tr class="{order_class}">
                <td>{order.get('stock')}</td>
                <td>{order.get('tradeid')}</td>
                <td>{order.get('date').strftime('%Y-%m-%d')}</td>
                <td>{order.get('active')}</td>
                <td>{order.get('size')}</td>
                <td>{order.get('price'):.2f}</td>
                <td>{order.get('amount'):.2f}</td>
                <td>{order_type}</td>
            </tr>"""

    html += """
        </table>"""

    html += """
    </body>
    </html>"""

    return html
