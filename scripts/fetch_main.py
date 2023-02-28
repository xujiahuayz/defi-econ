# -*- coding: utf-8 -*-
"""

University College London
Project : defi_econ
Topic   : fetch_main.py
Author  : Yichen Luo
Date    : 2022-12-17

"""

# Import internal modules.
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd
from environ.fetch.data_fetcher import fetch_data
from environ.process.data_processor import process_data

if __name__ == "__main__":

    # Initize the config and parse the running date.
    print_info_log("DeFi data fetching script started", "progress")

    config = Config()
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Fetch data.
    # fetch_data()

    # Process data
    # process_data()

    # Finish.
    print_info_log("Fetch script finished", "progress")
