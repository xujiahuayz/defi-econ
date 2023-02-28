"""
Function to fetch the primary token information from the coingecko.
"""

# Import the necessary library
import warnings
import time
import pandas as pd
from pycoingecko import CoinGeckoAPI
from glob import glob
from tqdm import tqdm
from environ.utils.config_parser import Config
from environ.fetch.fetch_utils.subgraph_query import run_query_var

# ignore the warning
warnings.filterwarnings("ignore")

# initialize the config
config = Config()
UNISWAP_V2_DATA_PATH = config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"]
UNISWAP_V3_DATA_PATH = config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"]
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
HTTP_V2 = config["dev"]["config"]["subgraph"]["HTTP_V2"]
HTTP_V3 = config["dev"]["config"]["subgraph"]["HTTP_V3"]
cg = CoinGeckoAPI()

# query the token info in a token pair
underlying_query_v2 = """
query($pair_address: String!)
{
  pair(id: $pair_address) {
    token0 {
      id
      name
      symbol
    }
    token1 {
      id
      name
      symbol
    }
  }
}
"""

underlying_query_v3 = """
query($pair_address: String!)  
{
  pool(id: $pair_address) {
    token0 {
      id
      name
      symbol
    }
    token1 {
      id
      name
      symbol
    }
  }
}
"""


def _get_primary_token_pair_set(uni_version: str) -> set:
    """
    Get the primary token pair set
    """

    if uni_version == "v2":
        # Get the primary token pair set of Uniswap V2
        # load in all csv file in data/data_uniswap_v2/pool_list
        path = rf"{UNISWAP_V2_DATA_PATH}/pool_list/"
        all_files = glob(path + "/*.csv")

    if uni_version == "v3":
        # Get the primary token pair set of Uniswap V3
        # load in all csv file in data/data_uniswap_v3/pool_list
        path = rf"{UNISWAP_V3_DATA_PATH}/pool_list/"
        all_files = glob(path + "/*.csv")

    # create a set to store the primary token pair
    primary_token_pair_set = set()
    for filename in all_files:

        # load in the csv file
        df_pool = pd.read_csv(filename)

        # add multiple pair address to the set
        if uni_version == "v2":
            primary_token_pair_set.update(
                df_pool["pairAddress"]
                .apply(lambda pair_address: pair_address.lower())
                .values
            )
        if uni_version == "v3":
            primary_token_pair_set.update(
                df_pool["id"].apply(lambda pool_address: pool_address.lower()).values
            )

    return primary_token_pair_set


def _get_underlying_token(pair_address: str, uni_version: str) -> pd.DataFrame:
    """
    Function to get the underlying token information from the graph.
    """
    while True:
        try:
            df_underlying_token = pd.DataFrame()

            if uni_version == "v2":
                # set the params
                underlying_params_v2 = {"pair_address": pair_address}

                # query the graph
                underlying_token_json = run_query_var(
                    HTTP_V2, underlying_query_v2, underlying_params_v2
                )

                # get the underlying token information
                for underlying_token in underlying_token_json["data"]["pair"].values():
                    # append the underlying token to the dataframe
                    df_underlying_token = df_underlying_token.append(
                        {
                            "id": underlying_token["id"],
                            "name": underlying_token["name"],
                            "symbol": underlying_token["symbol"],
                        },
                        ignore_index=True,
                    )
                # break the loop
                break

            if uni_version == "v3":
                # set the params
                underlying_params_v3 = {"pair_address": pair_address}

                # query the graph
                underlying_token_json = run_query_var(
                    HTTP_V3, underlying_query_v3, underlying_params_v3
                )
                # get the underlying token information
                for underlying_token in underlying_token_json["data"]["pool"].values():
                    # append the underlying token to the dataframe
                    df_underlying_token = df_underlying_token.append(
                        {
                            "id": underlying_token["id"],
                            "name": underlying_token["name"],
                            "symbol": underlying_token["symbol"],
                        },
                        ignore_index=True,
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

    # Get the primary token pair set of Uniswap V2
    primary_token_pair_set_v2 = _get_primary_token_pair_set(uni_version="v2")

    # Get the primary token pair set of Uniswap V3
    primary_token_pair_set_v3 = _get_primary_token_pair_set(uni_version="v3")

    # create a dataframe to store the primary token information
    df_primary_token = pd.DataFrame()

    # get the primary token information
    for pair_address in tqdm(primary_token_pair_set_v2):
        # get the underlying token information
        df_underlying_token = _get_underlying_token(pair_address, uni_version="v2")

        # append two underlying token to the dataframe
        df_primary_token = df_primary_token.append(
            {
                "id": df_underlying_token["id"].values[0],
                "name": df_underlying_token["name"].values[0],
                "symbol": df_underlying_token["symbol"].values[0],
            },
            ignore_index=True,
        )
        df_primary_token = df_primary_token.append(
            {
                "id": df_underlying_token["id"].values[1],
                "name": df_underlying_token["name"].values[1],
                "symbol": df_underlying_token["symbol"].values[1],
            },
            ignore_index=True,
        )

    # get the primary token information
    for pair_address in tqdm(primary_token_pair_set_v3):
        # get the underlying token information
        df_underlying_token = _get_underlying_token(pair_address, uni_version="v3")

        # append two underlying token to the dataframe
        df_primary_token = df_primary_token.append(
            {
                "id": df_underlying_token["id"].values[0],
                "name": df_underlying_token["name"].values[0],
                "symbol": df_underlying_token["symbol"].values[0],
            },
            ignore_index=True,
        )
        df_primary_token = df_primary_token.append(
            {
                "id": df_underlying_token["id"].values[1],
                "name": df_underlying_token["name"].values[1],
                "symbol": df_underlying_token["symbol"].values[1],
            },
            ignore_index=True,
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

    # # correct the timestamp of uma token
    # # load in the csv in data/data_global/coingecko/token_data/uma.csv
    # df_token_data = pd.read_csv(rf"{GLOBAL_DATA_PATH}/coingecko/token_data/uma.csv")

    # # convert the timestamp to datetime
    # df_token_data["time"] = pd.to_datetime(df_token_data["time"])

    # # convert the timestamp to the form of "YYYY-MM-DD"
    # df_token_data["time"] = df_token_data["time"].dt.strftime("%Y-%m-%d")

    # # save the dataframe to data/data_global/coingecko/token_data/uma.csv
    # df_token_data.to_csv(
    #     rf"{GLOBAL_DATA_PATH}/coingecko/token_data/uma.csv",
    #     index=False,
    #     encoding="utf-8",
    # )

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

    # load in the primary token price information
    df_primary_token_price = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_price_2.csv"
    )

    # load in the primary token market cap information
    df_primary_token_mcap = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_marketcap_2.csv"
    )

    # rename the column time to Date
    df_primary_token_price = df_primary_token_price.rename(columns={"time": "Date"})

    # rename the column time to Date
    df_primary_token_mcap = df_primary_token_mcap.rename(columns={"time": "Date"})

    # save the token price to data/data_global/primary_token/primary_token_price_2.csv
    df_primary_token_price.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_price_2.csv",
        encoding="utf-8",
    )

    # save the token price to data/data_global/primary_token/primary_token_price_2.csv
    df_primary_token_mcap.to_csv(
        rf"{GLOBAL_DATA_PATH}/primary_token/primary_token_marketcap_2.csv",
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
