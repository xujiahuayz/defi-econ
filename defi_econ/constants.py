"""
Data path setting
"""

from os import path
from defi_econ.settings import PROJECT_ROOT


DATA_PATH = path.join(PROJECT_ROOT, "data")
UNISWAP_V2_DATA_PATH = path.join(DATA_PATH, "data_uniswap_v2")
UNISWAP_V3_DATA_PATH = path.join(DATA_PATH, "data_uniswap_v3")
COMPOUND_DATA_PATH = path.join(DATA_PATH, "data_compound")
AAVE_DATA_PATH = path.join(DATA_PATH, "data_aave")
GLOBAL_DATA_PATH = path.join(DATA_PATH, "data_global")
NETWORK_DATA_PATH = path.join(DATA_PATH, "data_network")
