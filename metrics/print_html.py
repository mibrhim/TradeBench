def print_html_report(performance_metrics, trades_data, annual_pnl_data):
    html = """
    <html>
    <head>
        <title>Backtest Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f9;
            }
            h1, h2 {
                color: #333;
                text-align: center;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: #fff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
            td {
                color: #555;
            }
            .collapsible {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                padding: 10px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 15px;
            }
            .active, .collapsible:hover {
                background-color: #45a049;
            }
            .content {
                padding: 0 18px;
                display: block;
                overflow: hidden;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>Backtest Performance Metrics</h1>
        <table>
            <tr>
                <th>System</th>
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
            </tr>"""

    for metrics in performance_metrics:
        html += f"""
            <tr>
                <td><b>{metrics['System']}</b></br>{metrics['Params']}</td>
                <td>{metrics['CAGR']:.2f}%</td>
                <td>{metrics['Max Drawdown']:.2f}%</td>
                <td>{metrics['Longest Drawdown']:.2f}</td>
                <td>{metrics.get('Annual Volatility', 0):.2f}%</td>
                <td>{metrics['Sharpe Ratio']:.2f}</td>
                <td>{metrics.get('MAR', 0):.2f}</td>
                <td>{metrics.get('Win(%)', 0):.2f}</td>
                <td>{metrics.get('Win/Loss', 0):.2f}</td>
                <td>{metrics.get('Trades', 0):.2f}</td>
                <td>{metrics.get('Average Days in Trade', 0):.2f}</td>
                <td>{metrics['Total Return']:.2f}%</td>
            </tr>"""

    html += """
        </table>
        <h2>Executed Trades</h2>"""

    systems = set([trade['System'] for trade in trades_data])
    params = {trade['System']: trade['Params'] for trade in trades_data}

    for system in systems:
        html += f"""
        <button class="collapsible"><b>{system}</b> : {params[system]}</button>
        <div class="content">
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
            if trade['System'] == system:
                html += f"""
                <tr>
                    <td>{trade.get('Stock')}</td>
                    <td>{trade.get('Trade ID')}</td>
                    <td>{trade.get('Date In')}</td>
                    <td>{trade.get('Date Out')}</td>
                    <td>{trade.get('PnL'):,.2f}</td>
                    <td>{trade.get('Net PnL'):,.2f}</td>
                    <td>
                    <table>"""

                # Display orders related to this trade
                if 'orders' in trade and trade['orders']:
                    html += """<tr>
                    <td>Date</td>
                    <td>Size</td>
                    <td>Price</td>
                    <td>Amount</td>
                    <td>Commission</td></tr>"""
                    for order in trade['orders']:
                        order_date = order.get('date', 'N/A').strftime('%Y-%m-%d %H:%M:%S') if order.get('date') else 'N/A'
                        html += f"""<tr>
                        <td>{order_date}</td>
                        <td>{order.get('size'):,}</td>
                        <td>{order.get('price'):,.2f}</td>
                        <td>{order.get('amount'):,.0f}</td>
                        <td>{order.get('commission')}</td>"""
                        html += "</tr>"

                html += """</table></td></tr>"""

        html += """
            </table>
        </div>"""

    html += """
    <h2>Annual Profit and Loss</h2>"""

    # Sort months based on calendar order
    sorted_months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    # Collect all unique months from annual_pnl_data
    for annual_pnl in annual_pnl_data:
        system = annual_pnl['System']
        pnl_data = annual_pnl['AnnualPnL']

        html += f"""
        <h3>{system}</h3>
        <table>
        <tr>
            <th>Year</th>"""

        # Add dynamic month headers
        for index, month in sorted_months.items():
            html += f"<th>{month}</th>"
        
        html += """
                <th>Yearly</th>
                </tr>"""

        # Populate rows with PnL data per year
        for year, months_data in pnl_data.items():
            html += f"<tr><td>{year}</td>"
            for month in sorted_months.keys():
                pnl_value = months_data.get("months", {}).get(month, 0)  # Get PnL for the month, 0 if not available
                html += f"<td>{pnl_value:.2f}%</td>"
            
            html += f"<td>{months_data['pnl']:.2f}</td>"
            html += "</tr>"

        html += """
        </table>
        </div>
    <script>
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            });
        }
    </script>
    </body>
    </html>"""

    return html
