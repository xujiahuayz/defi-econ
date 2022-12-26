"""

University College London
Project : defi_econ
Topic   : data_fetcher.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch DeFi data.

"""
# Import python modules
from datetime import datetime

# Import internal modules
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd
from .fetch_source.uniswap import fetch_uni
from .fetch_source.compound import fetch_comp

# from .fetch_source.aave import fetch_aave


def fetch_data():

    """
    Aggregate function to fetch defi data.
    """

    # Initialize argument parser
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Input start date and end date
    start_date = datetime.strptime(parsed_args.start, "%Y-%m-%d")
    end_date = datetime.strptime(parsed_args.end, "%Y-%m-%d")
    label = start_date.strftime("b")

    # Fetch uniswap-related data
    print_info_log(
        f"Fetch Uniswap Data from {parsed_args.start} to {parsed_args.end}", "progress"
    )
    fetch_uni(label, start_date, end_date)

    # Fetch compound-related data
    print_info_log(
        f"Fetch Compound Data from {parsed_args.start} to {parsed_args.end}", "progress"
    )
    fetch_comp(start_date, end_date)

    # Fetch aave-related data
    # print_info_log("Fetch AAVE Data", "progress")
    # fetch_aave()
