# -*- coding: utf-8 -*-
"""
Fetch all pairs for Uniswap V2
"""

from datetime import date
from os import path
import pandas as pd
import scripts.subgraph_query as subgraph
from defi_econ.constants import UNISWAP_V2_DATA_PATH


def get_all_pools_v2() -> pd.DataFrame:
    """
    get all liquidity pools from the v2 protocol
    """
    # Start from fetching 1000 pairs as the initial Batch 0, order by created timestamp
    get_pairs_query_0 = """
  {
    pairs(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc) 
    { 
      token0 {
          id
          symbol
      }
      token1 {
          id
          symbol
      }
      id
      createdAtBlockNumber
      createdAtTimestamp
    }
  }
  """

    get_pairs_batch0 = subgraph.run_query(subgraph.http_v2, get_pairs_query_0)

    # Create a dataframe to store the pairs info, initializa with the first 1000 pairs
    df_all_pairs = pd.DataFrame.from_dict(get_pairs_batch0["data"]["pairs"])

    # Do iteration to fetch all the pairs, skip the first 1000 in batch 0
    # Start from the last timestamp which is got by batch 0

    iter_count = 0
    pairs_iter = get_pairs_batch0["data"]["pairs"]  # Pair info list in each batch
    total_pair_amount = len(
        pairs_iter
    )  # Initial the total pair amount by 1000 (in batch 0)

    # Do loop until
    while len(pairs_iter) == 1000:
        # The last timestamp in the previous query batch
        last_gt = int(pairs_iter[-1]["createdAtTimestamp"])
        params_gt = {"createdAtTimestamp_gt": last_gt}

        # Query 1000 new pairs from the last timestamp
        query_iter = """
    query ($createdAtTimestamp_gt: Int!) {
      pairs(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc
      where: {createdAtTimestamp_gt: $createdAtTimestamp_gt }) 
      { 
        token0 {
          id
          symbol
        }
        token1 {
          id
          symbol
        }
        id
        createdAtBlockNumber
        createdAtTimestamp
      }
    }
    """
        result_iter = subgraph.run_query_var(subgraph.http_v2, query_iter, params_gt)

        # List of pair info for this batch
        pairs_iter = result_iter["data"]["pairs"]

        # Add list of this batch to the dataframe
        df_all_pairs = df_all_pairs.append(pairs_iter, ignore_index=True)

        # Summary for this batch, and update iterator
        iter_count = iter_count + 1
        total_pair_amount = total_pair_amount + len(pairs_iter)
        print(
            "Batch ",
            iter_count,
            ": ",
            len(pairs_iter),
            " pairs fetched,  Total pairs: ",
            total_pair_amount,
        )
        print("             Start from timestamp: ", last_gt)

    print("---------------------------")
    print("Amount of fetced pairs: ", total_pair_amount)

    return df_all_pairs


if __name__ == "__main__":
    # File name contains the executing date of this script, the instant snapshot
    file_date = date.today().strftime("%Y%m%d")

    # Define the file name
    file_name = path.join(
        UNISWAP_V2_DATA_PATH, "uniswap_v2_all_pools_" + file_date + ".csv"
    )

    # Write dataframe to csv
    df_all_pools = get_all_pools_v2()
    df_all_pools.to_csv(file_name)
    print("-------------------------")
    print("complete write the file: ", file_name)
