# -*- coding: utf-8 -*-
"""
Main script for fetching DeFi data.
"""
# Import internal modules.
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd

# from environ.fetch.data_fetcher import fetch_data
from environ.process.data_processor import process_data, create_data_folders
from environ.process.pre_betweenness import prepare_betweenness_data
from environ.process.pre_compound import prepare_compound_data
from environ.process.pre_panel import prepare_panel_data
from environ.process.pre_herfin import prepare_herfin_data
from environ.process.eigen_cluster.prepare_eigen_cluster import (
    prepare_eigencentrality_data,
)


if __name__ == "__main__":
    # Initize the config and parse the running date.
    print_info_log("DeFi data fetching script started", "progress")

    config = Config()
    # args = arg_parse_cmd()
    # parsed_args = args.parse_args()
    # ###testing
    # parsed_args.start = "2021-05-18"
    # parsed_args.end = "2021-05-31"

    # Fetch data. Now deprecated.
    # fetch_data()

    # Process data
    # create_data_folders()
    # print_info_log("processing v2", "progress")
    # process_data("v2")
    print_info_log("processing v3", "progress")
    process_data("v3")
    # print_info_log("processing v2v3 merged", "progress")
    # process_data("merged")

    prepare_betweenness_data()
    prepare_eigencentrality_data()
    print_info_log("processing Compound data", "progress")
    prepare_compound_data()
    prepare_panel_data()
    prepare_herfin_data()
    print_info_log("Fetch script finished", "progress")
