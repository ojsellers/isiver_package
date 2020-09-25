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


def moving_averages(df, column):
    '''
    Generalised function to calculate and append a moving averages column

    :param column: string name of column to calculate moving averages for
    :param windows: args int of time windows (days) for moving averages
            to be calculated over
    '''
    df[f'{column}_MA_{w}'] = df[column].rolling(window=w).mean()
    return df


def exp_moving_averages(df, column):
    '''
    Generalised function to calculate exponential moving averages
    '''
    df[f'{column}_EMA_{w}'] = df['Close'].ewm(span=w).mean()
    return df


def close_ma(df, windows=(20, 30, 50)):
    '''
    DEPRECATED
    Function to calculate moving averages for close price.
    '''
    for w in windows:
        check_columns(F'MA-{w}')
        df[F'MA-{w}'] = df['Close'].rolling(window=w).mean()
    return df


def close_exp_ma(df, windows=(12, 26)):
    '''
    DEPRECATED
    Function to calculate exponential moving averages for close price.
    '''
    for w in windows:
        check_columns(F'EMA-{w}')
        df[F'EMA-{w}'] = df['Close'].ewm(span=w).mean()
    return df


def macd(df, windows=(12, 26)):
    '''
    Function to add moving average convergence divergence column to df.
    Default value uses 12 and 26 period ema's
    '''
    check_columns(F'MACD-{windows[0]}-{windows[1]}')
    if F'EMA-{windows[0]}' or F'EMA-{windows[1]}' not in df:
        close_exp_ma(df, windows=(windows[0], windows[1]))
    df[F'MACD-{windows[0]}-{windows[1]}'] = \
        df[F'EMA-{windows[0]}'] - df[F'EMA-{windows[1]}']


def bollinger(df, windows=(20,)):
    '''
    Fn to calculate upper and lower bollinger bands for stock close price
    '''
    for w in windows:
        check_columns(F'BollUpper-{w}', F'BollLower-{w}')
        if F'MA-{w}' or F'MASD-{w}' not in df:
            close_ma(df, (w,))
            ma_std(df, (w,))
        df[F'BollUpper-{w}'] = \
            df[F'MA-{w}'] + (2 * df[F'MASD-{w}'])
        df[F'BollLower-{w}'] = \
            df[F'MA-{w}'] - (2 * df[F'MASD-{w}'])


def ma_std(df, windows=(20,)):
    '''
    Fn to calculate standard deviation of close price for specified
    rolling windows
    '''
    for w in windows:
        check_columns(df, F'MASD-{w}')
        df[F'MASD-{w}'] = df['Close'].rolling(window=w).std()
    return df


def get_def_metrics(df):
    '''
    Function to apply all above metrics to supplied stock dataframe.
    '''
    print(df)
    close_ma(df)
    close_exp_ma(df)
    macd(df)
    ma_std(df)
    bollinger(df)
    return df


def check_columns(df, *columns):
    '''
    Fn to check if column exists already in dataframe and delete if
    true
    '''
    for column in columns:
        if column in df:
            del df[column]
