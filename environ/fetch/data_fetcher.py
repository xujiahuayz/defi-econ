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
from dateutil import relativedelta
import pandas as pd

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

    # Update the data monthly
    start_date_input = parsed_args.start
    end_date_input = parsed_args.end

    # Input start date and end date
    for month in pd.date_range(start_date_input, end_date_input, freq="MS"):
        start_date = datetime.strptime(month.strftime("%Y-%m-%d"), "%Y-%m-%d")
        end_date = datetime.strptime(
            (month + relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d"),
            "%Y-%m-%d",
        )

        label_year = month.strftime("%Y")
        label_month = month.strftime("%b").upper()
        label = label_year + label_month

        # time for info logger

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        print_info_log(
            f"Fetch DeFi Data in {label_month} {label_year}",
            "progress",
        )

        # Fetch uniswap-related data
        print_info_log(
            f"Fetch Uniswap Data from {start_date_str} to {end_date_str}",
            "progress",
        )
        # fetch_uni(label, start_date, end_date)

        # Fetch compound-related data
        print_info_log(
            f"Fetch Compound Data from {start_date_str} to {end_date_str}",
            "progress",
        )
        fetch_comp(start_date, end_date)

        # Fetch aave-related data
        # print_info_log("Fetch AAVE Data", "progress")
        # fetch_aave()
