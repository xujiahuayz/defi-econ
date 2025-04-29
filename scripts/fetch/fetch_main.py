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

if __name__ == "__main__":
    # Initize the config and parse the running date.
    print_info_log("DeFi data fetching script started", "progress")

    config = Config()
    # args = arg_parse_cmd()
    # parsed_args = args.parse_args()

    # Fetch data. Now deprecated.
    # fetch_data()

    # Process data
    create_data_folders()
    process_data("v2")
    process_data("v3")
    process_data("merged")
    # Finish.
    print_info_log("Fetch script finished", "progress")
