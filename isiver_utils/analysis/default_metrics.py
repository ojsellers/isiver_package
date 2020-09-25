'''
@author = Isaac

Module to provide calculation of default metrics for stock dataframes.
'''


def get_rolling_metric(df, column, metric, *windows):
    '''
    This will be generalised to allow the calculation of
    a rolling metric over different windows
    '''
    pass


def ma(df, *columns, windows=(20, 30, 50)):
    '''
    Generalised function to calculate and append a moving averages column

    :param column: string name of column to calculate moving averages for
    :param windows: args int of time windows (days) for moving averages
            to be calculated over
    '''
    for c in columns:
        for w in windows:
            check_columns(F'{c}_MA_{w}')
            df[f'{c}_MA_{w}'] = df[c].rolling(window=w).mean()
    return df


def exp_ma(df, *columns, windows=(12, 26)):
    '''
    Generalised function to calculate exponential moving averages for given
    column(s)
    '''
    for c in columns:
        for w in windows:
            check_columns(F'{c}_EMA_{w}')
            df[F'{c}_EMA_{w}'] = df[c].ewm(span=w).mean()
    return df


# def close_ma(df, windows=(20, 30, 50)):
#     '''
#     DEPRECATED
#     Function to calculate moving averages for close price.
#     '''
#     for w in windows:
#         check_columns(F'MA_{w}')
#         df[F'MA_{w}'] = df['Close'].rolling(window=w).mean()
#     return df
#
#
# def close_exp_ma(df, windows=(12, 26)):
#     '''
#     DEPRECATED
#     Function to calculate exponential moving averages for close price.
#     '''
#     for w in windows:
#         check_columns(F'EMA_{w}')
#         df[F'EMA_{w}'] = df['Close'].ewm(span=w).mean()
#     return df


def macd(df, *columns, windows=(12, 26)):
    '''
    Function to add moving average convergence divergence column to df.
    Default value uses 12 and 26 period ema's
    '''
    for c in columns:
        check_columns(F'{c}_MACD_{windows[0]}_{windows[1]}')
        if F'{c}_EMA_{windows[0]}' or F'{c}_EMA_{windows[1]}' not in df:
            exp_ma(df, c, windows=(windows[0], windows[1]))
        df[F'{c}_MACD_{windows[0]}_{windows[1]}'] = \
            df[F'{c}_EMA_{windows[0]}'] - df[F'{c}_EMA_{windows[1]}']


def bollinger(df, *columns, windows=(20,)):
    '''
    Fn to calculate upper and lower bollinger bands for stock close price
    '''
    for c in columns:
        for w in windows:
            check_columns(F'{c}_Boll_Upper_{w}', F'{c}_Boll_Lower_{w}')
            if F'{c}_MA_{w}' or F'{c}_MA_{w}_SD' not in df:
                ma(df, 'Close', windows=(w,))
                std(df, F'{c}_MA_{w}', windows=(w,))
            df[F'{c}_Boll_Upper_{w}'] = \
                df[F'{c}_MA_{w}'] + (2 * df[F'{c}_MA_{w}_SD'])
            df[F'{c}_Boll_Lower_{w}'] = \
                df[F'{c}_MA_{w}'] - (2 * df[F'{c}_MA_{w}_SD'])


def std(df, *columns, windows=(20,)):
    '''
    Function to calculate standard deviation of given column(s), over specified
    window.
    '''
    for c in columns:
        for w in windows:
            check_columns(df, F'{c}_SD')
            df[F'{c}_SD'] = df[c].rolling(window=w).std()
    return df


def get_def_metrics(df):
    '''
    Function to apply all above metrics to supplied stock dataframe.
    '''
    ma(df, 'Close')
    exp_ma(df, 'Close')
    macd(df, 'Close')
    bollinger(df, 'Close')
    std(df, 'Close_MA_20')
    return df


def check_columns(df, *columns):
    '''
    Fn to check if column exists already in dataframe and delete if
    true
    '''
    for column in columns:
        if column in df:
            del df[column]
