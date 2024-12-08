def generate_home_page(performance_metrics):
    html = """
    <html>
    <head>
        <title>Backtest Summary Report</title>
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
        </style>
    </head>
    <body>
        <h1>Backtest Summary Report</h1>
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
                <th>Detailed Report</th>
            </tr>"""

    for metrics in performance_metrics:
        system_name = metrics['System']
        html += f"""
            <tr>
                <td><b>{metrics['System']}</b></br>{metrics['Params']}</td>
                <td>{metrics['CAGR']:.2f}%</td>
                <td>{metrics['Max Drawdown']:.2f}%</td>
                <td>{metrics['Longest Drawdown']:.2f}</td>
                <td>{metrics['Annual Volatility']:.2f}%</td>
                <td>{metrics['Sharpe Ratio']:.2f}</td>
                <td>{metrics['MAR']:.2f}</td>
                <td>{metrics['Win(%)']:.2f}</td>
                <td>{metrics['Win/Loss']:.2f}</td>
                <td>{metrics['Trades']:.2f}</td>
                <td>{metrics['Average Days in Trade']:.2f}</td>
                <td>{metrics['Total Return']:.2f}%</td>
                <td><a target="_blank" href="html/{system_name.replace(' ', '_').lower()}_report.html">View</a></td>
            </tr>"""

    html += """
        </table>
    </body>
    </html>"""

    return html
