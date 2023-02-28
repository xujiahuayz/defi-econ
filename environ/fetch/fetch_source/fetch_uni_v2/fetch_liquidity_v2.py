"""
Function to fetch the TVL data from the Uniswap V2 subgraph
"""

# Import the necessary library
import os
import warnings
import time
import pandas as pd
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from glob import glob
from tqdm import tqdm
from environ.utils.config_parser import Config
from environ.fetch.fetch_utils.subgraph_query import run_query_var, run_query

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

# query the tvl of a token
tvl_query_v2 = """
query($token_address: String!)
{
  tokenDayDatas(
    first: 1000
    orderBy: date
    orderDirection: asc
    where: {token_: {id: $token_address}}
  ) {
    date
    priceUSD
    totalLiquidityETH
    totalLiquidityToken
    totalLiquidityUSD
  }
}
"""

# query the total liquiy of uniswap v2
total_liquidity_query_v2 = """
query MyQuery {
  uniswapDayDatas(
    orderBy: date
    orderDirection: asc
    where: {date_gte: 1590969600, date_lte: 1675123200}
    first: 1000
  ) {
    date
    totalLiquidityUSD
  }
}
"""


def _get_tvl_v2() -> None:
    """
    Function to get the TVL data from the Uniswap V2 subgraph
    """

    # request the total liquidity data
    total_liquidity_json = run_query(HTTP_V2, total_liquidity_query_v2)

    # create a dataframe to store the total liquidity data
    df_total_liquidity = pd.DataFrame()

    # get the total liquidity data
    for total_liquidity in total_liquidity_json["data"]["uniswapDayDatas"]:
        # append the total liquidity data to the dataframe
        df_total_liquidity = df_total_liquidity.append(
            {
                "date": total_liquidity["date"],
                "totalLiquidityUSD": total_liquidity["totalLiquidityUSD"],
            },
            ignore_index=True,
        )

    # convert the unix to datetime
    df_total_liquidity["date"] = pd.to_datetime(
        df_total_liquidity["date"], unit="s", origin="unix"
    )

    # save the total liquidity data
    df_total_liquidity.to_csv(
        rf"{UNISWAP_V2_DATA_PATH}/tvl/total/total_liquidity.csv", index=False
    )

    # plot the totalLiquidityUSD
    plt.figure(figsize=(20, 10))
    plt.plot(
        df_total_liquidity["date"], df_total_liquidity["totalLiquidityUSD"].map(float)
    )
    plt.title("Total Liquidity USD")
    plt.xlabel("Date")
    plt.ylabel("Total Liquidity USD")
    plt.show()


def _get_primary_token_pair_set() -> set:
    """
    Get the primary token pair set
    """

    # Get the primary token pair set of Uniswap V2
    # load in all csv file in data/data_uniswap_v2/pool_list
    path = rf"{UNISWAP_V2_DATA_PATH}/pool_list/"
    all_files = glob(path + "/*.csv")

    # create a set to store the primary token pair
    primary_token_pair_set = set()
    for filename in all_files:

        # load in the csv file
        df_pool = pd.read_csv(filename)

        # add multiple pair address to the set
        primary_token_pair_set.update(
            df_pool["pairAddress"]
            .apply(lambda pair_address: pair_address.lower())
            .values
        )
    return primary_token_pair_set


def _get_underlying_token(pair_address: str) -> pd.DataFrame:
    """
    Function to get the underlying token information from the graph.
    """
    while True:
        try:
            df_underlying_token = pd.DataFrame()

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
        except:
            time.sleep(10)

    return df_underlying_token


def _get_primary_token() -> None:
    """
    Function to get the primary token
    """

    # Get the primary token pair set of Uniswap V2
    primary_token_pair_set_v2 = _get_primary_token_pair_set()

    # create a dataframe to store the primary token information
    df_primary_token = pd.DataFrame()

    # get the primary token information
    for pair_address in tqdm(primary_token_pair_set_v2):
        # get the underlying token information
        df_underlying_token = _get_underlying_token(pair_address)

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

    # drop nan for the symbol
    df_primary_token = df_primary_token.dropna(subset=["symbol"])

    # save the dateframe to rf"{UNISWAP_V2_DATA_PATH}/tvl/list"
    df_primary_token.to_csv(
        rf"{UNISWAP_V2_DATA_PATH}/tvl/list/primary_token.csv", index=False
    )


def _get_token_tvl(token_address: str, token_name: str, token_symbol) -> None:
    """
    Function to get the token tvl
    """
    try:
        # set the params
        tvl_params_v2 = {"token_address": token_address}

        # query the graph
        tvl_json = run_query_var(HTTP_V2, tvl_query_v2, tvl_params_v2)

        # get the tvl information
        df_tvl = pd.DataFrame(tvl_json["data"]["tokenDayDatas"])

        # convert the date to datetime
        df_tvl["date"] = pd.to_datetime(df_tvl["date"], unit="s", origin="unix")

        # sort the dataframe by date
        df_tvl = df_tvl.sort_values(by="date", ascending=True)

        # add the token id, name ,and symbol
        df_tvl["token_id"] = token_address
        df_tvl["token_name"] = token_name
        df_tvl["token_symbol"] = token_symbol

        # save the dateframe to rf"{UNISWAP_V2_DATA_PATH}/tvl/csv"
        df_tvl.to_csv(
            rf"{UNISWAP_V2_DATA_PATH}/tvl/csv/{token_symbol}.csv", index=False
        )
    except:
        print("Error: ", token_symbol)


def fetch_liquidity_v2() -> None:
    """
    Function to fetch the liquidity data from the Uniswap V2 subgraph
    """

    # check if there is path of data/data_uniswap_v2/tvl exists
    if not os.path.exists(rf"{UNISWAP_V2_DATA_PATH}/tvl"):

        # create the path
        os.makedirs(rf"{UNISWAP_V2_DATA_PATH}/tvl")
        os.makedirs(rf"{UNISWAP_V2_DATA_PATH}/tvl/csv")
        os.makedirs(rf"{UNISWAP_V2_DATA_PATH}/tvl/list")

        # get the primary token information
        _get_primary_token()

    # load in the primary token information
    df_primary_token = pd.read_csv(
        rf"{UNISWAP_V2_DATA_PATH}/tvl/list/primary_token.csv"
    )

    # get the list of primary token address in {UNISWAP_V2_DATA_PATH}/tvl/csv
    primary_token_address_list = [
        filename.split(".")[0]
        for filename in os.listdir(rf"{UNISWAP_V2_DATA_PATH}/tvl/csv")
    ]

    # exclude the primary token address that already exists in {UNISWAP_V2_DATA_PATH}/tvl/csv
    df_primary_token = df_primary_token[
        ~df_primary_token["symbol"].isin(primary_token_address_list)
    ]

    # get the token tvl
    for token_address, token_name, token_symbol in tqdm(
        df_primary_token.values.tolist()
    ):
        _get_token_tvl(token_address, token_name, token_symbol)


if __name__ == "__main__":
    # fetch_liquidity_v2()
    # _get_token_tvl("0xc770eefad204b5180df6a14ee197d99d808ee52d")
    _get_tvl_v2()
