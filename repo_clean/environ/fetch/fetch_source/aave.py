"""

University College London
Project : defi_econ
Topic   : uniswap.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch compound data.

"""

# Import internal modules
from repo_clean.environ.utils.info_logger import print_info_log
from .fetch_aave.download_aave_historical_data import fetch_aave_historical_data


def fetch_aave() -> None:

    """
    Aggreate functio to fetch aave-related data.
    """

    print_info_log("Fetch aave historical data of all the tokens", "AAVE")
    fetch_aave_historical_data()
