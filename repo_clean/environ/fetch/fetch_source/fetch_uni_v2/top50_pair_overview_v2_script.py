# -*- coding: utf-8 -*-
"""
Overview of the Top 50 Pairs (All Time) with Transaction Count
"""

from datetime import date
from datetime import datetime
from os import path
import pandas as pd
from tqdm import tqdm
import repo_clean.environ.fetch.fetch_utils.subgraph_query as subgraph
from repo_clean.environ.utils.config_parser import Config


def get_pool_overview(batch_pair_id: str) -> dict:
    """
    get the basic data of the liquidity pool
    """
    # Variables for the query
    params_batch_pair = {"batch_pair": batch_pair_id}

    # Query the basic pair info
    batch_pair_overview_query = """
    query($batch_pair: String!) 
    {
      pair(id: $batch_pair){
        createdAtTimestamp
        totalSupply
        reserve0
        reserve1
        reserveUSD
        txCount
      }
    }
  """
    batch_pair_overview = subgraph.run_query_var(
        subgraph.http_v2, batch_pair_overview_query, params_batch_pair
    )

    # Query result for this pair
    batch_pair_info = batch_pair_overview["data"]["pair"]

    return batch_pair_info


def count_mints_transactions(batch_pair_id: str) -> int:
    """
    count the total mints transaction for the pool from it starts
    """
    # Variables for the query
    params_batch_pair = {"batch_pair": batch_pair_id}

    # Iteration for counting mints transactions
    # Start from counting the initial Batch 0: Query 1000 transactions order by timestamp
    get_mints_batch0_query = """
    query($batch_pair: String!)
    {
      mints(first: 1000, orderBy: timestamp, orderDirection: asc, where:
        { pair: $batch_pair })
        {
          transaction {
            id
            timestamp
          }
          amountUSD
        }
    }
  """
    get_mints_batch0 = subgraph.run_query_var(
        subgraph.http_v2, get_mints_batch0_query, params_batch_pair
    )

    # Global variable for counting mints
    mints_iter_count = 0
    mints_tx_iter = get_mints_batch0["data"]["mints"]  # Result for each batch
    total_mints = len(mints_tx_iter)

    # Do loop until
    while len(mints_tx_iter) == 1000:
        # The last timestamp in the previous query batch
        last_mints_gt = int(mints_tx_iter[-1]["transaction"]["timestamp"])
        params_mints_gt = {"batch_pair": batch_pair_id, "timestamp_gt": last_mints_gt}

        # Query 1000 new mints from the last timestamp
        get_mints_query = """
      query ($batch_pair: String!, $timestamp_gt: Int!) {
        mints(first: 1000, orderBy: timestamp, orderDirection: asc, where:
          { pair: $batch_pair,
            timestamp_gt: $timestamp_gt })
            {
              transaction {
                id
                timestamp
              }
              amountUSD
            }
      }
    """
        get_mints = subgraph.run_query_var(
            subgraph.http_v2, get_mints_query, params_mints_gt
        )
        mints_tx_iter = get_mints["data"]["mints"]

        # Summary of this batch for counting mints
        mints_iter_count = mints_iter_count + 1
        total_mints = total_mints + len(mints_tx_iter)
    # End of while loop for counting mints

    return total_mints


def count_burns_transactions(batch_pair_id: str) -> int:
    """
    count the total burns transaction for the pool from it starts
    """
    # Variables for the query
    params_batch_pair = {"batch_pair": batch_pair_id}

    # Iteration for counting burns transactions
    # Start from counting the initial Batch 0: Query 1000 transactions order by timestamp
    get_burns_batch0_query = """
    query($batch_pair: String!)
    {
      burns(first: 1000, orderBy: timestamp, orderDirection: asc, where:
        { pair: $batch_pair })
        {
          transaction {
            id
            timestamp
          }
          amountUSD
        }
    }
  """
    get_burns_batch0 = subgraph.run_query_var(
        subgraph.http_v2, get_burns_batch0_query, params_batch_pair
    )

    # Global variable for counting burns
    burns_iter_count = 0
    burns_tx_iter = get_burns_batch0["data"]["burns"]  # Result for each batch
    total_burns = len(burns_tx_iter)

    # Do loop until
    while len(burns_tx_iter) == 1000:
        # The last timestamp in the previous query batch
        last_burns_gt = int(burns_tx_iter[-1]["transaction"]["timestamp"])
        params_burns_gt = {"batch_pair": batch_pair_id, "timestamp_gt": last_burns_gt}

        # Query 1000 new burns from the last timestamp
        get_burns_query = """
      query ($batch_pair: String!, $timestamp_gt: Int!) {
        burns(first: 1000, orderBy: timestamp, orderDirection: asc, where:
          { pair: $batch_pair,
             timestamp_gt: $timestamp_gt })
            {
              transaction {
                id
                timestamp
              }
              amountUSD
            }
      }
    """
        get_burns = subgraph.run_query_var(
            subgraph.http_v2, get_burns_query, params_burns_gt
        )
        burns_tx_iter = get_burns["data"]["burns"]

        # Summary of this batch for counting burns
        burns_iter_count = burns_iter_count + 1
        total_burns = total_burns + len(burns_tx_iter)
    # End of while loop for counting mints

    return total_burns


def top50_pair_overview_v2(list_label: str) -> None:
    """
    Get the historical information of top50 pools until the executing time, save to csv
    """

    # Initialize configuration
    config = Config()

    file_source = (
        config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"]
        + "/pool_list/top50_pairs_list_v2_"
        + list_label
        + ".csv"
    )
    # Load the dataframe from the top 50 pairs of May
    df_top50_pairs_overview = pd.read_csv(file_source)
    df_top50_pairs_overview = df_top50_pairs_overview.drop(
        columns=[
            "Unnamed: 0",
            "pastTotalVolumeUSD",
            "pastValidDays",
            "avgDailyVolumeUSD",
        ]
    )

    # Do iteration to count all transactions for each pair
    for index, row in tqdm(
        df_top50_pairs_overview.iterrows(), total=df_top50_pairs_overview.shape[0]
    ):
        # get the pool id for this pair
        batch_pair_id = row["pairAddress"]

        # Get the pair overview of this pair
        batch_pair_info = get_pool_overview(batch_pair_id)
        # Store values for the pool overview
        df_top50_pairs_overview.loc[index, "createdDate"] = datetime.fromtimestamp(
            int(batch_pair_info["createdAtTimestamp"])
        )
        df_top50_pairs_overview.loc[index, "totalSupply"] = batch_pair_info[
            "totalSupply"
        ]
        df_top50_pairs_overview.loc[index, "pooledToken0"] = batch_pair_info["reserve0"]
        df_top50_pairs_overview.loc[index, "pooledToken1"] = batch_pair_info["reserve1"]
        df_top50_pairs_overview.loc[index, "totalLiquidityUSD"] = batch_pair_info[
            "reserveUSD"
        ]
        df_top50_pairs_overview.loc[index, "txCount"] = batch_pair_info["txCount"]

        # Get the count of the mints transactions
        total_mints = count_mints_transactions(batch_pair_id)
        # Store the mints count to the dataframe
        df_top50_pairs_overview.loc[index, "mintsCount"] = total_mints

        # Get the count of the burns transactions
        total_burns = count_burns_transactions(batch_pair_id)
        # Store the burns count to the dataframe
        df_top50_pairs_overview.loc[index, "burnsCount"] = total_burns

        # the count of swaps: swaps are too much to count one by one, so just do subtraction
        total_swaps = int(batch_pair_info["txCount"]) - total_mints - total_burns
        df_top50_pairs_overview.loc[index, "swapsCount"] = total_swaps

    # End of the for loop (for each pair)

    # file name contains the executing date of this script
    file_date = date.today().strftime("%Y%m%d")
    # Define the file name
    file_name = path.join(
        config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
        "overview/top50_pairs_overview_v2_" + file_date + ".csv",
    )

    # Write dataframe to csv
    df_top50_pairs_overview.to_csv(file_name)
