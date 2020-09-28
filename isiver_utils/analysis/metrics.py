'''
Module to provide calculation of default metrics for stock dataframes.

TODO:
    - Exponential rsi
    - Deltas and mivng avg deltas
'''

from isiver_utils.data.data_acquisition import stock_dataframe
import numpy as np
import pandas as pd

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
            check_columns(f'{c}_MA_{w}')
            df[f'{c}_MA_{w}'] = df[c].rolling(window=w).mean()
    return df


def exp_ma(df, *columns, windows=(12, 26)):
    '''
    Generalised function to calculate exponential moving averages for given
    column(s)
    '''
    for c in columns:
        for w in windows:
            check_columns(f'{c}_EMA_{w}')
            df[f'{c}_EMA_{w}'] = df[c].ewm(span=w).mean()
    return df


# def close_ma(df, windows=(20, 30, 50)):
#     '''
#     DEPRECATED
#     Function to calculate moving averages for close price.
#     '''
#     for w in windows:
#         check_columns(f'MA_{w}')
#         df[f'MA_{w}'] = df['Close'].rolling(window=w).mean()
#     return df
#
#
# def close_exp_ma(df, windows=(12, 26)):
#     '''
#     DEPRECATED
#     Function to calculate exponential moving averages for close price.
#     '''
#     for w in windows:
#         check_columns(f'EMA_{w}')
#         df[f'EMA_{w}'] = df['Close'].ewm(span=w).mean()
#     return df


def macd(df, *columns, windows=(12, 26)):
    '''
    Function to add moving average convergence divergence column to df.
    Default value uses 12 and 26 period ema's
    '''
    for c in columns:
        check_columns(f'{c}_MACD_{windows[0]}_{windows[1]}')
        if f'{c}_EMA_{windows[0]}' or f'{c}_EMA_{windows[1]}' not in df:
            exp_ma(df, c, windows=(windows[0], windows[1]))
        df[f'{c}_MACD_{windows[0]}_{windows[1]}'] = \
            df[f'{c}_EMA_{windows[0]}'] - df[f'{c}_EMA_{windows[1]}']


def bollinger(df, *columns, windows=(20,)):
    '''
    Fn to calculate upper and lower bollinger bands for stock close price
    '''
    for c in columns:
        for w in windows:
            check_columns(f'{c}_Boll_Upper_{w}', f'{c}_Boll_Lower_{w}')
            if f'{c}_MA_{w}' or f'{c}_MA_{w}_SD' not in df:
                ma(df, 'Close', windows=(w,))
                std(df, f'{c}_MA_{w}', windows=(w,))
            df[f'{c}_Boll_Upper_{w}'] = \
                df[f'{c}_MA_{w}'] + (2 * df[f'{c}_MA_{w}_SD'])
            df[f'{c}_Boll_Lower_{w}'] = \
                df[f'{c}_MA_{w}'] - (2 * df[f'{c}_MA_{w}_SD'])


def std(df, *columns, windows=(20,)):
    '''
    Function to calculate standard deviation of given column(s), over specified
    window.
    '''
    for c in columns:
        for w in windows:
            check_columns(df, f'{c}_SD')
            df[f'{c}_SD'] = df[c].rolling(window=w).std()
    return df


def rsi(df, *columns, windows=(14,)):
    '''
    Function to calculate the relative strength index (RSI) of a stock column.
    Currently calculates for standard moving average.
    '''
    for c in columns:
        for w in windows:
            delta = df[c].diff()
            up, down = delta.copy(), delta.copy()
            up[up < 0], down[down > 0] = 0, 0
            rs = up.rolling(w).mean() / \
                 down.abs().rolling(w).mean()
            df[f'{c}_RSI_{w}'] = 100.0 - (100.0 / (1.0 + rs))
    return df


def check_columns(df, *columns):
    '''
    Fn to check if column exists already in dataframe and delete if
    true
    '''
    for column in columns:
        if column in df:
            del df[column]

def update_returns(start_date, df):
    '''
    This is used to update the returns column of a dataframe by resampling
    from a specified date using the stock_dataframe class. This is mainly used
    so ISF_L and GLTS_L databases can be resized for comparison with stocks
    having different time frames

    :param start_date: is the date from which resampling should be done
    :param df: dataframe on which recalculating should be performed
    :return: resampled dataframe
    '''
    return stock_dataframe('',None,df[df.index>=start_date]).pre_process(False)


def risk_free_rate(start_date, risk_free_df):
    '''
    This returns the risk free rate for a specified risk free stock dataframe

    :param start_date: date to calculate risk free rate from
    :param risk_free_df: risk free stock dataframe with 'Returns' column to be
            updated from specified start date
    :return: float return rate from specified start date
    '''
    return (update_returns(start_date, risk_free_df)['Returns']).tail(1) - 1


def covariance(df, base):
    '''
    Calculate covariance matrix for stock df against base stock

    :param df: main stock dataframe
    :param base: base stock dataframe to compare against e.g. FTSE 100 tracker
    :return: np 2x2 covariance matrix
    '''
    return np.cov(df['Returns'], base)


def beta(cov_matrix):
    '''
    Calculate beta value which is a measure of risk

    :param cov_matrix: covariance matrix between stock dataframe and baseline
            return e.g. FTSE 100 tracker
    :return: float beta value
    '''
    if cov_matrix[1][1] == 0:
        return np.nan
    return (cov_matrix[0][1] / cov_matrix[1][1])


def alpha(df, beta_value, rf, base):
    '''
    Calculate alpha value which is a measure of returns

    :param df: main stock dataframe
    :beta_value: beta for stock against risk free stock
    :rf: risk free rate (e.g. government bonds)
    :base: baseline stock returns dataframe (e.g. FTSE 100 tracker)
    :return: float alpha value
    '''
    a = (df['Returns'].tail(1) - 1) - rf - beta_value * ((base.tail(1)-1) - rf)
    return a.iloc[0] * 100


def sharpes(df, rf=0.01):
    '''
    Function to calculate Sharpe's ratio which is a combined measure of risk vs
    reward

    :param df: the stock dataframe with a 'Returns' column in
    :param rf: the risk free rate, if not specified defaults to 1%
    :return: float sharpes ratio
    '''
    if np.std(df['Returns']) == 0:
        return np.nan
    return (((df['Returns'].tail(1) - 1) - rf) / np.std(df['Returns'])).iloc[0]


def get_return_metrics(df, start_date, base_df, risk_free_df):
    '''
    Function to get all above metrics: sharpes, alpha, and beta

    :param df: stock dataframe of interest
    :param start_date: start date to calculate metrics from
    :param base_df: baseline stock dataframe (e.g. FTSE 100 tracker)
    :param risk_free_df: risk free stock dataframe (e.g. government bonds)
    '''
    if not start_date:
        start_date = df.head(1).index[0]
    rf = risk_free_rate(start_date, risk_free_df)
    base = update_returns(start_date, base_df)['Returns']
    beta_value = beta(covariance(df, base))
    return beta_value, alpha(df, beta_value, rf, base), sharpes(df, rf)
