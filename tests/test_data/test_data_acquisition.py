'''
unit tests for data_acquisition file and stock_dataframe class
'''

from isiver_utils.data.data_acquisition import stock_dataframe
from datetime import datetime, timedelta, date
import pandas as pd

def test_data(ticker='SMT_L'):
    '''Fn to test stock_dataframe and the yfinance API is working
    - len(df) assertion is given range to account for bank holidays at the ends
    of the time periods'''
    print('testing data...')
    start_date = str(date.today() - timedelta(days=210))
    df = stock_dataframe(ticker, start_date, pd.DataFrame()).new_stock_df()
    assert(149<=len(df)<=151)
    assert(len(df.columns)) == 8
    print('...data test passed')
    return ticker, df, start_date

def test_df_output(ticker='SMT_L', history_days=200):
    '''
    Fn to generate stock class and print dataframe for of given ticker to
    command line, to inspect functionailty of preprocessing methods and fidelity
    of stock data.
    '''
    start_date = str(date.today() - timedelta(days=history_days))
    stock_class = stock_dataframe(ticker, start_date, pd.DataFrame())
    stock_class.new_stock_df()
    print(stock_class.df.tail(20))

test_df_output()
