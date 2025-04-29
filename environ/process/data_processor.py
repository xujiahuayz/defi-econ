"""
Aggregate function to process defi data.
"""

# Import python modules
import os
import datetime
from dateutil import relativedelta
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
from functools import partial

# Import internal modules
from environ.utils.args_parser import arg_parse_cmd
from environ.utils.info_logger import print_info_log
from environ.process.network.prepare_network_data import prepare_network_data
from environ.process.network.network_graph import prepare_volume
from environ.process.network.network_graph import prepare_network_graph
from environ.process.betweeness_centrality.betweeness_scripts import (
    get_betweenness_centrality,
)


def create_data_folders():
    for uni_version_folder in ["data/data_network/v2/", "data/data_network/v3/"]:
        for uni_version_subfolder in [
            "betweenness",
            "clustering_ind",
            "eigen_centrality_pool",
            "eigen_centrality_swap",
            "eigen_centrality_undirected",
            "eigen_centrality_undirected_multi",
            "inflow_centrality",
            "inout_flow",
            "network_graph",
            "outflow_centrality",
            "primary_tokens",
            "sankey",
            "total_eigen_centrality_undirected",
            "tvl",
            "tvl_old",
            "tvl_share",
            "tvl_share_old",
            "volume",
            "volume_in",
            "volume_in_share",
            "volume_out",
            "volume_out_share",
            "volume_share",
            "volume_total",
            "vol_inter_full_len",
            "vol_in_full_len",
            "vol_out_full_len",
        ]:
            # Create it (and parents) if it doesn't exist
            os.makedirs(uni_version_folder + uni_version_subfolder, exist_ok=True)

        for betw_folder in [
            "data/data_betweenness/betweenness",
            "data/data_betweenness/swap_route",
        ]:
            # Create it (and parents) if it doesn't exist
            os.makedirs(betw_folder, exist_ok=True)


def process_data(uni_version="v2"):
    """
    Aggregate function to process defi data.
    """

    # # Initialize argument parser
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    if uni_version == "v2" or uni_version == "merged":
        parsed_args.start = "2020-05-18"
        parsed_args.end = "2023-01-31"
    elif uni_version == "v3":
        parsed_args.start = "2021-05-05"
        parsed_args.end = "2023-01-31"
    # # Input start date and end date
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

    # Process inout flow data
    print_info_log(
        f"Process In and Out Flow Data from {parsed_args.start} to {parsed_args.end}",
        "progress",
    )

    for date in tqdm(date_list, total=len(date_list)):
        prepare_network_data(date, uni_version)
        # prepare_network_data(date, "v3")

    # Prepare eigenvector centrality data
    print_info_log(
        f"Process Eigenvector Centrality Data from {parsed_args.start} to {parsed_args.end}",
        "progress",
    )

    for date in tqdm(date_list_volume, total=len(date_list)):
        prepare_network_graph(date, uni_version, directed=True)
        # prepare_network_graph(date, "v3", directed=True)
        # prepare_network_graph(date, "merged", directed=True)

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
                uniswap_version=uni_version,
            ),
            date_list_betweenness,
        )

    # Process volume data
    print_info_log(
        f"Process Volume Data from {parsed_args.start} to {parsed_args.end}",
        "progress",
    )

    for date in tqdm(date_list_volume, total=len(date_list_volume)):
        prepare_volume(date, uni_version)
        # prepare_volume(date, "v3")
        # prepare_volume(date, "merged")
