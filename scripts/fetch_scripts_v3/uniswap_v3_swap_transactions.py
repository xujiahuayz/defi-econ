# -*- coding: utf-8 -*-
"""
Fetch swap trading for Uniswap V3
"""


import datetime
import calendar
from os import path
import pandas as pd
import scripts.subgraph_query as subgraph
from defi_econ.constants import UNISWAP_V3_DATA_PATH


def query_swaps_trading_v3(start_timestamp: int, end_timestamp: int) -> pd.DataFrame:
    """
    Get information of swaps transactions
    """

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
      pool{
        id
      }
      token0 {
          id
          symbol
      }
      token1 {
          id
          symbol
      }
      amount0
      amount1
      amountUSD
      sender
      recipient
      origin
    }
  }
  """

    get_swaps_batch0 = subgraph.run_query_var(
        subgraph.http_v3, get_swaps_query_0, params_start_gt
    )

    # Create a dataframe to store the basic structure of attributes, initializa with the first 1000 swaps
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
        pool{
          id
        }
        token0 {
            id
            symbol
        }
        token1 {
            id
            symbol
        }
        amount0
        amount1
        amountUSD
        sender
        recipient
        origin
      }
    }
    """

        result_iter = subgraph.run_query_var(subgraph.http_v3, query_iter, params_gt)

        # List of swaps for this batch
        swaps_iter = result_iter["data"]["swaps"]

        # Add list of this batch to the dataframe
        df_all_swaps = df_all_swaps.append(swaps_iter, ignore_index=True)

        # Summary for this batch, and update iterator
        iter_count = iter_count + 1
        total_swaps_amount = total_swaps_amount + len(swaps_iter)

        print(
            "Batch ",
            iter_count,
            ": ",
            len(swaps_iter),
            " swaps fetched,  Total swaps: ",
            total_swaps_amount,
        )
        print("Start from timestamp: ", last_gt)

    df_all_swaps = df_all_swaps.drop(
        df_all_swaps[df_all_swaps.timestamp >= str(end_timestamp)].index
    )

    df_all_swaps["transaction"] = df_all_swaps["transaction"].apply(lambda x: x["id"])
    df_all_swaps["pool"] = df_all_swaps["pool"].apply(lambda x: x["id"])
    df_all_swaps["token0_id"] = df_all_swaps["token0"].apply(lambda x: x["id"])
    df_all_swaps["token0_symbol"] = df_all_swaps["token0"].apply(lambda x: x["symbol"])
    df_all_swaps = df_all_swaps.drop(["token0"], axis=1)
    df_all_swaps["token1_id"] = df_all_swaps["token1"].apply(lambda x: x["id"])
    df_all_swaps["token1_symbol"] = df_all_swaps["token1"].apply(lambda x: x["symbol"])
    df_all_swaps = df_all_swaps.drop(["token1"], axis=1)

    print("---------------------------")
    print(
        "Amount of fetced swaps: ",
        total_swaps_amount
        - len(df_all_swaps[df_all_swaps.timestamp >= str(end_timestamp)]),
    )

    return df_all_swaps


def uniswap_v3_swaps(
    start_timestamp: int, end_timestamp: int, period_label: str
) -> None:
    """
    Fetch swap transactions in V3 and save to the file named with specific label (for time period)
    """

    file_name = path.join(
        UNISWAP_V3_DATA_PATH, "swap/uniswap_v3_swaps_" + period_label + ".csv"
    )
    df_all_swaps = query_swaps_trading_v3(start_timestamp, end_timestamp)
    df_all_swaps.to_csv(file_name)
    print("-------------------------")
    print("complete write the file: ", file_name)


if __name__ == "__main__":
    period_label = "JUL"

    start_date_UTC = datetime.datetime(2022, 7, 1, 0, 0)
    end_date_UTC = datetime.datetime(2022, 8, 1, 0, 0)

    start_timestamp = int(calendar.timegm(start_date_UTC.timetuple()))  # include
    end_timestamp = int(calendar.timegm(end_date_UTC.timetuple()))  # exclude

    print("Start Time: ", start_date_UTC, "  ", start_timestamp)
    print("End Time: ", end_date_UTC, "  ", end_timestamp)

    uniswap_v3_swaps(start_timestamp, end_timestamp, period_label)
