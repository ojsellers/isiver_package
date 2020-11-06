'''
File containing formatting functionality for visualisation.py
'''

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

def format_plot(fig, title, **kwargs):
    '''
    Wrapper function to call formatting functions on figure and axes
    '''
    format_fig(fig, title, **kwargs)
    format_axes(fig, **kwargs)
    format_ohlcv(fig.axes[0])


def format_fig(fig, title, plot_size=(14, 9), background_colour='#07000d'):
    '''
    Format figure titles, colour and plot size
    '''
    fig.suptitle(title, color='w')
    fig.set_size_inches(plot_size)
    fig.set_facecolor(background_colour)
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))


def format_axes(fig, ax_colour='#07000d', spine_colour='#1ABC9C',
                tick_colour='w', max_dticks=30):
    '''
    Fn to format ax objects in fig
    '''
    for ax in fig.axes:
        ax.set_facecolor(ax_colour)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right') #readable labels
        plt.setp(ax.spines.values(), color=spine_colour)
        ax.tick_params(colors=tick_colour)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mticker.MaxNLocator(max_dticks))
    return fig


def format_ohlcv(ax):
    '''
    Format OHLCV axes colour and labels
    '''
    # OHLC main price chart
    ax.grid(True, color='w', linewidth=0.5, linestyle=':')
    ax.set_ylabel('Stock Price (GBP)', color='w')
    ax.set_xlabel('Date', color='w')
