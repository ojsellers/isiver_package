'''
@author = Isaac

Cleans and plots pandas dataframe(s) using modified mpl_finance module

TODO
    - DO IT WITH THE DATA AS A CLASS, ALLOWS PASSING TICKER IN WITH *ARGS AND
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
import mpl_finance_modified as mpf # old mpl-finance library - gives full matplotlib customisation

# Default plot save directory
default_plot_dir = os.getcwd() + '/plots/'

# TEST PLOTTING FUNCTION FROM WITHIN SCRIPT - COMMENT OUT IF CALLING FROM ELSEWHERE

# import sys
# sys.path.insert(1, os.getcwd() + '/data')
# import data_acquisition # Can't pickle a user class - must reference origin
#
# # Temporary example data
# stock_class = pickle.load(open('data/example_data_class.pkl', 'rb'))
#
# # Check the data imported
# print(stock_class.df)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def daily_ohlcv(*stock_classes, output_window=True, save_fig=False,
                save_dir=default_plot_dir, **kwargs):
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
        plot_size - sizo of matplotlib output window
        background_colour - fig background colour
        up_colour - up bar colour
        down_colour - down bar colour
        ax1_colour - background of main plot
        spine_colour - colour of all spines in plot
        tick_colour - X/Y tick colour
        max_dticks - assign maximum number of date ticks on bottom axis for readability
        fill_dates - choose False to include weekends in plot

    returns list containing fig and ax object(s) for further manipulation
    '''

    # Initialise empty lists for fig and ax objects if they need to be returned
    plot_list = []

    for stock_class in stock_classes:
        fig, axes = generate_daily_ohlcv(stock_class.df, **kwargs)
        fig.suptitle(stock_class.ticker, color='w')

        plot_list.append([fig, axes])

        if save_fig == True:
            plt.savefig(f'{save_dir}{stock_class.ticker}.{date.today()}.png')

        if output_window == True:
            plt.show()

    return plot_list

def prepare_data(data):
    '''
    Formats data to allow for plotting with older mpl-finance module.
    '''

    # Convert dates from string to datetime format
    data.index = pd.to_datetime(data.index)

    # extract OHLC prices into list of lists (required for old mpl-finance module)
    ohlcv_list = data[['Open', 'High', 'Low', 'Close', 'Volume']].values.tolist()

    # Convert date index to Matplotlib date format
    matplotlib_dates = mdates.date2num(data.index)

    # If future data acquisition methods give index column as string type
    # matplotlib_dates = mpl.dates.datestr2num(data.index)

    # Append adjusted dates to ohlcv_list
    ohlcv = [[matplotlib_dates[i]] + ohlcv_list[i] for i in range(len(matplotlib_dates))]

    return ohlcv

def generate_daily_ohlcv(dataframe, up_colour = '#53c156',
                         down_colour='#ff1717', volume_plot='bar', **kwargs):
    '''
    Generate daily ohlcv fig and ax objects with modified mpl-finance module
    '''

    ohlcv = prepare_data(dataframe)

    # Create figure and specify dimensions
    fig = plt.figure() # create figure
    ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4) # assign axis

    # Check and add initial data to plot
    mpf.plot_day_summary_ohlc(ax1, ohlcv, ticksize = 3, colorup=up_colour,
                              colordown=down_colour)

    # OHLC main price chart
    ax1.grid(True, color='w', linewidth=0.5, linestyle=':')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    plt.ylabel('Stock Price (GBP)', color='w')
    ax1.set_xlabel('Date', color='w')
    axes = [ax1]

    # Apply volume overlay
    if volume_plot != 'off':
        axes = axes + [volume_overlay(ohlcv, ax1, volume_plot)]

    # Arrange date labels in a readable way
    plt.setp(ax1.get_xticklabels(), rotation=30, ha='right')

    fig, axes = format_plot(fig, axes, **kwargs)

    return fig, axes

def volume_overlay(ohlcv, ax, volume_plot):
        '''
        Function to overlay volume on price plot
        '''

        volumeMin = 0
        volume_data = [line[5] for line in ohlcv]
        dates = [line[0] for line in ohlcv]
        axv = ax.twinx()

        if volume_plot == 'bar':
            axv.bar(dates, volume_data, color='#1ABC9C', alpha=.3)

        if volume_plot == 'fill':
            axv.fill_between(dates, volumeMin, volume_data, facecolor='#1ABC9C',
                             alpha=.3)

        axv.set_ylim(0, 4*max(volume_data)) # Set max bar height lower than ohlc markers for ease of viewing
        axv.set_ylabel('Volume', color='w')

        return axv

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

def format_plot(fig, axes, plot_size=(14, 9), background_colour='#07000d',
                ax1_colour='#07000d', spine_colour='#1ABC9C', tick_colour='w',
                max_dticks=30):
    '''
    Use **kwargs to dynamically assign any non-default parameters
    '''

    fig.set_size_inches(plot_size)
    fig.set_facecolor(background_colour)

    for ax in axes:
        ax.set_facecolor(ax1_colour)
        plt.setp(ax.spines.values(), color=spine_colour)
        ax.tick_params(colors=tick_colour)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mticker.MaxNLocator(max_dticks=max_dticks))

    return fig, axes

# plot_list = daily_ohlcv(stock_class, save_fig=True)
