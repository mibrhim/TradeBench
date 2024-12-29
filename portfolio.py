import os
import yfinance as yf
import backtrader as bt
import pandas as pd

from helper.utlis import clear_folder


class PortfolioFactory:
    # _start_date = '1900-01-01'
    # _end_date = '2100-01-01'

    # Existing Portfolio Types
    SPY_STOCK = 0
    SINGLE_STOCK = 20
    OLD_STOCKS = 1
    NEW_STOCK = 2
    TECHNOLOGY_STOCK = 3
    SAMPLE_STOCKS = 4
    ALL_STOCKS = 5
    S_AND_P_500 = 17  # New portfolio type for S&P 500

    # New Portfolio Types for Different Sectors
    TECHNOLOGY = 6
    HEALTHCARE = 7
    FINANCIALS = 8
    CONSUMER_DISCRETIONARY = 9
    ENERGY = 10
    INDUSTRIALS = 11
    CONSUMER_STAPLES = 12
    UTILITIES = 13
    REAL_ESTATE = 14
    MATERIALS = 15
    COMMUNICATION_SERVICES = 16

    TOP_US_STOCKS = 18  # New portfolio type for Top US Stocks

    @staticmethod
    def make(portfolio_type, _start_date='1900-01-01', _end_date='2100-01-01'):

        stock_symbols = ['SPY']  # Default portfolio is SPY if nothing matches

        match portfolio_type:
            case PortfolioFactory.SAMPLE_STOCKS:
                stock_symbols = ['MSFT', 'MED', 'AMD']
            case PortfolioFactory.OLD_STOCKS:
                stock_symbols = ['MSFT', 'INTC', 'AMZN', 'AAPL', 'NVDA', 'XOM', 'MED', 'PFE', 'KO', 'DVN', 'JNJ',
                                 'GE', 'MNST', 'MMM', 'CVX', 'PG', 'COST', 'ADBE', 'PEP', 'CALM', 'RIO', 'NKE', 'CAT']
            case PortfolioFactory.NEW_STOCK:
                stock_symbols = ['AMD', 'ADM', 'EQR', 'WMT', 'MRK', 'QCOM', 'RIO', 'TSLA', 'V', 'STLA', 'AVGO', 'GOOG',
                                 'DHT', 'GNK']
            case PortfolioFactory.TECHNOLOGY_STOCK:
                stock_symbols = ['MSFT', 'INTC', 'AMZN', 'AAPL', 'NVDA', 'ADBE', 'AMD', 'AVGO', 'GOOG']
            case PortfolioFactory.ALL_STOCKS:
                stock_symbols = [
                    # Existing Stocks
                    'MSFT', 'INTC', 'AMZN', 'AAPL', 'NVDA', 'XOM', 'MED', 'PFE', 'KO', 'DVN', 'JNJ',
                    'GE', 'MNST', 'MMM', 'CVX', 'PG', 'COST', 'ADBE', 'PEP', 'CALM', 'RIO', 'NKE', 'CAT',
                    'AMD', 'ADM', 'EQR', 'WMT', 'MRK', 'QCOM', 'RIO', 'TSLA', 'V', 'STLA', 'AVGO', 'GOOG',
                    'DHT', 'GNK',
                    # Technology
                    'AAPL', 'MSFT', 'NVDA', 'TSM', 'AVGO',
                    # Healthcare
                    'JNJ', 'PFE', 'MRK', 'UNH', 'TMO',
                    # Financials
                    'JPM', 'BAC', 'WFC', 'C', 'GS',
                    # Consumer Discretionary
                    'AMZN', 'TSLA', 'HD', 'NKE', 'MCD',
                    # Energy
                    'XOM', 'CVX', 'COP', 'SLB', 'EOG',
                    # Industrials
                    'BA', 'CAT', 'GE', 'UNP', 'MMM',
                    # Consumer Staples
                    'PG', 'KO', 'PEP', 'WMT', 'COST',
                    # Utilities
                    'NEE', 'DUK', 'SO', 'D', 'AEP',
                    # Real Estate
                    'PLD', 'AMT', 'CCI', 'SPG', 'PSA',
                    # Materials
                    'LIN', 'APD', 'SHW', 'NEM', 'FCX',
                    # Communication Services
                    'GOOGL', 'NFLX', 'DIS', 'T'
                ]
                # Remove duplicates
                stock_symbols = list(set(stock_symbols))
            case PortfolioFactory.S_AND_P_500:
                stock_symbols = PortfolioFactory.get_s_and_p_500_symbols()
                print(f"Portfolio Length: {len(stock_symbols)}")
            case PortfolioFactory.TECHNOLOGY:
                stock_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSM', 'AVGO']
            case PortfolioFactory.HEALTHCARE:
                stock_symbols = ['JNJ', 'PFE', 'MRK', 'UNH', 'TMO']
            case PortfolioFactory.FINANCIALS:
                stock_symbols = ['JPM', 'BAC', 'WFC', 'C', 'GS']
            case PortfolioFactory.CONSUMER_DISCRETIONARY:
                stock_symbols = ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD']
            case PortfolioFactory.ENERGY:
                stock_symbols = ['XOM', 'CVX', 'COP', 'SLB', 'EOG']
            case PortfolioFactory.INDUSTRIALS:
                stock_symbols = ['BA', 'CAT', 'GE', 'UNP', 'MMM']
            case PortfolioFactory.CONSUMER_STAPLES:
                stock_symbols = ['PG', 'KO', 'PEP', 'WMT', 'COST']
            case PortfolioFactory.UTILITIES:
                stock_symbols = ['NEE', 'DUK', 'SO', 'D', 'AEP']
            case PortfolioFactory.REAL_ESTATE:
                stock_symbols = ['PLD', 'AMT', 'CCI', 'SPG', 'PSA']
            case PortfolioFactory.MATERIALS:
                stock_symbols = ['LIN', 'APD', 'SHW', 'NEM', 'FCX']
            case PortfolioFactory.COMMUNICATION_SERVICES:
                stock_symbols = ['GOOGL', 'NFLX', 'DIS', 'T']
            case PortfolioFactory.SINGLE_STOCK:
                stock_symbols = ['AAPL']
            case PortfolioFactory.TOP_US_STOCKS:
                stock_symbols = PortfolioFactory.get_top_us_stocks()
                print(f"Top US Stocks Portfolio Length: {len(stock_symbols)}")


        return Portfolio(stock_symbols, _start_date, _end_date)

    @staticmethod
    def get_s_and_p_500_symbols(top_n=500):
        # Fetch the list of S&P 500 symbols from Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url, header=0)
        df = table[0]

        stock_symbols = df['Symbol'].tolist()
        
        print(f"Portfolio Length: {len(stock_symbols)}")
        return stock_symbols[:top_n]

    @staticmethod
    def get_top_us_stocks(top_n=500):
        # For demonstration, fetching "most active" stocks from Yahoo Finance
        url = 'https://stockanalysis.com/list/nyse-stocks/'
        table = pd.read_html(url)[0]
        
        stock_symbols = table['Symbol'].tolist()
        print(f"Top {top_n} Stocks: {stock_symbols[:top_n]}")
        
        return stock_symbols[:top_n]


class Portfolio:
    def __init__(self, symbols, start_date, end_date, data_folder='data'):
        self.symbols = symbols
        self.symbols.append("SPY")
        self.start_date = start_date
        self.end_date = end_date
        self.data_folder = data_folder
        self.stocks = []
        # clear_folder("data")
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        min_data_points = 300  # Example: Set the minimum number of data points required by your indicators

        for symbol in self.symbols:
            csv_file = os.path.join(self.data_folder, f"{symbol}.csv")

            # Check if the file exists
            if os.path.exists(csv_file):
                # Load existing data
                data = pd.read_csv(csv_file, index_col='Date', parse_dates=True)
                data_start = data.index.min()
                data_end = data.index.max()

                print(f"{symbol} {data_start}, {data_end}")
                print(f"{symbol} {pd.to_datetime(self.start_date)}, {pd.to_datetime(self.end_date)}")
                # Check if the data covers the required period
                if data_start == pd.to_datetime(self.start_date): # and data_end == pd.to_datetime(self.end_date):
                    print(f"Using existing data for {symbol} from {csv_file}")
                else:
                    # Re-download data if existing data doesn't cover the required period
                    print(f"Existing data for {symbol} doesn't cover the required period. Re-downloading...")
                    data = self.download_data(symbol, csv_file)
            else:
                # Download fresh data if CSV doesn't exist
                data = self.download_data(symbol, csv_file)

            # Skip if not enough data points
            if len(data) < min_data_points:
                print(f"Not enough data for {symbol} (only {len(data)} rows), skipping.")
                continue

            # Convert data to Backtrader's DataFeed format
            try:
                if data.index.min() == pd.to_datetime(self.start_date):
                    data_feed = bt.feeds.PandasData(dataname=data)
                    self.stocks.append(Stock(symbol, data_feed))
            except Exception as e:
                print(f"Error processing {symbol}: {e}, skipping.")

    def download_data(self, symbol, csv_file):
        """Download data from Yahoo Finance and save it as a CSV."""
        data = yf.download(symbol, start=self.start_date, end=self.end_date)

        # Skip if no data is returned
        if data.empty:
            print(f"No data found for {symbol}, skipping.")
            return data
        
        # Save the downloaded data to a CSV file
        data.to_csv(csv_file)
        print(f"Downloaded and saved data for {symbol} to {csv_file}")
        return data

    def get_stock(self, symbol):
        csv_file = os.path.join(self.data_folder, f"{symbol}.csv")

        # Check if the file exists
        if os.path.exists(csv_file):
            # Load data from the CSV file
            data = pd.read_csv(csv_file, index_col='Date', parse_dates=True)
            print(f"Loaded data for {symbol} from {csv_file}")
        else:
            # Download data from Yahoo Finance
            data = self.download_data(symbol, csv_file)

        return data


class Stock:
    def __init__(self, symbol, data_feed):
        self.symbol = symbol
        self.data = data_feed