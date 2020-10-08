'''
@author = Isaac

Cleans and plots pandas dataframe(s) using modified mpl_finance module

TODO
    - add all function strings
    - DO IT with THE DATA AS A CLASS, ALLOWS PASSING TICKER IN with *ARGS AND
    CAN HOLD SAME DYNAMIC FUNCTIONALITY WE HAVE HERE
    - Add close/adjusted close parameter
    - update to use test_data functionality in data_acquisition
'''

import pickle
import os
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.ticker import Formatter
from isiver_utils.plotting import mpl_finance_modified as mpf

# Default plot save directory
default_plot_dir = os.getcwd() + '/plots/'

def daily_ohlcv(*stock_classes, output_window=True, save_fig=False, **kwargs):
    '''
    Wrapper function for daily OHLC graph, with volume data overlay.

    *args:
        stock_classes - stock_class(es) generated from data_acquisition.py

    defaults:
        save_fig - Toggle if plot is save_d
        save_dir - path to plot save directory

    **kwargs:
        volume_plot - either 'off', 'bar' or 'fill'
        output_window - selects if plot is printed from command line
        plot_size - size of matplotlib output window
        background_colour - fig background colour
        up_colour - up bar colour
        down_colour - down bar colour
        ax1_colour - background of main plot
        spine_colour - colour of all spines in plot
        tick_colour - X/Y tick colour
        max_dticks - assign maximum number of date ticks on bottom axis for readability
        fill_dates - choose False to include weekends in plot
        save_fig - toggle if matplotlib saves plot
        save_dir - directory to save plot in

    returns list containing fig and ax object(s) for further manipulation
    '''
    # Initialise empty lists for fig and ax objects if they need to be returned
    plot_list = []

    for stock_class in stock_classes:
        format_dates(stock_class.df)
        fig, ax = generate_fig_ax()                                             # CREATE SUBPLOT AXES HERE WITH CONDITIONAL AND KWARGS
        fig, axes = generate_daily_ohlcv(stock_class.df, fig, ax, **kwargs)
        fig, axes = format_plot(fig, axes, **kwargs)
        add_subplots(stock_class.df, axes)
        fig.suptitle(stock_class.ticker, color='w')
        plot_list.append([fig, axes])
        process_fig(**kwargs)

    return plot_list


def generate_fig_ax():
    '''
    Fn to generate figure and axis objects for plotting stock information
    '''
    # Create figure and specify dimensions
    fig = plt.figure() # create figure
    ax = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4) # assign axis
    return fig, ax


def format_dates(stock_df):
    '''
    Fn to format df index dates for plotting with matlab
    '''
    stock_df.index = pd.to_datetime(stock_df.index)
    mdates.date2num(stock_df.index)
    # matplotlib_dates = mpl.dates.datestr2num(data.index) # If index column str
    return stock_df


def process_fig(save_fig=False, save_dir=default_plot_dir, output_window=True):
    '''
    Fn to save and/or output figure depending on save_fig and output_window
    Booleans.
    '''
    if save_fig == True:
        plt.savefig(f'{save_dir}{stock_class.ticker}.{date.today()}.png')
    if output_window == True:
        plt.show()


def generate_daily_ohlcv(dataframe, fig, ax1, up_colour='#53c156',
                         down_colour='#ff1717', volume_plot='bar', **kwargs):
    '''
    Generate daily ohlcv fig and ax objects with modified mpl-finance module
    '''
    ohlcv = prepare_ohlcv_list(dataframe)
    # Check and add initial data to plot
    mpf.plot_day_summary_ohlc(ax1, ohlcv, ticksize = 3, colorup=up_colour,
                              colordown=down_colour)
    format_ohlcv(ax1)
    # Apply volume overlay
    axes = plot_volume_overlay(ohlcv, [ax1], volume_plot)
    return fig, axes

def format_ohlcv(ax):

    # OHLC main price chart
    ax.grid(True, color='w', linewidth=0.5, linestyle=':')
    plt.ylabel('Stock Price (GBP)', color='w')
    ax.set_xlabel('Date', color='w')

def prepare_ohlcv_list(stock_df):
    '''
    Formats data into list to allow for plotting with older mpl-finance functions.
    '''
    # extract OHLC prices into list of lists (required for old mpl-finance module)
    ohlcv_list = stock_df[['Open', 'High', 'Low', 'Close', 'Volume']].values.tolist()
    # Append adjusted dates to ohlcv_list
    ohlcv = [[stock_df.index[i]] + ohlcv_list[i] for i in range(len(stock_df.index))]
    return ohlcv


def plot_volume_overlay(ohlcv, axes, volume_plot):
    '''
    Function to overlay volume on price plot
    '''
    if volume_plot != 'off':
        volumeMin = 0
        volume_data = [line[5] for line in ohlcv]
        dates = [line[0] for line in ohlcv]
        ax_v = axes[0].twinx()

        if volume_plot == 'bar':
            ax_v.bar(dates, volume_data, color='#1ABC9C', alpha=.3)

        if volume_plot == 'fill':
            ax_v.fill_between(dates, volumeMin, volume_data, facecolor='#1ABC9C',
                             alpha=.3)

        # Set max bar height lower than ohlc markers for ease of viewing
        ax_v.set_ylim(0, 4*max(volume_data))
        ax_v.set_ylabel('Volume', color='w')
        return axes + [ax_v]
    return axes


def add_subplots(stock_df, axes, macd_plot='on'):
    x = 1
    # # Apply volume overlay
    # if macd_plot != 'off':
    #     axes = axes + [plot_macd(stock_df, axes[0], macd_plot)]


# def plot_macd(stock_df, ax, macd_plot):
#
#     ax_macd = plt.subplot2grid((6,4), (5,0), sharex=ax, rowspan=1, colspan=4,
#                             facecolor='#07000d')
#     ax_macd.plot(stock_df['Date'], stock_df['Close_MACD_12_26'], color='#4ee6fd', lw=2)
#     # ax_macd.plot([line[0] for line in stock_dataframe], stock_df['Close_MACD_12_26'], color='#e1edf9', lw=1)
#
#
#
#     print('reached')
#     return ax_macd


def add_indicator_arrow(ax, date, price, text, colour):
    '''
    Adds annotation to supplied axis object

    Args:

        ax - axis object to be annotated
        index - date format index where annotation is to be made
        price - price value to make annotation
        text - annotation text
        colour - annotation and arrow colour
    '''
    index_num = mdates.date2num(date) # Convert date to number to plot correctly
    ax.annotate(text, (index_num, price), (index_num, price+30),
                arrowprops=dict(arrowstyle='->', color=colour), color=colour)

# def add_titles():

def format_plot(fig, axes, plot_size=(14, 9), background_colour='#07000d',
                ax1_colour='#07000d', spine_colour='#1ABC9C', tick_colour='w',
                max_dticks=30):
    '''
    Use **kwargs to dynamically assign any non-default parameters
    '''
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    fig.set_size_inches(plot_size)
    fig.set_facecolor(background_colour)

    for ax in axes:
        ax.set_facecolor(ax1_colour)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right') #readable labels
        plt.setp(ax.spines.values(), color=spine_colour)
        ax.tick_params(colors=tick_colour)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mticker.MaxNLocator(max_dticks))

    return fig, axes
