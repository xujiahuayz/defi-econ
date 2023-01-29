# -*- coding: utf-8 -*-
"""
Convert the gas fee to USD
"""

from datetime import date
from os import path
import pandas as pd
from defi_econ.constants import GLOBAL_DATA_PATH


if __name__ == "__main__":
    # Data Source: https://etherscan.io/chart/gasprice
    df_gas_fee = pd.read_csv(
        GLOBAL_DATA_PATH + "/gas_fee/data_source/etherscan_avg_gas_price.csv",
        index_col="Date(UTC)",
    )
    df_gas_fee["Value (GWei)"] = df_gas_fee["Value (Wei)"] * (10 ** (-9))
    df_gas_fee["Value (ETH)"] = df_gas_fee["Value (Wei)"] * (10 ** (-18))

    # Data Source: https://etherscan.io/chart/etherprice
    df_eth_price = pd.read_csv(
        GLOBAL_DATA_PATH + "/gas_fee/data_source/etherscan_ether_price.csv",
        index_col="Date(UTC)",
    )
    df_eth_price.rename(columns={"Value": "ETH Price (USD)"}, inplace=True)
    df_gas_fee_usd = pd.concat(
        [df_gas_fee, df_eth_price.drop(columns=["UnixTimeStamp"])], axis=1
    )

    df_gas_fee_usd["Gas Fee USD"] = (
        df_gas_fee_usd["Value (ETH)"] * df_gas_fee_usd["ETH Price (USD)"]
    )

    # Write dataframe to csv
    # file name contains the executing date of this script, includes the historical info until this date
    file_date = date.today().strftime("%Y%m%d")
    file_name = path.join(GLOBAL_DATA_PATH, "gas_fee/avg_gas_fee.csv")
    df_gas_fee_usd.to_csv(file_name)
    print("-------------------------")
    print("complete write the file: ", file_name)
