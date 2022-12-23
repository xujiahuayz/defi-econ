"""

University College London
Project : defi_econ
Topic   : uniswap.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch uniswap data.

"""
import datetime
from .fetch_uni_v2.top50_pair_directional_volume_v2 import select_top50_pairs_v2

# Fetch uniswap-related data


def fetch_uni():
    period = 31
    end_date = datetime.datetime(2022, 5, 31, 0, 0)

    # Fetch the list of top 50 pairs in volume
    select_top50_pairs_v2(end_date, period, "2022MAY")
