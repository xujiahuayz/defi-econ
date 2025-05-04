"""
Fetch PLF data
"""

# Import python modules
from datetime import datetime

import pandas as pd
from dateutil import relativedelta

from environ.utils.args_parser import arg_parse_cmd

# Import internal modules
from environ.utils.info_logger import print_info_log

from .fetch_source.uniswap import fetch_uni
from environ.fetch.fetch_source.fetch_aave.download_aave_historical_data import (
    fetch_aave_historical_data,
)
from environ.fetch.fetch_source.fetch_comp.fetch_compound_historical_data import (
    fetch_comp_historical_data,
)


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
        fetch_uni(label, start_date, end_date)

        # Fetch compound-related data
        print_info_log(
            f"Fetch Compound Data from {start_date_str} to {end_date_str}",
            "progress",
        )
        fetch_comp_historical_data(start_date, end_date)

        # Fetch aave-related data
        print_info_log("Fetch AAVE Data", "progress")
        fetch_aave_historical_data()
