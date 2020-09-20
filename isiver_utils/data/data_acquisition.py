'''
@author = Ollie
- Added to Isiver repo on 29/07/2020.
- Script containing class and test function to download, clean, and update
pandas dataframes with stock prices from the yfinance API.
- Limitations of this API are that prives for some stock codes are lacking in
places and intraday frequency is not possible for download periods of >60 days.
'''

import yfinance as yf
from pandas_datareader import data as pdr
yf.pdr_override()
import pandas as pd
from datetime import datetime, timedelta, date

class stock_dataframe():
    def __init__(self, ticker, start_date, df):
        '''This class represents a dataframe that can be used to scrape up to
        date market data from yfinance api or perform cleaning and add columns
        :param ticker: the code used to represent the stock entered in form
                        suitable for SQL and adjusted here for yfinance
        :param start_date: date from which the market data should be gathered
                        can be set to None and will download past 5 years
        :param df: can input pre created dataframe to use clean and returns fns
        '''
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
        '''This fn used to clean downloaded data from yfinance
        - converts all prices to pence
        - inserts missing dates and resamples to business days
        - interpolates missing values'''
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
        '''Fn backtracks up column to update all prices to pence
        :param i: row from which backtracking should start (inclusive)
        :param j: column which needs backtracking
        :return: True or False depending on whether operation was successful'''
        try:
            for x in range(i + 1):
                self.df.iat[x, j] = self.df.iloc[x][j] * 100
        except:
            return False
        else:
            return True

    def returns(self):
        if 'Returns' in self.df:
            del self.df['Returns']
        self.df['Returns'] = ((self.df['AdjClose'].pct_change() + 1).cumprod())
        self.df.iat[0, len(self.df.columns) - 1] = 1
        return self.df

    def moving_averages(self, t_frame=50):
        '''Fn to create a new column in dataframe for moving averages of Returns
        :param t_frame: number of days over which moving average is taken
        :return: updated dataframe'''
        if 'ReturnsMA' in self.df:
            del self.df['ReturnsMA']
        self.df['ReturnsMA'] = self.df['Returns'].rolling(window=t_frame).mean()
        return self.df

    def pre_process(self, clean):
        if clean:
            self.clean_data()
        self.returns()
        self.moving_averages()
        return self.df

    def new_stock_df(self):
        self.download_data()
        return self.pre_process(True)

    def update_stock_df(self):
        '''Updates stock dataframe to include up to date prices'''
        old_df = self.df.copy()
        if 'Returns' in old_df:
            del old_df['Returns']
        if 'ReturnsMA' in old_df:
            del old_df['ReturnsMA']
        self.download_data()
        self.df = pd.concat([old_df, self.df])
        return self.pre_process(True)
