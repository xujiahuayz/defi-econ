"""
Fetch the instant snapshot of Uniswap V2 Factory: Pool Count, Transaction Count
"""

from datetime import datetime
from os import path
import pandas as pd
import subgraph_query as subgraph
from defi_econ.constants import UNISWAP_V3_DATA_PATH


def get_factory_overview_v3(factory_address: str):
    """
    get the basic statistical overview of the factory
    """

    params_factory_addr = {"factory_id": factory_address}
    # Query instant factory overview
    v3_overview_query = """
    query($factory_id: String!)
    {
    factory(id: $factory_id){
        totalVolumeUSD
        totalValueLockedUSD
        totalVolumeETH
        totalValueLockedETH
        poolCount
        txCount
    }
    }
    """
    v3_overview = subgraph.run_query_var(
        subgraph.http_v3, v3_overview_query, params_factory_addr
    )

    return v3_overview


def get_instant_eth_price(http):
    """
    get the instant ETH price
    """

    # Query instant ETH price
    eth_price_query = """
    {
        bundle(id: "1" ) {
            ethPriceUSD
        }
    }
    """
    eth_price = subgraph.run_query(http, eth_price_query)

    return eth_price


if __name__ == "__main__":
    # File path
    overview_file_v3 = UNISWAP_V3_DATA_PATH + "/uniswap_v3_overview.csv"

    # Factory address of Uniswap V3
    factory_address_v3 = "0x1F98431c8aD98523631AE4a59f267346ea31F984"

    # Read the historical data from the existing file
    df_v3_overview = pd.read_csv(overview_file_v3, index_col="Unnamed: 0")

    # Get the executing time
    query_time = datetime.now()

    # Get the query result
    v3_overview = get_factory_overview_v3(factory_address_v3)
    eth_price = get_instant_eth_price(subgraph.http_v3)

    # Store the new results
    new_overview = pd.DataFrame(
        {
            "snapshotTime": [query_time],
            "poolCount": [v3_overview["data"]["factory"]["poolCount"]],
            "txCount": [v3_overview["data"]["factory"]["txCount"]],
            "totalVolumeETH": [v3_overview["data"]["factory"]["totalVolumeETH"]],
            "totalVolumeUSD": [v3_overview["data"]["factory"]["totalVolumeUSD"]],
            "totalValueLockedETH": [
                v3_overview["data"]["factory"]["totalValueLockedETH"]
            ],
            "totalValueLockedUSD": [
                v3_overview["data"]["factory"]["totalValueLockedUSD"]
            ],
            "ethPrice": [eth_price["data"]["bundle"]["ethPriceUSD"]],
        }
    )

    # Add a new row to the dataframe
    df_v3_overview = pd.concat(
        [df_v3_overview, new_overview], ignore_index=True, axis=0
    )

    # Update the file with the new query result
    df_v3_overview.to_csv(overview_file_v3)
