'''
@author = Isaac

Contains functions to download (via data_acquisition) and pickle stock classes,
for ease of access.
'''
import pickle
import pandas as pd
import data_acquisition
from datetime import date, timedelta


def pickle_stock_class(ticker, history_days, outdir):
    '''
    Function to download and preprocess a stock via data_acquisition, and pickle
    to given directory.
    '''
    start_date = str(date.today() - timedelta(days=history_days))
    stock_class = data_acquisition.stock_dataframe(ticker, start_date, pd.DataFrame())
    stock_class.new_stock_df()
    stock_class.pre_process(True)
    pickle.dump(stock_class, open(outdir+'example_data_class.pkl', 'wb'))


pickle_stock_class('SMT_L', 200, 'examples/')
