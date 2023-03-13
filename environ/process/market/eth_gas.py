"""
process etherprice and gasprice data
"""

from pathlib import Path
import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# read the data
gas_df = pd.read_csv(
    Path(GLOBAL_DATA_PATH) / "gasprice.csv",
    index_col=None,
    parse_dates=["Date(UTC)"],
)

gas_df.columns = ["Date", "timestamp", "gas_price_wei"]

# read the data and specify date column as datetime
ether_df = pd.read_csv(
    Path(GLOBAL_DATA_PATH) / "etherprice.csv",
    index_col=None,
    parse_dates=["Date(UTC)"],
)

ether_df.columns = ["Date", "timestamp", "ether_price_usd"]

# join the two dataframes with all rows
gas_eth_df = gas_df.merge(ether_df, on=["Date", "timestamp"], how="outer")
gas_eth_df["gas_price_usd"] = (
    gas_eth_df["gas_price_wei"] * gas_eth_df["ether_price_usd"] / 1e18
)
