# -*- coding: utf-8 -*-
"""
Fetch all tokens for Uniswap V2
"""

from datetime import date
from os import path
import pandas as pd
import scripts.subgraph_query as subgraph
from defi_econ.constants import UNISWAP_V2_DATA_PATH


def get_all_tokens_v2():
    """
    get all tokens from the v2 protocol
    """

    # Start from fetching the initial Batch 0: Query 1000 tokens on UNISWAP V2 order by id (asc)
    get_all_tokens_batch0_query = """
  {
    tokens(first: 1000, orderBy: id, orderDirection: asc) {
      id
      name
      symbol
    }
  }
  """
    get_all_tokens_batch0 = subgraph.run_query(
        subgraph.http_v2, get_all_tokens_batch0_query
    )

    # Create a dataframe to store the tokens info, initializa with the first 1000 tokens
    df_all_tokens = pd.DataFrame.from_dict(get_all_tokens_batch0["data"]["tokens"])

    # Do iteration to fetch all the tokens, skip the first 1000 in batch 0
    # Start from the last id which is got by batch 0

    tokens_iter_count = 0
    tokens_iter = get_all_tokens_batch0["data"][
        "tokens"
    ]  # Token info list in each batch
    total_tokens_amount = len(
        tokens_iter
    )  # Initial the total token amount by 1000 (in batch 0)

    # Do loop until
    while len(tokens_iter) == 1000:
        # The last id in the previous query batch
        last_id_gt = str(tokens_iter[-1]["id"])
        params_id_gt = {"id_in": last_id_gt}

        # Query 1000 new tokens from the last id
        query_iter = """
    query tokens($id_in: String!) {
      tokens(first: 1000, orderBy: id, orderDirection: asc
      where: {id_gt: $id_in }) 
      { 
        id
        name
        symbol
      }
    }
    """
        tokens_result_iter = subgraph.run_query_var(
            subgraph.http_v2, query_iter, params_id_gt
        )

        # List of token info for this batch
        tokens_iter = tokens_result_iter["data"]["tokens"]

        # Add list of this batch to the dataframe
        df_all_tokens = df_all_tokens.append(tokens_iter, ignore_index=True)

        # Summary for this batch, and update iterator
        tokens_iter_count = tokens_iter_count + 1
        total_tokens_amount = total_tokens_amount + len(tokens_iter)
        print(
            "Batch ",
            tokens_iter_count,
            ": ",
            len(tokens_iter),
            " tokens fetched, Total tokens: ",
            total_tokens_amount,
        )
        print("             Start from id: ", last_id_gt)

    print("---------------------------")
    print("Amount of fetced tokens: ", total_tokens_amount)

    return df_all_tokens


if __name__ == "__main__":
    # File name contains the executing date of this script, the instant snapshot
    file_date = date.today().strftime("%Y%m%d")

    # Define the file name
    file_name = path.join(
        UNISWAP_V2_DATA_PATH, "uniswap_v2_all_tokens_" + file_date + ".csv"
    )

    # Write dataframe to csv
    df_all_tokens = get_all_tokens_v2()
    df_all_tokens.to_csv(file_name)
    print("-------------------------")
    print("complete write the file: ", file_name)
