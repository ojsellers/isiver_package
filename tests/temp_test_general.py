"""
@author = Isaac

Simple test function to check class functionality outside of class module
"""


from datetime import date, timedelta
import pandas as pd


from isiver_utils.data import stock_dataframe
from isiver_utils.plotting import visualisation


def test_df_output(ticker='SMT_L', history_days=200):
    """
    Fn to generate stock class and print dataframe for of given ticker to
    command line, to inspect functionailty of preprocessing methods and fidelity
    of stock data.
    """
    start_date = str(date.today() - timedelta(days=history_days))
    stock_class = stock_dataframe(ticker, start_date,
                                                   pd.DataFrame())
    stock_class.new_stock_df()
    print(stock_class.df.tail(20))
    return stock_class


def test_visualisation(stock_class):
    """
    Fn to test the output of visualisation.py
    """
    visualisation.daily_ohlcv(stock_class, save_fig=False, output_window=True)


if __name__ == '__main__':
    stock_class = test_df_output()
    test_visualisation(stock_class)
