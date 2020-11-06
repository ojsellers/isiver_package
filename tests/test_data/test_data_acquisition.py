"""
Unit testing for data_acquisition file and stock_dataframe class
"""


import unittest
import pandas as pd
from datetime import datetime, timedelta, date


from isiver_utils.data.data_acquisition import stock_dataframe


class test_dataframe(unittest.TestCase):

    def test_data(self, ticker='SMT_L'):
        """
        Fn to test stock_dataframe and the yfinance API is working
        - len(df) assertion is given range to account for bank holidays at the ends
        of the time periods
        """
        print('testing data...')
        start_date = str(date.today() - timedelta(days=210))
        df = stock_dataframe(ticker, start_date, pd.DataFrame()).new_stock_df()
        print(df)
        self.assertTrue(149<=len(df)<=151)
        self.assertEqual(len(df.columns), 13)
        print('...data test passed')


if __name__ == '__main__':
    unittest.main()
