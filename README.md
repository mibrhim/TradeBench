## Trading System Backtester

An open-source platform designed to help stock traders test their trading strategies, share them with the community, and analyze detailed statistics and backtest reports. This project provides insightful visualizations and is a great starting point for strategy development and collaboration.


## Features

- Run backtests on trading strategies and view detailed reports.
- Analyze results through interactive visualizations.
- Easily add custom trading strategies by implementing a unified interface.
- Roadmap for future development into a full-stack web application.


## How to Use

1. **Install Dependencies**

   Before running the project, make sure to install the required Python packages. Use the following command:
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Run the Project**
 
   Execute the main script to perform a backtest:
   ```bash
   python main.py
   ```
   
4. **View Results**

   After running the backtest, open the following files in your browser to view the results:
   - `index.html`: For a visual representation of the backtest.
   - `backtest_summary.html`: For a detailed backtest summary.


## Contribution Guidelines

We welcome contributions from developers, traders, and enthusiasts! Here's how you can get started:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

Feel free to suggest improvements, report bugs, or enhance the documentation.


## Adding New Strategies

Developers can add new trading strategies by inheriting the `Strategy` class and implementing it's absract methods
Ensure your strategy follows the framework's guidelines and is thoroughly tested before contributing.


## Next Steps

We envision this project evolving into a robust, user-friendly web platform. Here are our immediate action items:

1. **Framework Migration**  
   - Transition the backend to the **Django Python framework** to leverage its scalability and flexibility.
   - Replace the current HTML files with a **Single Page Application (SPA)** built using modern frameworks like **Angular** or **React**.

2. **Code Cleanup**  
   - Refactor the codebase for better modularity and maintainability.

3. **More Strategies**  
   - Expand the library of trading strategies to cater to a broader range of users and scenarios.

We’re excited to see this project grow with your contributions and feedback. Together, let’s build a powerful tool for the trading community!


## Contact

For questions, feedback, or collaboration opportunities, feel free to reach out through `mahmoud.ibrahim2590@gmail.com`
