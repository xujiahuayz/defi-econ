# -*- coding: utf-8 -*-
"""
Compute Directional Daily Volume USD for Top 50 Pairs
"""

import datetime
import calendar
from os import path
import pandas as pd
from tqdm import tqdm
import environ.fetch.fetch_utils.subgraph_query as subgraph
from environ.utils.config_parser import Config


def get_gross_volume(batch_pair_id: str, date_timestamp: int) -> list:
    """
    fetch the gross daily volume by API
    """
    # Variables for the query
    params_batch_pair = {"batch_pair": batch_pair_id, "date_timestamp": date_timestamp}

    # Query the daily aggregated info (gross volume USD)
    batch_pair_daily_query = """
    query ($batch_pair: String!, $date_timestamp: Int!) 
    {
      poolDayDatas(
        where: {
          pool: $batch_pair,
          date: $date_timestamp
        })
        {
          txCount
          volumeToken0
          volumeToken1
          volumeUSD
          tvlUSD
        }
      }
  """
    batch_pair_daily = subgraph.run_query_var(
        subgraph.HTTP_V3, batch_pair_daily_query, params_batch_pair
    )
    # Query result for this pair
    batch_pair_gross_info = batch_pair_daily["data"]["poolDayDatas"]

    return batch_pair_gross_info


def count_daily_mints(
    batch_pair_id: str, date_timestamp: int, end_timestamp: int
) -> int:
    """
    get all mints transactions and count daily mints
    """
    # Iteration for counting the mints transactions within the date
    # Global variables
    mints_count = 0
    last_timestamp_gt = date_timestamp - 1

    # If the last timestamp for the previous batch is earlier than the end timestamp
    while last_timestamp_gt < end_timestamp:
        params_mints_gt = {
            "batch_pair": batch_pair_id,
            "last_timestamp_gt": last_timestamp_gt,
        }
        # Get all mints transactions
        mints_batch_query = """
        query($batch_pair: String!, $last_timestamp_gt: Int!)
        {
            mints(first: 1000, 
            where: {
                pool: $batch_pair,
                timestamp_gt: $last_timestamp_gt
            }, orderBy: timestamp, orderDirection: asc)
            {
            transaction {
                id
            }
            timestamp
            amountUSD
            }
        }
        """
        mints_batch = subgraph.run_query_var(
            subgraph.HTTP_V3, mints_batch_query, params_mints_gt
        )

        # Check whether the api returns data
        if list(mints_batch.keys()) == ["data"]:

            # Mint transactions in this batch
            mints_txs_batch = mints_batch["data"]["mints"]

            # Fix issue: no transaction in the next day
            if len(mints_txs_batch) == 0:
                break

            # Do loop to observe each mint transaction
            for i, _ in enumerate(mints_txs_batch):
                # Update the last_timestamp
                # last_ts_gt >= end_ts after the executing of loop break
                last_timestamp_gt = int(mints_txs_batch[i]["timestamp"])

                # Only count transactions within the given date of this batch
                if int(mints_txs_batch[i]["timestamp"]) < end_timestamp:
                    # Count++ for the valid swap
                    mints_count = mints_count + 1

                # Stop loop when the timestamp exceed the end timestamp
                else:
                    break

        # End of the for loop, we got the transactions in this batch
    # End of the while loop, we got the transactions for all batchs

    return mints_count


def count_daily_burns(
    batch_pair_id: str, date_timestamp: int, end_timestamp: int
) -> int:
    """
    get all burns transactions and count daily burns
    """
    # Iteration for counting the burns transactions within the date
    # Global variables
    burns_count = 0
    # Initialize the last timestamp
    last_timestamp_gt = date_timestamp - 1

    # If the last timestamp for the previous batch is earlier than the end timestamp
    while last_timestamp_gt < end_timestamp:
        params_burns_gt = {
            "batch_pair": batch_pair_id,
            "last_timestamp_gt": last_timestamp_gt,
        }
        # Get all burns transactions
        burns_batch_query = """
      query($batch_pair: String!, $last_timestamp_gt: Int!)
      {
        burns(first: 1000, 
          where: {
            pool: $batch_pair,
            timestamp_gt: $last_timestamp_gt
          }, orderBy: timestamp, orderDirection: asc)
        {
          transaction {
            id
          }
          timestamp
          amountUSD
        }
      }
    """
        burns_batch = subgraph.run_query_var(
            subgraph.HTTP_V3, burns_batch_query, params_burns_gt
        )

        # burns transactions in this batch
        burns_txs_batch = burns_batch["data"]["burns"]

        # Fix issue: no transaction in the next day
        if len(burns_txs_batch) == 0:
            break

        # Do loop to observe each burns transaction
        for i, _ in enumerate(burns_txs_batch):
            # Update the last_timestamp
            # last_ts_gt >= end_ts after the executing of loop break
            last_timestamp_gt = int(burns_txs_batch[i]["timestamp"])

            # Only count transactions within the given date of this batch
            if int(burns_txs_batch[i]["timestamp"]) < end_timestamp:
                # Count++ for the valid swap
                burns_count = burns_count + 1

            # Stop loop when the timestamp exceed the end timestamp
            else:
                break

        # End of the for loop, we got the transactions in this batch
    # End of the while loop, we got the transactions for all batchs

    return burns_count


def compute_daily_directional_volume(
    batch_pair_id: str, date_timestamp: int, end_timestamp: int
) -> tuple[int, int, float, int, float]:
    """
    manually compute the directional volume by iterating each transaction
    """
    # Iteration for calculating directional daily volume USD
    # by summing swaps of token 0->1 and 1->0

    # Global variables
    swaps_count = 0
    tx_0to1_count = 0
    tx_1to0_count = 0
    volume_0to1 = 0.0
    volume_1to0 = 0.0

    # Initialize the last timestamp
    last_timestamp_gt = date_timestamp - 1

    # If the last timestamp for the previous batch is earlier than the end timestamp
    while last_timestamp_gt < end_timestamp:
        params_swaps_gt = {
            "batch_pair": batch_pair_id,
            "last_timestamp_gt": last_timestamp_gt,
        }
        # Get all transactions within the date
        swaps_batch_query = """
      query($batch_pair: String!, $last_timestamp_gt: Int!)
      {
        swaps(first: 1000, 
          where: {
            pool: $batch_pair,
            timestamp_gt: $last_timestamp_gt
          }, orderBy: timestamp, orderDirection: asc)
        {
          transaction {
            id
          }
          timestamp
          amount0
          amount1
          amountUSD
        }
      }
    """
        swaps_batch = subgraph.run_query_var(
            subgraph.HTTP_V3, swaps_batch_query, params_swaps_gt
        )

        # Check whether the api returns data
        if list(swaps_batch.keys()) == ["data"]:

            # Swap transactions in this batch
            swaps_txs_batch = swaps_batch["data"]["swaps"]

            # Fix issue: no transaction in the next day
            if len(swaps_txs_batch) == 0:
                break

            # Do loop to observe each swap transaction
            for i, _ in enumerate(swaps_txs_batch):
                # Update the last_timestamp no matter which type of transaction it is
                # last_ts_gt >= end_ts after the executing of loop break
                last_timestamp_gt = int(swaps_txs_batch[i]["timestamp"])

                # Only count transactions within the given date
                if int(swaps_txs_batch[i]["timestamp"]) < end_timestamp:
                    # Count++ for the valid swap
                    swaps_count = swaps_count + 1

                    # For swaps: token0 to token1
                    # A.K.A. SWAP token0 for token1, token0 IN, token1 OUT
                    # 0IN != 0 (must), 0OUT == 0, 1IN == 0, 1OUT != 0 (must)
                    # V3: 0IN -> amount 0 > 0, 1OUT -> amount1 < 0
                    if (float(swaps_txs_batch[i]["amount0"]) > 0.0) and (
                        float(swaps_txs_batch[i]["amount1"]) < 0.0
                    ):
                        tx_0to1_count = tx_0to1_count + 1
                        volume_0to1 = volume_0to1 + float(
                            swaps_txs_batch[i]["amountUSD"]
                        )

                    # For swaps: token1 to token0
                    # A.K.A. SWAP token1 for token0, token0 OUT, token1 IN
                    # 0IN == 0 (or not?), 0OUT != 0 (must), 1IN != 0 (Must), 1OUT == 0
                    # V3: 0OUT -> amount0<0,  1IN -> amount1>0
                    elif (float(swaps_txs_batch[i]["amount1"]) > 0.0) and (
                        float(swaps_txs_batch[i]["amount0"]) < 0.0
                    ):
                        tx_1to0_count = tx_1to0_count + 1
                        volume_1to0 = volume_1to0 + float(
                            swaps_txs_batch[i]["amountUSD"]
                        )

                    # Theoretically no transactions here
                    else:
                        pass
                        # print(
                        #     "Invest what happens on this transaction: ",
                        #     swaps_txs_batch[i]["transaction"]["id"],
                        # )

                # Stop loop when the timestamp exceed the end timestamp
                else:
                    break

            # End the for loop (finish summing this batch)
        # End the while loop (finish summing all batch)

    return swaps_count, tx_0to1_count, volume_0to1, tx_1to0_count, volume_1to0


def top50_pair_directional_volume_v3(
    aggregate_date: datetime, token_list_label: str
) -> None:
    """
    Get the directional volume and transaction counts, then save to file
    """
    # Initialize configuration
    config = Config()

    # Convert the readable date to the unix timestamp
    date_timestamp = int(calendar.timegm(aggregate_date.timetuple()))
    # End timestamp (the next day)
    end_date = aggregate_date + datetime.timedelta(days=1)
    end_timestamp = int(calendar.timegm(end_date.timetuple()))

    # Load the dataframe from the top 50 pairs of May
    df_top50_pairs_dir_volume = pd.read_csv(
        config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"]
        + "/pool_list/top50_pairs_list_v3_"
        + token_list_label
        + ".csv"
    )
    df_top50_pairs_dir_volume = df_top50_pairs_dir_volume.drop(
        columns=[
            "Unnamed: 0",
            "pastTotalVolumeUSD",
            "pastValidDays",
            "avgDailyVolumeUSD",
        ]
    )

    # Do iteration to sum up all transaction (directional) for each pair
    for index, row in tqdm(
        df_top50_pairs_dir_volume.iterrows(), total=df_top50_pairs_dir_volume.shape[0]
    ):
        # Pool id for this batch
        batch_pair_id = row["id"]

        # Get the daily gross volume from subgraph API
        batch_pair_info = get_gross_volume(batch_pair_id, date_timestamp)

        # fix the bug of null data
        if len(batch_pair_info) == 0:
            batch_pair_info = [
                {
                    "txCount": "0",
                    "volumeToken0": "0",
                    "volumeToken1": "0",
                    "volumeUSD": "0",
                    "tvlUSD": "0",
                }
            ]
            print("WARNING: Notice the null data at index: ", index)

        # Store values for the daily aggregated data
        df_top50_pairs_dir_volume.loc[index, "dailyTxns"] = batch_pair_info[0][
            "txCount"
        ]
        df_top50_pairs_dir_volume.loc[index, "dailyGrossVolumeUSD"] = batch_pair_info[
            0
        ]["volumeUSD"]
        df_top50_pairs_dir_volume.loc[index, "dailySwapVolumeToken0"] = batch_pair_info[
            0
        ]["volumeToken0"]
        df_top50_pairs_dir_volume.loc[index, "dailySwapVolumeToken1"] = batch_pair_info[
            0
        ]["volumeToken1"]
        df_top50_pairs_dir_volume.loc[index, "tvlUSD"] = batch_pair_info[0]["tvlUSD"]

        # Get the daily count for the mints transactions
        mints_count = count_daily_mints(batch_pair_id, date_timestamp, end_timestamp)
        # Store the values to the dataframe for this pair
        df_top50_pairs_dir_volume.loc[index, "mintsCount"] = mints_count

        # Get the daily count for the burns transactions
        burns_count = count_daily_burns(batch_pair_id, date_timestamp, end_timestamp)
        # Store the values to the dataframe for this pair
        df_top50_pairs_dir_volume.loc[index, "burnsCount"] = burns_count

        # Compute the daily directional volume of swaps
        (
            swaps_count,
            tx_0to1_count,
            volume_0to1,
            tx_1to0_count,
            volume_1to0,
        ) = compute_daily_directional_volume(
            batch_pair_id, date_timestamp, end_timestamp
        )
        # Store the values to the dataframe for this pair
        df_top50_pairs_dir_volume.loc[index, "swapsCount"] = swaps_count
        df_top50_pairs_dir_volume.loc[index, "token0To1Txs"] = tx_0to1_count
        df_top50_pairs_dir_volume.loc[index, "token0To1VolumeUSD"] = volume_0to1
        df_top50_pairs_dir_volume.loc[index, "token1To0Txs"] = tx_1to0_count
        df_top50_pairs_dir_volume.loc[index, "token1To0VolumeUSD"] = volume_1to0
        df_top50_pairs_dir_volume.loc[index, "GrossVolumeUSD"] = (
            volume_0to1 + volume_1to0
        )
    # End of the for loop

    # Delete the data of directly fected by daily aggregated API because the error is small
    df_top50_pairs_dir_volume = df_top50_pairs_dir_volume.drop(
        columns=["dailyGrossVolumeUSD"]
    )

    # Data file contains the defined date for the aggregation
    file_date = aggregate_date.date().strftime("%Y%m%d")

    # Define the file name
    file_name = path.join(
        config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"],
        "directional_volume/top50_directional_volume_v3_" + file_date + ".csv",
    )
    # Write dataframe to csv
    df_top50_pairs_dir_volume.to_csv(file_name)
