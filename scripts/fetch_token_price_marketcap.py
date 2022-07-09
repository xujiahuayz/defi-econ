# -*- coding: utf-8 -*-
"""
Fetch the historical price and market cap for tokens from coingecko
Note: the data for market cap of WETH is not available
"""


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import calendar

# Unofficial API python package for CoinGeckoAPI
# * Attribution required: https://www.coingecko.com/en/api
from pycoingecko import CoinGeckoAPI


if __name__ == "__main__": 
  # Define the horizon of fecting historical data
  start_date = datetime(2020, 1, 1, 0, 0)
  end_date = datetime(2022, 7, 1, 0, 0)

  # Define the currency of unit
  target_currency = 'usd'

  # Refer to CoinGecko API Token List
  # https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit#gid=0
  # token symbol is not unique variable, so that manually check from the doc to get id is recommended
  primary_token_dict = {
      'USDC': 'usd-coin',
      'WETH': 'weth',
      'DAI': 'dai',
      'WBTC': 'wrapped-bitcoin',
      'USDT': 'tether',
      'FRAX': 'frax',
      'PAX': 'paxos-standard',
      'agEUR': 'ageur',
      'APE': 'apecoin',
      '1INCH': '1inch',
      'BUSD': 'binance-usd',
      'FEI': 'fei-usd',
      'HEX': 'hex',
      'RAI': 'rai',
      'LOOKS': 'looksrare',
      'renBTC': 'renbtc',
      'MKR': 'maker',
      'LINK': 'chainlink',
      'ETH2x-FLI': 'eth-2x-flexible-leverage-index',
      'MATIC': 'matic-network',
      'TUSD': 'true-usd',
      'EURS': 'stasis-eurs',
      'CRV': 'curve-dao-token',
      'NEXO': 'nexo',
      'FUN': 'funfair',
      'ENS': 'ethereum-name-service',
      'LUNA': 'terra-luna-2',
      'MIM': 'magic-internet-money',
      'LUSD': 'liquity-usd'
  }

  # Convert the date (UTC) to unix timestamp
  start_timestamp = str(calendar.timegm(start_date.timetuple()))
  end_timestamp = str(calendar.timegm(end_date.timetuple()))

  # List of candidate dates
  candidate_date = []
  candidate_timestamp = []
  for date_count in range((end_date - start_date).days + 1):
    aggregate_date = start_date + timedelta(days=date_count)
    candidate_date.append(aggregate_date)
    candidate_timestamp.append(int(calendar.timegm(aggregate_date.timetuple())))

  # Initialize the dataframe for the historical data
  df_price = pd.DataFrame({'Date': candidate_date}, index=candidate_timestamp)
  df_marketcap = pd.DataFrame({'Date': candidate_date}, index=candidate_timestamp)

  # Initialize the CoinGeckoAPI instance
  cg = CoinGeckoAPI()

  # Iterate for fetching the historical data
  for symbol, coin_id in primary_token_dict.items():
    # Fetch the data
    print(coin_id)
    token_historical_data = cg.get_coin_market_chart_range_by_id(id=coin_id, vs_currency=target_currency, from_timestamp=start_timestamp, to_timestamp=end_timestamp)
    
    # keep speed limitation
    time.sleep(3)

    # Initialize the column for token
    df_price[symbol] = np.nan
    df_marketcap[symbol] = np.nan

    # Store the value
    for price_pair in token_historical_data['prices']:
      df_price.loc[price_pair[0]/1000, symbol] = price_pair[1]

    # Store the value
    for mktcap_pair in token_historical_data['market_caps']:
      df_marketcap.loc[mktcap_pair[0]/1000, symbol] = mktcap_pair[1]

  # Write data to csv
  df_price.to_csv("global_data/token_market/primary_token_price.csv")
  df_marketcap.to_csv("global_data/token_market/primary_token_marketcap.csv")
