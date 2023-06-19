"""
Function to fetch the primary token information from the coingecko.
"""

import time

import warnings
from glob import glob

import pandas as pd
from pycoingecko import CoinGeckoAPI
from tqdm import tqdm

from environ.fetch.fetch_utils.subgraph_query import run_query_var
from environ.constants import (
    UNISWAP_V2_DATA_PATH,
    UNISWAP_V3_DATA_PATH,
    GLOBAL_DATA_PATH,
    HTTP_V2,
    HTTP_V3,
    UNDERLYING_QUERY_V2,
    UNDERLYING_QUERY_V3,
)

# ignore the warning
warnings.filterwarnings("ignore")

# initialize the config
cg = CoinGeckoAPI()

# uniswap version info mapping
UNISWAP_VERSION_MAPPING = {
    "data_path": {
        "v2": UNISWAP_V2_DATA_PATH,
        "v3": UNISWAP_V3_DATA_PATH,
    },
    "http": {
        "v2": HTTP_V2,
        "v3": HTTP_V3,
    },
    "underlying_query": {
        "v2": UNDERLYING_QUERY_V2,
        "v3": UNDERLYING_QUERY_V3,
    },
}


def _get_primary_token_pair_set(uni_version: str) -> set:
    """
    Get the primary token pair set
    """

    # get all the csv files
    path_mapping = {
        "v2": UNISWAP_V2_DATA_PATH,
        "v3": UNISWAP_V3_DATA_PATH,
    }
    path = rf"{path_mapping[uni_version]}/pool_list/"
    all_files = glob(path + "/*.csv")

    # create a set to store the primary token pair
    primary_token_pair_set = set()
    for filename in all_files:
        # load in the csv file
        df_pool = pd.read_csv(filename)

        # add multiple pair address to the set
        match uni_version:
            case "v2":
                primary_token_pair_set.update(
                    df_pool["pairAddress"]
                    .apply(lambda pair_address: pair_address.lower())
                    .values
                )
            case "v3":
                primary_token_pair_set.update(
                    df_pool["id"]
                    .apply(lambda pool_address: pool_address.lower())
                    .values
                )

    return primary_token_pair_set


def _get_underlying_token(pair_address: str, uni_version: str) -> pd.DataFrame:
    """
    Function to get the underlying token information from the graph.
    """
    while True:
        try:
            df_underlying_token = pd.DataFrame()

            # query the graph
            underlying_token_json = run_query_var(
                UNISWAP_VERSION_MAPPING["http"][uni_version],
                UNISWAP_VERSION_MAPPING["underlying_query"][uni_version],
                {"pair_address": pair_address},
            )

            # get the underlying token information
            for underlying_token in underlying_token_json["data"]["pair"].values():
                # append the underlying token to the dataframe
                df_underlying_token = pd.concat(
                    [
                        df_underlying_token,
                        pd.DataFrame.from_dict(
                            {
                                "id": underlying_token["id"],
                                "name": underlying_token["name"],
                                "symbol": underlying_token["symbol"],
                            }
                        ),
                    ],
                    axis=1,
                )
            # break the loop
            break
        except:
            time.sleep(10)

    return df_underlying_token


def get_primary_token() -> None:
    """
    Get the primary token information from the coingecko.
    """

    # token pair set mapping
    token_pair_set_mapping = {
        "v2": _get_primary_token_pair_set(uni_version="v2"),
        "v3": _get_primary_token_pair_set(uni_version="v3"),
    }

    # create a dataframe to store the primary token information
    df_primary_token = pd.DataFrame()

    # get the primary token information
    for _, primary_token_pair_set_v2 in token_pair_set_mapping.items():
        for pair_address in tqdm(primary_token_pair_set_v2):
            # get the underlying token information
            df_underlying_token = _get_underlying_token(pair_address, uni_version="v2")

            for _, value in df_underlying_token.items():
                df_primary_token = pd.concat(
                    [
                        df_primary_token,
                        pd.DataFrame.from_dict(
                            {
                                "id": value["id"],
                                "name": value["name"],
                                "symbol": value["symbol"],
                            }
                        ),
                    ],
                    axis=1,
                )

    # drop the duplicate token by symbol
    df_primary_token = df_primary_token.drop_duplicates(subset=["symbol"])

    # save the dateframe to data/data_global/primary_token
    df_primary_token.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token.csv",
        index=False,
        encoding="utf-8",
    )


def _coingecko_contract(token_address: str) -> str:
    """
    Function to get the token info from contract via coingecko.
    """

    # get the token info from contract
    token_info_json = cg.get_coin_info_from_contract_address_by_id(
        id="ethereum", contract_address=token_address
    )

    token_id = token_info_json["id"]

    return token_id


def manually_check() -> None:
    """
    Function to manually check the token data from the coingecko.
    """

    # load in the primary token price information
    df_primary_token_price = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_price_2.csv"
    )

    # get the list of keys excluding the timestamp
    key_list = list(df_primary_token_price.keys())[1:]

    # load in the primary token information
    df_primary_token = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token.csv"
    )

    # drop nan in column id and symbol
    df_primary_token = df_primary_token.dropna(subset=["id", "symbol"])

    # get the list of primary token symbol
    primary_token_symbol_list = df_primary_token["symbol"].values

    # get the symbol in the primary token price dataframe but not in the key list
    symbol_not_in_key_list = [
        symbol for symbol in primary_token_symbol_list if symbol not in key_list
    ]

    # load in the token data in data/data_uniswap_v2/tvl/csv
    for token_symbol in symbol_not_in_key_list:
        try:
            df_token_data = pd.read_csv(
                f"{UNISWAP_V2_DATA_PATH}/tvl/csv/{token_symbol}.csv"
            )
        except:
            df_token_data = pd.read_csv(
                f"{UNISWAP_V3_DATA_PATH}/tvl/csv/{token_symbol}.csv"
            )

        # get the price of the token
        df_token_data = df_token_data[["date", "priceUSD"]]

        # rename the column name
        df_token_data = df_token_data.rename(
            columns={"priceUSD": token_symbol, "date": "Date"}
        )

        # merge the dataframe
        df_primary_token_price = pd.merge(
            df_primary_token_price, df_token_data, on="Date", how="left"
        )
    # convert the timestamp to datetime
    df_primary_token_price["Date"] = pd.to_datetime(df_primary_token_price["Date"])

    # sort the dataframe by time
    df_primary_token_price = df_primary_token_price.sort_values(
        by="Date", ascending=True
    )

    # save the token price to data/data_global/primary_token/primary_token_price_2.csv
    df_primary_token_price.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_price_2.csv",
        encoding="utf-8",
    )


def csv_formatting() -> None:
    """
    Function to convert the new csv format to the old csv format.
    """

    for file_type in ["primary_token_price_2", "primary_token_marketcap_2"]:
        # load in the primary token price information
        df_primary = pd.read_csv(rf"{GLOBAL_DATA_PATH}/primary_token/{file_type}.csv")

        # rename the column time to Date
        df_primary = df_primary.rename(columns={"time": "Date"})

        # save the file
        df_primary.to_csv(
            rf"{GLOBAL_DATA_PATH}/primary_token/{file_type}.csv",
            encoding="utf-8",
        )


def get_primary_token_price() -> None:
    """
    Function to get the primary token price from the coingecko.
    """

    # load in the primary token information
    df_primary_token = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token.csv"
    )

    # drop nan in column id and symbol
    df_primary_token = df_primary_token.dropna(subset=["id", "symbol"])

    # dataframe to store the token price
    df_token_price = pd.DataFrame()

    # dataframe to store the market cap
    df_market_cap = pd.DataFrame()

    # get the token price using contract (id) from coingecko
    for _, row in tqdm(df_primary_token.iterrows(), total=df_primary_token.shape[0]):
        try:
            time.sleep(6)
            # get the token id in coingecko
            token_id = _coingecko_contract(row["id"])

            # load in the csv in data/data_global/coingecko/token_data
            df_token_data = pd.read_csv(
                rf"{GLOBAL_DATA_PATH}/coingecko/token_data/{token_id}.csv"
            )

            # only keep the time and prices column
            df_token_price_data = df_token_data[["time", "prices"]].copy()

            # rename the column prices to token symbol
            df_token_price_data.rename(
                columns={"prices": row["symbol"], "time": "Date"}, inplace=True
            )

            # sort the dataframe by time
            df_token_price_data = df_token_price_data.sort_values(
                by="Date", ascending=True
            )

            # if this is the first time to get the token price
            if df_token_price.empty:
                df_token_price = df_token_price_data
            else:
                df_token_price = df_token_price.merge(
                    df_token_price_data, how="outer", on="Date"
                )

            # only keep the time and market_caps column
            df_market_cap_data = df_token_data[["Date", "market_caps"]].copy()

            # rename the column market_caps to token symbol
            df_market_cap_data.rename(
                columns={"market_caps": row["symbol"]}, inplace=True
            )

            # sort the dataframe by time
            df_market_cap_data = df_market_cap_data.sort_values(
                by="Date", ascending=True
            )

            # if this is the first time to get the token price
            if df_market_cap.empty:
                df_market_cap = df_market_cap_data
            else:
                df_market_cap = df_market_cap.merge(
                    df_market_cap_data, how="outer", on="Date"
                )

        except:
            continue

    # save the token price to data/data_global/primary_token/primary_token_price_2.csv
    df_token_price.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_price_2.csv",
        index=False,
        encoding="utf-8",
    )

    # save the market cap to data/data_global/primary_token/primary_token_marketcap_2.csv
    df_market_cap.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_marketcap_2.csv",
        index=False,
        encoding="utf-8",
    )


if __name__ == "__main__":
    # get_primary_token()
    # print(_coingecko_contract("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"))
    # get_primary_token_price()
    # manually_check()
    csv_formatting()
