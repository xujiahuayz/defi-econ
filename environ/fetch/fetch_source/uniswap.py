"""

University College London
Project : defi_econ
Topic   : uniswap.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch uniswap data.

"""

# Inport python modules
import os
from os import path
import datetime
from tqdm import tqdm

# Import internal modules
from environ.utils.info_logger import print_info_log
from environ.utils.config_parser import Config
from .fetch_uni_v2.select_top50_pairs_v2_script import select_top50_pairs_v2
from .fetch_uni_v3.select_top50_pairs_v3_script import select_top50_pairs_v3
from .fetch_uni_v2.top50_pair_directional_volume_v2_script import (
    top50_pair_directional_volume_v2,
)
from .fetch_uni_v3.top50_pair_directional_volume_v3_script import (
    top50_pair_directional_volume_v3,
)

# Fetch uniswap-related data
def fetch_uni(
    top50_list_label: str, start_date: datetime.datetime, end_date: datetime.datetime
) -> None:

    """
    Aggregate functon to fetch uniswap-related data.
    """
    # Initialize configuration
    config = Config()

    # Calculate period
    period = (end_date - start_date).days

    # List for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # List for to-do dates of Uniswap V2 for top 50 directional volume
    done_v2_directional_volume_list = os.listdir(
        path.join(
            config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
            "directional_volume/",
        )
    )
    date_list_v2 = [
        to_do_date
        for to_do_date in date_list
        if "top50_directional_volume_v2_" + to_do_date.strftime("%Y%m%d") + ".csv"
        not in done_v2_directional_volume_list
    ]

    # List for to-do dates of Uniswap V3 for top 50 directional volume
    done_v3_directional_volume_list = os.listdir(
        path.join(
            config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"],
            "directional_volume/",
        )
    )
    date_list_v3 = [
        to_do_date
        for to_do_date in date_list
        if "top50_directional_volume_v3_" + to_do_date.strftime("%Y%m%d") + ".csv"
        not in done_v3_directional_volume_list
    ]

    # Step 1: determine the list of monthly top 50 pools as candidates
    print_info_log("Fetch the list of monthly top 50 pools", "Uniswap V2")

    select_top50_pairs_v2(end_date - datetime.timedelta(1), period, top50_list_label)

    print_info_log("Fetch the list of monthly top 50 pools", "Uniswap V3")

    select_top50_pairs_v3(end_date - datetime.timedelta(1), period, top50_list_label)

    # Step 2: get directional daily volume for all dates based on the list in Step 1
    print_info_log("Fetch daily directional volume", "Uniswap V2")

    for date in tqdm(date_list_v2):
        try:
            top50_pair_directional_volume_v2(date, top50_list_label)
        except:
            print_info_log(
                f"Failed to fetch daily directional volume for {date} for Uniswap V2.",
                "Error",
            )

    print_info_log("Fetch daily directional volume", "Uniswap V3")

    for date in tqdm(date_list_v3):
        try:
            top50_pair_directional_volume_v3(date, top50_list_label)
        except:
            print_info_log(
                f"Failed to fetch daily directional volume for {date} for Uniswap V3.",
                "Error",
            )
