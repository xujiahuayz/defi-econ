"""
Functions to get the historical price, market capitalization, and volume data from CoinGecko API
"""

import pandas as pd
import time
from tqdm import tqdm
from pycoingecko import CoinGeckoAPI
from environ.utils.config_parser import Config

# Initialize config
config = Config()

# Initialize data path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]

# Initialize the start date and end date
START_DATE = config["dev"]["config"]["coingecko"]["START_DATE"]
END_DATE = config["dev"]["config"]["coingecko"]["END_DATE"]

# Initialize CoinGecko API
cg = CoinGeckoAPI()


def _load_in_token_list() -> pd.DataFrame:
    """
    Function to load in the
    """

    # read in the xlsx file
    token_list = pd.read_excel(
        rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
    )

    # reset the index
    token_list = token_list.reset_index(drop=True)

    # check if there is no column "attempt", create one:
    if "attempt" not in token_list.columns:
        token_list["attempt"] = 0
        # save the dataframe to the xlsx file
        token_list.to_excel(
            rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
            index=False,
        )

    return token_list


def _to_unix_time(datetime_str: str) -> int:
    """
    Function to convert the datetime to unix time
    """

    return int(pd.to_datetime(datetime_str).timestamp())


def _to_timestamp(unix_time: int) -> pd.Timestamp:
    """
    Function to convert the unix time to timestamp
    """

    return pd.to_datetime(unix_time, unit="ms", origin="unix")


def _get_token_data(token: str, start_date: int, end_date: int) -> pd.DataFrame:
    """
    Function to get the token data from CoinGecko API
    """

    # get raw token data of a specific token
    token_data = cg.get_coin_market_chart_range_by_id(
        id=token,
        vs_currency="usd",
        from_timestamp=start_date,
        to_timestamp=end_date,
    )

    # create a list to store the data
    token_data_dfs = []

    # unwrap the data and save it to a pd.DataFrame
    for var_name in token_data.keys():
        token_data_df = pd.DataFrame(token_data[var_name], columns=["time", var_name])
        token_data_df["time"] = token_data_df["time"].apply(_to_timestamp)
        token_data_df.set_index("time", inplace=True)
        token_data_dfs.append(token_data_df)

    token_data_dfs = pd.concat(token_data_dfs, axis=1)
    token_data_dfs.reset_index(inplace=True)

    return token_data_dfs


def fetch_coingecko() -> None:
    """
    Function to fetch the historical price, market
    capitalization, and volume data from CoinGecko API.
    """

    # load in the token list
    token_list = _load_in_token_list()

    for index in tqdm(token_list[token_list["attempt"] >= 0].index):

        # Free API has a rate limit of 10-30 calls/minute
        time.sleep(6)
        try:
            # get the token id
            token_id = token_list.loc[index, "Id"]

            # get the token data
            token_data = _get_token_data(
                token_id, _to_unix_time(START_DATE), _to_unix_time(END_DATE)
            )
            # save the token data to the csv file
            token_data.to_csv(
                rf"{GLOBAL_DATA_PATH}/coingecko/token_data/{token_id}.csv",
                index=False,
            )
            # set the attempt to -1
            token_list.loc[index, "attempt"] = -1
            # save the dataframe to the xlsx file
            token_list.to_excel(
                rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
                index=False,
            )

        except Exception as e:
            # attempt add one
            token_list.loc[index, "attempt"] += 1
            # save the dataframe to the xlsx file
            token_list.to_excel(
                rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
                index=False,
            )

    # save the dataframe to the xlsx file
    token_list.to_excel(
        rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
        index=False,
    )


if __name__ == "__main__":
    fetch_coingecko()
