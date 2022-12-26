# -*- coding: utf-8 -*-
"""
Fetch the instant snapshot of Uniswap V2 and V3 Factory: Pool Count, Transaction Count
"""

from datetime import datetime
import pandas as pd
import scripts.subgraph_query as subgraph
from defi_econ.constants import UNISWAP_V2_DATA_PATH, UNISWAP_V3_DATA_PATH


def get_factory_overview_uniswap(
    factory_address: str, http: str, variables: list
) -> dict:
    """
    get the basic statistical overview of the factory
    """
    params_factory_addr = {"factory_id": factory_address}
    # Query instant factory overview
    overview_query = f"""
    query($factory_id: String!)
    {{
        {variables[0]}(id: $factory_id){{
            {variables[2]}
            {variables[3]}
            {variables[4]}
            {variables[5]}
            {variables[6]}
            {variables[7]}
        }}
    }}
    """
    overview = subgraph.run_query_var(http, overview_query, params_factory_addr)

    return overview


def get_instant_eth_price(http: str, variables: list) -> dict:
    """
    get the instant ETH price
    """
    # Query instant ETH price
    eth_price_query = f"""
    {{
        bundle(id: "1" ) {{
        {variables[8]}
        }}
    }}
    """
    eth_price = subgraph.run_query(http, eth_price_query)

    return eth_price


def uniswap_overview(
    overview_file: str,
    factory_address: str,
    http: str,
    variables: list,
) -> None:
    """
    Read and update the uniswap_overview.csv by adding one row snapshot of querying factory information
    """

    # Read the historical data from the existing file
    df_overview = pd.read_csv(overview_file, index_col="Unnamed: 0")

    # Get the executing time
    query_time = datetime.now()

    # Get the query result
    overview = get_factory_overview_uniswap(factory_address, http, variables)
    eth_price = get_instant_eth_price(http, variables)

    # Store the new results
    new_overview = pd.DataFrame(
        {
            variables[1]: [query_time],
            variables[2]: [overview["data"][variables[0]][variables[2]]],
            variables[3]: [overview["data"][variables[0]][variables[3]]],
            variables[4]: [overview["data"][variables[0]][variables[4]]],
            variables[5]: [overview["data"][variables[0]][variables[5]]],
            variables[6]: [overview["data"][variables[0]][variables[6]]],
            variables[7]: [overview["data"][variables[0]][variables[7]]],
            "ethPrice": [eth_price["data"]["bundle"][variables[8]]],
        }
    )

    # Add a new row to the dataframe
    df_overview = pd.concat([df_overview, new_overview], ignore_index=True, axis=0)

    # Update the file with the new query result
    df_overview.to_csv(overview_file)


if __name__ == "__main__":

    # Set the parameters for uniswap v2
    overview_file_v2 = UNISWAP_V2_DATA_PATH + "/overview/uniswap_v2_overview.csv"

    factory_address_v2 = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

    variables_v2 = [
        "uniswapFactory",
        "instant",
        "pairCount",
        "txCount",
        "totalVolumeETH",
        "totalVolumeUSD",
        "totalLiquidityETH",
        "totalLiquidityUSD",
        "ethPrice",
    ]

    # get the overview for uniswap v2
    uniswap_overview(
        overview_file_v2,
        factory_address_v2,
        subgraph.http_v2,
        variables_v2,
    )

    # Set the parameters for uniswap v3
    overview_file_v3 = UNISWAP_V3_DATA_PATH + "/overview/uniswap_v3_overview.csv"

    factory_address_v3 = "0x1F98431c8aD98523631AE4a59f267346ea31F984"

    variables_v3 = [
        "factory",
        "snapshotTime",
        "poolCount",
        "txCount",
        "totalVolumeETH",
        "totalVolumeUSD",
        "totalLiquidityETH",
        "totalLiquidityUSD",
        "ethPriceUSD",
    ]

    # get the overview for uniswap v3
    uniswap_overview(
        overview_file_v3,
        factory_address_v3,
        subgraph.http_v3,
        variables_v3,
    )
