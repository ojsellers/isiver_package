'''
Module to provide calculation of default metrics for stock dataframes.

TODO:
    - Exponential rsi
    - Deltas and mivng avg deltas
    - Isaac can you update your other metrics so they work with the
    add_metric_column function in the stock_dataframe class. Feel free to make
    any edits as you need - I reckon you could whip some kwargs in to pass to
    the specified metric function for additional parameters
'''

import numpy as np
import pandas as pd
import sys

def moving_average(df_column, window):
    '''
    Generalised function to calculate and append a moving averages column

    '''
    return df_column.rolling(window=window).mean()


def exp_moving_average(df_column, window):
    '''
    Generalised function to calculate exponential moving averages for given
    column(s)
    '''
    return df_column.ewm(span=window).mean()


def std(df_column, window):
    '''
    Function to calculate standard deviation of given column(s), over specified
    window.
    '''
    return df_column.rolling(window=window).std()


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


# def macd(df_column, window):
#     '''
#     Function to add moving average convergence divergence column to df.
#     Default value uses 12 and 26 period ema's
#     '''
#     if f'{c}_EMA_{window[0]}' or f'{c}_EMA_{window[1]}' not in df:
#         sys.exit(f'METRIC ERROR: {window[0]}-{window[0]} MACD missing required \
#                 EMA columns')
#     return df[f'{c}_EMA_{windows[0]}'] - df[f'{c}_EMA_{windows[1]}']

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

def risk_free_rate(risk_free_df):
    '''
    This returns the risk free rate for a specified risk free stock dataframe

    :param risk_free_df: risk free stock dataframe with 'Returns' same length
                as base_df
    :return: float return rate from specified start date
    '''
    return (risk_free_df['Returns']).tail(1) - 1


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


def get_return_metrics(df, base_df, risk_free_df):
    '''
    Function to get all above metrics: sharpes, alpha, and beta
    Have to ensure returns column in risk_free_df and base_df have the same
    length returns column using the in-class resample_returns col

    :param df: stock dataframe of interest
    :param base_df: baseline stock dataframe (e.g. FTSE 100 tracker)
    :param risk_free_df: risk free stock dataframe (e.g. government bonds)
    '''
    rf = risk_free_rate(risk_free_df)
    beta_value = beta(covariance(df, base_df['Returns']))
    return beta_value, alpha(df, beta_value, rf, base_df['Returns']), sharpes(df, rf)
