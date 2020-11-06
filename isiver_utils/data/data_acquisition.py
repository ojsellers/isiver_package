"""
Added to Isiver repo on 29/07/2020.

Script containing stock_dataframe class used to download, clean, and perform
single stock analysis with.

Limitations of yfinance API are that prices for some stock codes are lacking in
places and intraday frequency is not possible for download periods of >60 days.
"""


import yfinance as yf
from pandas_datareader import data as pdr
yf.pdr_override()
import pandas as pd
from datetime import datetime, timedelta, date
from isiver_utils.analysis import metrics


class stock_dataframe():
    def __init__(self, ticker, start_date, df):
        """
        This class represents a dataframe that can gather data from the
        yfinance API, clean, and perform single stock calcs.

        :param ticker: the code used to represent the stock entered in from
                        suitable for SQL and adjusted here for yfinance
        :param start_date: date from which the market data should be gathered
                        can be None and will download past 5 years
        :param df: can input existing dataframe to update
        """
        self.ticker = ticker.replace("_", ".")
        self.ticker = ''.join([i for i in self.ticker if not i.isdigit()])
        self.start_date = start_date
        self.df = df

    def download_data(self):
        if not self.start_date:
            self.start_date = datetime.today() - timedelta(days=1825)
        self.df = pdr.get_data_yahoo(self.ticker, self.start_date,
                                                            datetime.today())
        self.df.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']
        return self.df

    def clean_data(self):
        """
        This fn used to clean downloaded data from yfinance
        - converts all prices to pence
        - inserts missing dates and resamples to business days
        - interpolates missing values
        """
        for i in range(len(self.df) - 1):
            for j in range(len(self.df.columns) - 1):
                if (0.1 > self.df.iloc[i+1][j] / self.df.iloc[i][j]):
                    self.df.iat[i+1, j] = self.df.iloc[i+1][j] * 100
                elif (self.df.iloc[i+1][j] / self.df.iloc[i][j] > 10):
                    if not self.update_previous(i, j):
                        return False
        self.df = self.df.asfreq('D')
        self.df = self.df[self.df.index.dayofweek < 5]
        self.df = self.df.interpolate(method='spline', order=1)
        return self.df

    def update_previous(self, i, j):
        """
        Fn backtracks up column to update all prices to pence

        :param i: row from which backtracking should start (inclusive)
        :param j: column which needs backtracking
        :return: True or False depending on whether operation was successful
        """
        try:
            for x in range(i + 1):
                self.df.iat[x, j] = self.df.iloc[x][j] * 100
        except:
            return False
        else:
            return True

    def returns(self):
        """
        Creates a cumulative returns column and appends to stock dataframe
        """
        self.check_columns('Returns')
        self.df['Returns'] = ((self.df['AdjClose'].pct_change() + 1).cumprod())
        self.df.iat[0, len(self.df.columns) - 1] = 1
        return self.df

    def get_default_metrics(self):
        """
        Function to apply all above metrics to supplied stock dataframe
        """
        self.add_metric_column(metrics.moving_average, ['Returns', 'Close'],
                                (30,50), 'MA')
        self.add_metric_column(metrics.moving_average, ['Close'], (30,50), 'EMA')
        # metrics.macd(self.df, 'Close')
        # metrics.std(self.df, 'Close_MA_20')
        # metrics.bollinger(self.df, 'Close')
        # metrics.rsi(self.df, 'Close')
        return self.df

    def add_metric_column(self, metric, columns, windows, metric_col_name):
        """
        Generalised function to add columns to the dataframe based on a
        specified function

        :param metric: metric from metrics file e.g. metric.moving_average
        :param columns: list of column names to apply to
        :param windows: tuple of windows to calculate metric over
        :param metric_col_name: abreviation to be added to col name in df
                        e.g. 'MA''
        """
        for c in columns:
            for w in windows:
                self.check_columns(f'{c}_{metric_col_name}_{w}')
                self.df[f'{c}_{metric_col_name}_{w}'] = metric(self.df[c], w)
        return self.df

    def check_columns(self, *columns):
        """
        Fn to check if column exists already in dataframe and delete if
        true
        """
        for column in columns:
            if column in self.df:
                del self.df[column]
        return self.df

    def pre_process(self, clean):
        """
        Function to preprocess a dataframe by cleaning and calculating default
        metrics

        :param clean: bool True for clean
        """
        if clean:
            self.clean_data()
        self.returns()
        self.get_default_metrics()
        return self.df

    def new_stock_df(self):
        """
        Function to grab a new stock dataframe with default metrics
        """
        self.download_data()
        return self.pre_process(True)

    def update_stock_df(self):
        """
        Updates a current stock dataframe to up-to-date prices and recalcs
        default metrics
        """
        old_df = self.df.copy()
        self.download_data()
        self.df = pd.concat([old_df, self.df])
        return self.pre_process(True)
