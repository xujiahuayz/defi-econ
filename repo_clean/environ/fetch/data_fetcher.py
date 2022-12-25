"""

University College London
Project : defi_econ
Topic   : data_fetcher.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch DeFi data.

"""

# Import internal modules
from repo_clean.environ.utils.info_logger import print_info_log
from .fetch_source.uniswap import fetch_uni
from .fetch_source.compound import fetch_comp
from .fetch_source.aave import fetch_aave


def fetch_data():

    """
    Aggregate function to fetch defi data.
    """

    # Fetch uniswap-related data
    print_info_log("Fetch Uniswap Data", "progress")
    fetch_uni()

    # Fetch compound-related data
    print_info_log("Fetch Compound Data", "progress")
    fetch_comp()

    # Fetch aave-related data
    print_info_log("Fetch AAVE Data", "progress")
    fetch_aave()
