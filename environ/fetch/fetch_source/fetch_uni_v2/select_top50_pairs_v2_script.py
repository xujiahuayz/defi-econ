# -*- coding: utf-8 -*-
"""
Select Top 50 pairs by the daily average gross volume USD
"""

import datetime
import calendar
from os import path
import pandas as pd
import numpy as np
from tqdm import tqdm
import environ.fetch.fetch_utils.subgraph_query as subgraph
from environ.utils.config_parser import Config


def select_candidate_pairs(end_date: datetime.datetime) -> pd.DataFrame:
    """
    select top 500 pairs order by daily volume USD as candidate pairs
    """
    # Convert the end date to unix timestamp
    # Notice: time.mktime() will get the local time, calendar.timegm() will get the utc time
    end_timestamp = int(calendar.timegm(end_date.timetuple()))
    params_end_timestamp = {"end_date": end_timestamp}

    # Firstly, fetch the top 500 candidate pairs by the total volume USD on a single day
    # Query the daily aggregated volume USD on the end date
    top500_candidate_pairs_query = """
      query($end_date: Int!)
      {
        pairDayDatas(first: 500, orderBy: dailyVolumeUSD, orderDirection: desc,
          where: {
            date: $end_date
          }
        ) {
            pairAddress
            token0 {
              symbol
            }
            token1 {
              symbol
            }
            dailyVolumeUSD
          }
      }
    """
    top500_candidate_pairs = subgraph.run_query_var(
        subgraph.HTTP_V2, top500_candidate_pairs_query, params_end_timestamp
    )

    # Create a dataframe to store the candidate pairs info
    df_top500_pairs = pd.DataFrame.from_dict(
        top500_candidate_pairs["data"]["pairDayDatas"]
    )

    return df_top500_pairs


def get_avg_volume_candidate_pairs(
    df_top500_pairs: pd.DataFrame, start_date: datetime.datetime, period: int
) -> pd.DataFrame:
    """
    get the average daily volume by dividing the sum of each daily volume for the past horizon
    """
    # The previous date before the start date as the last timestamp gt
    end_date = start_date + datetime.timedelta(days=period)
    end_timestamp = int(calendar.timegm(end_date.timetuple()))
    last_date = start_date - datetime.timedelta(days=1)
    last_timestamp = int(calendar.timegm(last_date.timetuple()))

    # For each pair, sum up the daily aggregated volume
    for index, row in tqdm(df_top500_pairs.iterrows(), total=df_top500_pairs.shape[0]):
        candidate_pair = row["pairAddress"]
        params_candidate_pair = {
            "period": period,
            "candidate_pair": candidate_pair,
            "last_date_gt": last_timestamp,
        }

        # Query the historical daily aggregated volume for the past period
        candidate_daily_volume_query = """
          query($period: Int!, $candidate_pair: String!, $last_date_gt: Int!) 
          {
            pairDayDatas(first: $period, orderBy: date, orderDirection: asc,
              where: {
                pairAddress: $candidate_pair,
                date_gt: $last_date_gt
              })
              {
                date
                dailyVolumeToken0
                dailyVolumeToken1
                dailyVolumeUSD
              }
          }
        """
        candidate_daily_volume = subgraph.run_query_var(
            subgraph.HTTP_V2, candidate_daily_volume_query, params_candidate_pair
        )

        # Check whether the api returns data
        if list(candidate_daily_volume.keys()) == ["data"]:

            # The variable to control the divisor of the total volume
            df_top500_pairs.loc[index, "pastValidDays"] = len(
                candidate_daily_volume["data"]["pairDayDatas"]
            )

            # Sum up the daily volume
            past_total_volume_usd = 0
            for i, _ in enumerate(candidate_daily_volume["data"]["pairDayDatas"]):
                # Fix the bug for recent created pools
                if (
                    int(candidate_daily_volume["data"]["pairDayDatas"][i]["date"])
                    > end_timestamp
                ):
                    df_top500_pairs.loc[index, "pastValidDays"] = i
                else:
                    past_total_volume_usd = past_total_volume_usd + float(
                        candidate_daily_volume["data"]["pairDayDatas"][i][
                            "dailyVolumeUSD"
                        ]
                    )

            # Complete summing, store the total volume to dataframe
            df_top500_pairs.loc[index, "pastTotalVolumeUSD"] = past_total_volume_usd
            df_top500_pairs.loc[
                index, "avgDailyVolumeUSD"
            ] = past_total_volume_usd / len(
                candidate_daily_volume["data"]["pairDayDatas"]
            )

    return df_top500_pairs


def select_top50_pairs_v2(
    end_date: datetime.datetime, period: int, output_label: str
) -> None:
    """
    Select the top50 pools of v2 by given end date, past period, and output label
    (eg. MAY2022). Output to the separate data file.
    """
    # Initialize configuration
    config = Config()

    # Example of time period: 01/05/2022 -> 31/05/2022
    # 31 days in May
    start_date = end_date - datetime.timedelta(days=period - 1)

    # Filter condition of the new pool
    # Example: trace back 1 May to 31 May, but pool was created at 15 May, so only 16 valid days
    valid_threshold = 30

    # Select the top 500 candidate pairs
    df_top500_pairs = select_candidate_pairs(end_date)

    # Add a column for the valid days in the past period
    # Example: some pool was created at 17 May 2022
    # So that there was no volume between 1 May and 16 May
    df_top500_pairs["pastValidDays"] = 0
    # Add a column for the sum up of daily aggregated volume USD in the past N days
    df_top500_pairs["pastTotalVolumeUSD"] = np.zeros
    # Add a column for the average of the daily volume USD in the past N days
    df_top500_pairs["avgDailyVolumeUSD"] = np.zeros

    # Get the average daily volume by summing up daily aggregated data
    df_top500_pairs = get_avg_volume_candidate_pairs(
        df_top500_pairs, start_date, period
    )

    # Sort the dataframe by avgDailyVolumeUSD, here change to the new index as ranking
    df_top500_pairs = df_top500_pairs.sort_values(
        by="avgDailyVolumeUSD", ascending=False, ignore_index=True
    )

    # Set conditions to filter the new pool which does not have enough past valid days
    df_top50_avg_pairs = df_top500_pairs.loc[
        df_top500_pairs["pastValidDays"] >= valid_threshold
    ]

    # Select the top 50 pairs and reset index as ranking
    df_top50_avg_pairs = df_top50_avg_pairs[:50].reset_index()

    # Drop the outdated index
    df_top50_avg_pairs = df_top50_avg_pairs.drop(columns="index")

    # Define the file name
    file_name = path.join(
        config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
        "pool_list/top50_pairs_list_v2_" + output_label + ".csv",
    )

    # Write dataframe to csv
    df_top50_avg_pairs.to_csv(file_name)
