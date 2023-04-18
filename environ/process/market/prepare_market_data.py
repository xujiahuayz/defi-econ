"""
Script to preprocess the market data
"""

from environ.process.market.eth_gas import gas_eth_df
from environ.process.market.sp import sp_df
from environ.utils.variable_constructer import log_return, return_vol

# join two dataframes

market_data = sp_df.merge(gas_eth_df, on="Date", how="outer")

for v in ["S&P", "ether_price_usd", "gas_price_usd"]:
    market_data = log_return(market_data, v, rolling_window_return=1)
    market_data = return_vol(
        market_data, v, rolling_window_return=1, rolling_window_vol=30
    )
