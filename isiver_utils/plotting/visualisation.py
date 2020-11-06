"""
@author = Isaac

Cleans and plots pandas dataframe(s) using modified mpl_finance module

TODO
    - add all function strings
    - DO IT with THE DATA AS A CLASS, ALLOWS PASSING TICKER IN with *ARGS AND
    CAN HOLD SAME DYNAMIC FUNCTIONALITY WE HAVE HERE
    - Add close/adjusted close parameter
    - update to use test_data functionality in data_acquisition
    - check all kwargs
    - subfunction subplot generation
    - make main plot a different size dependng on chosen plots
    - put functions in another script
    - check how many times we assign facecolor
    - rename to ohlcv_daily
    - fix kwarg output_window and save_fig issue
    - add macd subplot

"""

import pickle
import os
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import Formatter


from isiver_utils import default_plot_dir
from isiver_utils.plotting import mpl_finance_modified as mpf
from isiver_utils.plotting import formatting


def daily_ohlcv(*stock_classes, output_window=True, save_fig=False, **kwargs):
    """
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
        ax_colour - background of main plot
        spine_colour - colour of all spines in plot
        tick_colour - X/Y tick colour
        max_dticks - assign maximum number of date ticks on bottom axis for readability
        fill_dates - choose False to include weekends in plot
        save_fig - toggle if matplotlib saves plot
        save_dir - directory to save plot in

    returns list containing fig object(s)
    """
    # Initialise empty lists for fig objects if they need to be returned
    plot_list = []

    for stock_class in stock_classes:                                           # REORDER AS NECESSARY - Make sure following functions are in order called
        format_dates(stock_class.df)
        fig, ohlcv_ax = generate_fig_ax()                                       # CREATE SUBPLOT AXES HERE WITH CONDITIONAL AND KWARGS
        generate_daily_ohlcv(stock_class.df, fig, ohlcv_ax, **kwargs)
        volume_ax = plot_volume(stock_class.df, ohlcv_ax, **kwargs)
        formatting.format_plot(fig, stock_class.ticker, **kwargs)
        plot_list.append([fig])
        process_fig(**kwargs)

    return plot_list


def generate_fig_ax():
    """
    Fn to generate figure and axis objects for plotting stock information
    """
    # Create figure and specify dimensions
    fig = plt.figure() # create figure
    ax = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, fig=fig)
    return fig, ax


def format_dates(stock_df):
    """
    Fn to format df index dates for plotting with matlab
    """
    stock_df.index = pd.to_datetime(stock_df.index)
    mdates.date2num(stock_df.index)
    # matplotlib_dates = mpl.dates.datestr2num(data.index) # If index column str
    return stock_df


def process_fig(save_fig=False, save_dir=default_plot_dir, output_window=True):
    """
    Fn to save and/or output figure depending on save_fig and output_window
    Booleans.
    """
    if save_fig == True:
        plt.savefig(f'{save_dir}{stock_class.ticker}.{date.today()}.png')
    if output_window == True:
        plt.show()


def generate_daily_ohlcv(stock_df, fig, ohlcv_ax, up_colour='#53c156',
                         down_colour='#ff1717', volume_plot='bar', **kwargs):
    """
    Generate daily ohlcv fig and ax objects with modified mpl-finance module
    """
    ohlcv = prepare_ohlcv_list(stock_df)
    mpf.plot_day_summary_ohlc(ohlcv_ax, ohlcv, ticksize = 3, colorup=up_colour,
                              colordown=down_colour)
    return fig, ohlcv_ax


def prepare_ohlcv_list(stock_df):
    """
    Formats data into list to allow for plotting with older mpl-finance functions.
    """
    # extract OHLC prices into list of lists (required for old mpl-finance module)
    ohlcv_list = stock_df[['Open', 'High', 'Low', 'Close', 'Volume']].values.tolist()
    # Append adjusted dates to ohlcv_list
    ohlcv = [[stock_df.index[i]] + ohlcv_list[i] for i in range(len(stock_df.index))]
    return ohlcv


def plot_volume(stock_df, ohlcv_ax, volume_plot='bar'):
    """
    Function to overlay volume on OHLCV price plot
    """
    ohlcv = prepare_ohlcv_list(stock_df)
    if volume_plot != 'off':
        volumeMin = 0
        volume_data = [line[5] for line in ohlcv]
        dates = [line[0] for line in ohlcv]
        volume_ax = ohlcv_ax.twinx()

        if volume_plot == 'bar':
            volume_ax.bar(dates, volume_data, color='#1ABC9C', alpha=.3)

        if volume_plot == 'fill':
            volume_ax.fill_between(dates, volumeMin, volume_data, facecolor='#1ABC9C',
                             alpha=.3)

        # Set max bar height lower than ohlc markers for ease of viewing
        volume_ax.set_ylim(0, 4*max(volume_data))
        volume_ax.set_ylabel('Volume', color='w')
        return volume_ax
    return ohlcv_ax


def add_indicator_arrow(ax, date, price, text, colour):
    """
    Adds annotation to supplied axis object

    Args:

        ax - axis object to be annotated
        index - date format index where annotation is to be made
        price - price value to make annotation
        text - annotation text
        colour - annotation and arrow colour
    """
    index_num = mdates.date2num(date) # Convert date to number to plot correctly
    ax.annotate(text, (index_num, price), (index_num, price+30),
                arrowprops=dict(arrowstyle='->', color=colour), color=colour)
