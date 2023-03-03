# -*- coding: utf-8 -*-

"""
Fetch swap transactions of Uniswap V2
"""

from os import path
from time import sleep
import warnings
import pandas as pd
from numpy import random

import environ.fetch.fetch_utils.subgraph_query as subgraph
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log

warnings.filterwarnings("ignore")


def query_swaps_trading_v2(start_timestamp: int, end_timestamp: int) -> pd.DataFrame:
    """
    Get information of swaps transactions
    """

    # Initialize configuration
    config = Config()

    # Start from fetching 1000 swaps as the initial Batch 0, order by created timestamp
    start_gt = start_timestamp - 1
    params_start_gt = {"start_timestamp_gt": start_gt}
    get_swaps_query_0 = """
    query ($start_timestamp_gt: Int!){
      swaps(first: 1000, orderBy: timestamp, orderDirection: asc, where: {timestamp_gt: $start_timestamp_gt }) 
    { 
      id
      transaction{
        id
      }
      timestamp
      pair{
        id
        token0 {
          id
          symbol
        }
        token1 {
          id
          symbol
        }
      }

      amount0In
      amount0Out
      amount1In
      amount1Out
      amountUSD
      sender
      to
    }
  }
  """

    get_swaps_batch0 = subgraph.run_query_var(
        config["dev"]["config"]["subgraph"]["HTTP_V2"],
        get_swaps_query_0,
        params_start_gt,
    )

    # Create a dataframe to store the basic structure of attributes,
    # initializa with the first 1000 swaps
    df_all_swaps = pd.DataFrame.from_dict(get_swaps_batch0["data"]["swaps"])

    # Do iteration to fetch all the swap tradings, skip the first 1000 in batch 0
    # Start from the last timestamp which is got by batch 0

    iter_count = 0
    swaps_iter = get_swaps_batch0["data"][
        "swaps"
    ]  # Initialize entity for each batch (last fetched)
    total_swaps_amount = len(
        swaps_iter
    )  # Initial the total swaps count with the count in batch 0

    # Do loop until

    while int(swaps_iter[-1]["timestamp"]) < end_timestamp:
        # The last trading timestamp in the previous query batch
        last_gt = int(swaps_iter[-1]["timestamp"])
        params_gt = {"timestamp_gt": last_gt}

        # Query 1000 new pairs from the last timestamp
        query_iter = """
      query ($timestamp_gt: Int!){
        swaps(first: 1000, orderBy: timestamp, orderDirection: asc, where: {timestamp_gt: $timestamp_gt }) 
      { 
        id
        transaction{
          id
        }
        timestamp
        pair{
          id
          token0 {
            id
            symbol
          }
          token1 {
            id
            symbol
          }
        }

        amount0In
        amount0Out
        amount1In
        amount1Out
        amountUSD
        sender
        to
      }
    }
    """
        result_iter = subgraph.run_query_var(
            config["dev"]["config"]["subgraph"]["HTTP_V2"], query_iter, params_gt
        )
        if list(result_iter.keys()) == ["data"]:
            # List of swaps for this batch
            swaps_iter = result_iter["data"]["swaps"]

            # Add list of this batch to the dataframe
            df_all_swaps = df_all_swaps.append(swaps_iter, ignore_index=True)

            # Summary for this batch, and update iterator
            iter_count = iter_count + 1
            total_swaps_amount = total_swaps_amount + len(swaps_iter)

            print_info_log(f"Batch {iter_count} fetched", "Uniswap V2")

    df_all_swaps = df_all_swaps.drop(
        df_all_swaps[df_all_swaps.timestamp >= str(end_timestamp)].index
    )

    df_all_swaps["transaction"] = df_all_swaps["transaction"].apply(lambda x: x["id"])
    df_all_swaps["pool"] = df_all_swaps["pair"].apply(lambda x: x["id"])
    df_all_swaps["token0_id"] = df_all_swaps["pair"].apply(lambda x: x["token0"]["id"])
    df_all_swaps["token0_symbol"] = df_all_swaps["pair"].apply(
        lambda x: x["token0"]["symbol"]
    )
    df_all_swaps["token1_id"] = df_all_swaps["pair"].apply(lambda x: x["token1"]["id"])
    df_all_swaps["token1_symbol"] = df_all_swaps["pair"].apply(
        lambda x: x["token1"]["symbol"]
    )

    df_all_swaps = df_all_swaps.drop(["pair"], axis=1)

    fetched_swaps_amount = total_swaps_amount - len(
        df_all_swaps[df_all_swaps.timestamp >= str(end_timestamp)]
    )
    print_info_log(
        f"Amount of fetced swaps: {fetched_swaps_amount}",
        "Uniswap V2",
    )

    return df_all_swaps


def uniswap_v2_swaps(
    start_timestamp: int, end_timestamp: int, period_label: str
) -> None:
    """
    Fetch swap transactions in V2 and save to the file named with specific label (for time period)
    """

    # Initialize configuration
    config = Config()

    file_name = path.join(
        config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
        "swap/uniswap_v2_swaps_" + period_label + ".csv",
    )
    df_all_swaps = query_swaps_trading_v2(start_timestamp, end_timestamp)

    df_all_swaps.to_csv(file_name)
    sleep(random.randint(10, 100) / 100)
