"""

University College London
Project : defi_econ
Topic   : data_processor.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Process DeFi data.

"""
# Import python modules
import datetime
from dateutil import relativedelta
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
from functools import partial

# Import internal modules
from environ.utils.args_parser import arg_parse_cmd
from environ.utils.info_logger import print_info_log
from .network.prepare_network_data import prepare_network_data
from .network.network_graph import prepare_volume
from .network.network_graph import prepare_network_graph
from .betweeness_centrality.betweeness_scripts import get_betweenness_centrality


def process_data():

    """
    Aggregate function to process defi data.
    """

    # Initialize argument parser
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Input start date and end date
    start_date = datetime.datetime.strptime(parsed_args.start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(parsed_args.end, "%Y-%m-%d")

    # Generate date list
    date_list = []
    for i in range((end_date - start_date).days + 1):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # Generate data list for volume data
    date_list_volume = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list_volume.append(date)

    # # Process inout flow data
    # print_info_log(
    #     f"Process Inout Flow Data from {parsed_args.start} to {parsed_args.end}",
    #     "progress",
    # )

    # for date in tqdm(date_list, total=len(date_list)):
    #     prepare_network_data(date, "v2")
    #     prepare_network_data(date, "v3")

    # # Prepare eigenvector centrality data
    # print_info_log(
    #     f"Process Eigenvector Centrality Data from {parsed_args.start} to {parsed_args.end}",
    #     "progress",
    # )

    # for date in tqdm(date_list_volume, total=len(date_list)):
    #     prepare_network_graph(date, "v2", directed=True)
    #     prepare_network_graph(date, "v3", directed=True)
    #     prepare_network_graph(date, "merged", directed=True)

    # Prepare betweenness centrality data
    print_info_log(
        f"Process Betweenness Centrality Data from {parsed_args.start} to {parsed_args.end}",
        "progress",
    )

    # Update the data monthly
    start_date_input = parsed_args.start
    end_date_input = parsed_args.end

    for month in tqdm(pd.date_range(start_date_input, end_date_input, freq="MS")):
        start_date = datetime.datetime.strptime(month.strftime("%Y-%m-%d"), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(
            (month + relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d"),
            "%Y-%m-%d",
        )

        label_year = month.strftime("%Y")
        label_month = month.strftime("%b").upper()
        label = label_year + label_month

        # list for multiple dates
        date_list_betweenness = []
        for i in range((end_date - start_date).days):
            date = start_date + datetime.timedelta(i)
            date_str = date.strftime("%Y%m%d")
            date_list_betweenness.append(date_str)

        # Multiprocess
        p = Pool()
        p.map(
            partial(
                get_betweenness_centrality,
                top_list_label=label,
                uniswap_version="v2v3",
            ),
            date_list_betweenness,
        )

    # # Process volume data
    # print_info_log(
    #     f"Process Volume Data from {parsed_args.start} to {parsed_args.end}",
    #     "progress",
    # )

    # for date in tqdm(date_list_volume, total=len(date_list_volume)):
    #     prepare_volume(date, "v2")
    #     prepare_volume(date, "v3")
    #     prepare_volume(date, "merged")
