"""

University College London
Project : defi_econ
Topic   : data_fetcher.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Fetch DeFi data.

"""

from .fetch_source.uniswap import fetch_uni


def fetch_data():
    fetch_uni()
