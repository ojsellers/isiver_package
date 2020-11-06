"""
Module to provide calculation of default metrics for stock dataframes.

TODO:
    - Exponential rsi
    - Deltas and mivng avg deltas
"""


import numpy as np
import pandas as pd


def moving_average(df_column, window):
    """
    Generalised function to calculate and append a moving averages column

    """
    return df_column.rolling(window=window).mean()


def exp_moving_average(df_column, window):
    """
    Generalised function to calculate exponential moving averages for given
    column(s)
    """
    return df_column.ewm(span=window).mean()


def std(df_column, window):
    """
    Function to calculate standard deviation of given column(s), over specified
    window.
    """
    return df_column.rolling(window=window).std()


def rsi(df_column, window):
    """
    Function to calculate the relative strength index (RSI) of a stock column.
    Currently calculates for standard moving average.
    """
    delta = df_column.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0], down[down > 0] = 0, 0
    rs = up.rolling(window).mean() / \
         down.abs().rolling(window).mean()
    return 100.0 - (100.0 / (1.0 + rs))


def macd(df_column, window):
    """
    Function to add moving average convergence divergence for given column to
    df.
    """
    ema_1 = exp_moving_average(df_column, window[0])
    ema_2 = exp_moving_average(df_column, window[1])
    return ema_1 - ema_2


def bollinger(df_column, window, bound='Upper'):
    """
    Fn to calculate upper and lower bollinger bands for given column
    """
    ma = moving_average(df_column, window)
    sd = std(df_column, window)
    if bound == 'Upper':
        return ma + (2 * sd)
    elif bound == 'Lower':
        return ma - (2 * sd)


def risk_free_rate(risk_free_df):
    """
    This returns the risk free rate for a specified risk free stock dataframe

    :param risk_free_df: risk free stock dataframe with 'Returns' same length
                as base_df
    :return: float return rate from specified start date
    """
    return (risk_free_df['Returns']).tail(1) - 1


def covariance(df, base):
    """
    Calculate covariance matrix for stock df against base stock

    :param df: main stock dataframe
    :param base: base stock dataframe to compare against e.g. FTSE 100 tracker
    :return: np 2x2 covariance matrix
    """
    return np.cov(df['Returns'], base)


def beta(cov_matrix):
    """
    Calculate beta value which is a measure of risk

    :param cov_matrix: covariance matrix between stock dataframe and baseline
            return e.g. FTSE 100 tracker
    :return: float beta value
    """
    if cov_matrix[1][1] == 0:
        return np.nan
    return (cov_matrix[0][1] / cov_matrix[1][1])


def alpha(df, beta_value, rf, base):
    """
    Calculate alpha value which is a measure of returns

    :param df: main stock dataframe
    :beta_value: beta for stock against risk free stock
    :rf: risk free rate (e.g. government bonds)
    :base: baseline stock returns dataframe (e.g. FTSE 100 tracker)
    :return: float alpha value
    """
    a = (df['Returns'].tail(1) - 1) - rf - beta_value * ((base.tail(1)-1) - rf)
    return a.iloc[0] * 100


def sharpes(df, rf=0.01):
    """
    Function to calculate Sharpe's ratio which is a combined measure of risk vs
    reward

    :param df: the stock dataframe with a 'Returns' column in
    :param rf: the risk free rate, if not specified defaults to 1%
    :return: float sharpes ratio
    """
    if np.std(df['Returns']) == 0:
        return np.nan
    return (((df['Returns'].tail(1) - 1) - rf) / np.std(df['Returns'])).iloc[0]


def get_return_metrics(df, base_df, risk_free_df):
    """
    Function to get all above metrics: sharpes, alpha, and beta

    Have to ensure returns column in risk_free_df and base_df have the same,
    can call this method from stock df:
    stock_dataframe('',None,df[df.index>=start_date]).pre_process(False)

    length returns column using the in-class resample_returns col

    :param df: stock dataframe of interest
    :param base_df: baseline stock dataframe (e.g. FTSE 100 tracker)
    :param risk_free_df: risk free stock dataframe (e.g. government bonds)
    """
    rf = risk_free_rate(risk_free_df)
    beta_value = beta(covariance(df, base_df['Returns']))
    return beta_value, alpha(df, beta_value, rf, base_df['Returns']), sharpes(df, rf)
