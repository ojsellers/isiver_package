"""
@author = Isaac

Contains functions to download (via data_acquisition) and pickle stock classes,
for ease of access.
"""


import pickle
import pandas as pd
from isiver_utils.data import stock_dataframe
from datetime import date, timedelta


def pickle_stock_class(ticker, history_days, outdir):
    """
    Function to download and preprocess a stock via data_acquisition, and pickle
    to given directory.
    """
    out_loc = f'{outdir}/{ticker}-h-{history_days}-{date.today()}.pkl'
    start_date = str(date.today() - timedelta(days=history_days))
    stock_class = stock_dataframe(ticker, start_date, pd.DataFrame())
    stock_class.new_stock_df()
    stock_class.pre_process(True)
    pickle.dump(stock_class, open(out_loc, 'wb'))
