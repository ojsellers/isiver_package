'''
@author = Ollie

This file is used to calculate common performance metrics for a certain stock,
requires the provision of a dataframe for a risk free stock (e.g. government
bonds) and a dataframe for a baseline stock (e.g. FTSE 100 tracker for a FTSE
stock)
'''

from isiver_utils.data.data_acquisition import stock_dataframe
import numpy as np
import pandas as pd

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

def get_metrics(df, start_date, base_df, risk_free_df):
    '''
    Function to get all above metrics

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
