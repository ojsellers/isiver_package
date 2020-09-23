'''
@author = Isaac

Simple test function to check class functionality outside of class module
'''
import data_acquisition
from datetime import date, timedelta
import pandas as pd

def test_df_output(ticker='SMT_L', history_days=200):
    '''
    Fn to generate stock class and print dataframe for of given ticker to
    command line, to inspect functionailty of preprocessing methods and fidelity
    of stock data.
    '''
    start_date = str(date.today() - timedelta(days=history_days))
    stock_class = data_acquisition.stock_dataframe(ticker, start_date,
                                                   pd.DataFrame())
    stock_class.new_stock_df()
    print(stock_class.df.tail(20))

test_df_output()
