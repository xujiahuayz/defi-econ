# -*- coding: utf-8 -*-
"""Fetch the instant snapshot of Uniswap V2 Factory: Pool Count, Transaction Count"""


import pandas as pd
from datetime import datetime

import subgraph_query as subgraph

def get_factory_overview_v2(factory_address):    
    params_factory_address = {"factory_id": factory_address}
    # Query instant factory overview
    v2_overview_query = """
    query($factory_id: String!)
    {
        uniswapFactory(id: $factory_id){
            totalVolumeUSD
            totalLiquidityUSD
            totalVolumeETH
            totalLiquidityETH
            pairCount
            txCount
        }
    }
    """
    v2_overview = subgraph.run_query_var(subgraph.http_v2, v2_overview_query, params_factory_address)

    return v2_overview

def get_instant_eth_price(http):
    # Query instant ETH price
    eth_price_query = """
    {
        bundle(id: "1" ) {
        ethPrice
        }
    }
    """
    eth_price = subgraph.run_query(subgraph.http_v2, eth_price_query)

    return eth_price



if __name__ == "__main__":
    # File path
    overview_file_v2 = "data_uniswap_v2/fetched_data_v2/uniswap_v2_overview.csv"

    # Factory address of Uniswap V2
    factory_address_v2 = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

    # Read the historical data from the existing file
    df_v2_overview = pd.read_csv(overview_file_v2, index_col="Unnamed: 0")

    # Get the executing time
    query_time = datetime.now()

    # Get the query result
    v2_overview = get_factory_overview_v2(factory_address_v2)
    eth_price = get_instant_eth_price(subgraph.http_v2)

    # Store the new results
    new_overview = pd.DataFrame({
        'instant': [query_time],
        'pairCount': [v2_overview['data']['uniswapFactory']['pairCount']],
        'txCount': [v2_overview['data']['uniswapFactory']['txCount']],
        'totalVolumeETH': [v2_overview['data']['uniswapFactory']['totalVolumeETH']],
        'totalVolumeUSD': [v2_overview['data']['uniswapFactory']['totalVolumeUSD']],
        'totalLiquidityETH': [v2_overview['data']['uniswapFactory']['totalLiquidityETH']],
        'totalLiquidityUSD': [v2_overview['data']['uniswapFactory']['totalLiquidityUSD']],
        'ethPrice': [eth_price['data']['bundle']['ethPrice']]
    })

    # Add a new row to the dataframe
    df_v2_overview = pd.concat([df_v2_overview, new_overview], ignore_index=True, axis=0)

    # Update the file with the new query result
    df_v2_overview.to_csv(overview_file_v2)
