# -*- coding: utf-8 -*-

import pandas as pd
from datetime import date

# Data Source: https://etherscan.io/chart/gasprice
df_gas_fee = pd.read_csv('ethereum/data_source/etherscan_avg_gas_price.csv', index_col='Date(UTC)')
df_gas_fee['Value (GWei)'] = df_gas_fee['Value (Wei)'] * (10 ** (-9))
df_gas_fee['Value (ETH)'] = df_gas_fee['Value (Wei)'] * (10 ** (-18))

# Data Source: https://etherscan.io/chart/etherprice
df_eth_price = pd.read_csv('ethereum/data_source/etherscan_ether_price.csv', index_col='Date(UTC)')
df_eth_price.rename(columns={'Value':'ETH Price (USD)'}, inplace=True)
df_gas_fee_usd = pd.concat([df_gas_fee, df_eth_price.drop(columns=['UnixTimeStamp'])], axis=1)

df_gas_fee_usd['Gas Fee USD'] = df_gas_fee_usd['Value (ETH)'] * df_gas_fee_usd['ETH Price (USD)']

# Write dataframe to csv
# file name contains the executing date of this script, includes the historical info until this date
file_date = date.today().strftime("%Y%m%d")
file_name = "ethereum/avg_gas_fee_"+file_date+".csv"
df_gas_fee_usd.to_csv(file_name)
print("-------------------------")
print("complete write the file: ", file_name)