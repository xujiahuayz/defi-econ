"""

University College London
Project : defi_econ
Topic   : uniswap.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch uniswap data.

"""

# Inport python modules
import datetime

# Import internal modules
from repo_clean.environ.utils.info_logger import print_info_log
from .fetch_uni_v2.select_top50_pairs_v2_script import select_top50_pairs_v2
from .fetch_uni_v3.select_top50_pairs_v3_script import select_top50_pairs_v3
from .fetch_uni_v2.top50_pair_directional_volume_v2_script import (
    top50_pair_directional_volume_v2,
)
from .fetch_uni_v3.top50_pair_directional_volume_v3_script import (
    top50_pair_directional_volume_v3,
)

# Fetch uniswap-related data
def fetch_uni() -> None:

    """
    Aggregate functon to fetch uniswap-related data.
    """

    top50_list_label = "2022JUL"

    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2022, 7, 11, 0, 0)
    end_date = datetime.datetime(2022, 8, 1, 0, 0)

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # Step 1: determine the list of monthly top 50 pools as candidates
    print_info_log("Fetch the list of monthly top 50 pools", "Uniswap V2")
    select_top50_pairs_v2(end_date - datetime.timedelta(1), 30, top50_list_label)
    print_info_log("Fetch the list of monthly top 50 pools", "Uniswap V3")
    select_top50_pairs_v3(end_date - datetime.timedelta(1), 30, top50_list_label)

    # Step 2: get directional daily volume for all dates based on the list in Step 1
    print_info_log("Fetch daily directional volume", "Uniswap V2")
    top50_pair_directional_volume_v2(date, top50_list_label)
    print_info_log("Fetch daily directional volume", "Uniswap V3")
    top50_pair_directional_volume_v3(date, top50_list_label)
