"""

University College London
Project : defi_econ
Topic   : data_fetcher.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch DeFi data.

"""
# Import python modules
import datetime
from tqdm import tqdm

# Import internal modules
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd

from environ.plot.network.plot_network import plot_network
from environ.plot.network.plot_dynamic import plot_dynamic
from environ.plot.timeseries.plot_timeseries import plot_timeseries


def plot_graph():

    """
    Aggregate function to plot graph
    """

    # Initialize argument parser
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Input start date and end date
    start_date = datetime.datetime.strptime(parsed_args.start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(parsed_args.end, "%Y-%m-%d")

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # Plot network graphs
    print_info_log(
        f"Plot network graphs from {parsed_args.start} to {parsed_args.end}", "progress"
    )

    # for date in tqdm(date_list):
    # plot_network(date, "v2")
    # plot_network(date, "v3")
    # plot_network(date)

    # Plot dynamic graphs
    print_info_log("Plot dynamic graphs for v2 and v3", "progress")

    # plot_dynamic("v2")
    # plot_dynamic("v3")
    # plot_dynamic("merged")

    # Plot time-series graphs
    print_info_log("Plot time-series graphs for v2 and v3", "progress")

    plot_timeseries(date_list, "v2")
    # plot_timeseries(date_list, "v3")
    # plot_timeseries(date_list, "merged")
