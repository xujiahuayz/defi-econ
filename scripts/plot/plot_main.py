# -*- coding: utf-8 -*-
"""

University College London
Project : defi_econ
Topic   : plot_main.py
Author  : Yichen Luo
Date    : 2023-01-02

"""

import datetime

import pandas as pd

from environ.plot.plot_utils.plot_ma import plot_ma
from environ.plot.timeseries.plot_timeseries import plot_timeseries
from environ.utils.args_parser import arg_parse_cmd

# Import internal modules.
from environ.utils.config_parser import Config

# Import internal modules
from environ.utils.info_logger import print_info_log

# Initize the config and parse the running date.
print_info_log("DeFi graph plot script started", "progress")

config = Config()
args = arg_parse_cmd()
parsed_args = args.parse_args()

# Plot graphs.

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

date_list_v3 = []
for i in range((end_date - pd.to_datetime("2021-05-05")).days):
    date = pd.to_datetime("2021-05-05") + datetime.timedelta(i)
    date_list_v3.append(date)

# # Plot network graphs
# print_info_log(
#     f"Plot network graphs from {parsed_args.start} to {parsed_args.end}", "progress"
# )

# for date in tqdm(date_list):
#     plot_network(date)

# # Plot dynamic graphs
# print_info_log("Plot dynamic graphs for v2 and v3", "progress")

# plot_dynamic("v2")
# plot_dynamic("v3")
# plot_dynamic("merged")

# Plot time-series graphs
print_info_log("Plot time-series graphs for v2 and v3", "progress")

plot_timeseries(date_list, "v2")
plot_timeseries(date_list_v3, "v3")
plot_timeseries(date_list, "merged")

# Plot moving average graphs
print_info_log("Plot moving average graphs for v2 and v3", "progress")

for iter_source in ["v2", "v3", "merged"]:
    for iter_graph_type in [
        "volume_in_share",
        "volume_out_share",
        "volume_share",
        "tvl_share",
    ]:
        plot_ma(iter_graph_type, iter_source)

for iter_graph_type in ["borrow_share", "supply_share", "borrow_apy", "supply_apy"]:
    plot_ma(iter_graph_type, iter_source)

for iter_source in ["v2", "v3", "v2v3"]:
    for iter_graph_type in [
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
    ]:
        plot_ma(iter_graph_type, iter_source)

    # Finish.
    print_info_log("Plot script finished", "progress")
