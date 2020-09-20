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
