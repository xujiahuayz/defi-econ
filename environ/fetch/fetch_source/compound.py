"""

University College London
Project : defi_econ
Topic   : uniswap.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch compound data.

"""

# Inport python modules
import datetime

# Import internal modules
from environ.utils.info_logger import print_info_log
from .fetch_comp.fetch_compound_historical_data import fetch_comp_historical_data


def fetch_comp(start_date: datetime.datetime, end_date: datetime.datetime) -> None:

    """
    Aggregate functon to fetch compound-related data.
    """

    # Fetch compound distorical data of all the tokens
    print_info_log("Fetch compound historical data of all the tokens", "Compound")
    fetch_comp_historical_data(start_date, end_date)
