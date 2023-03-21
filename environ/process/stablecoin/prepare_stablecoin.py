"""
Prepare stablecoin-related data for the environment.
"""

import warnings
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from environ.utils.config_parser import Config


# ignore warnings
warnings.filterwarnings("ignore")

# Initialize config
config = Config()

GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
TOKEN_LIB_V2_TOKEN = config["dev"]["config"]["token_library"]["v2"]["token"]
TOKEN_LIB_V2_STABLE = config["dev"]["config"]["token_library"]["v2"]["stable"]
TOKEN_LIB_V3_TOKEN = config["dev"]["config"]["token_library"]["v3"]["token"]
TOKEN_LIB_V3_STABLE = config["dev"]["config"]["token_library"]["v3"]["stable"]
FIGURE_PATH = config["dev"]["config"]["result"]["FIGURE_PATH"]


def prepare_stable_share() -> None:
    """
    Prepare the stablecoin share.
    """

    # check whether there is data/data_global/stablecoin
    # if not, create the folder
    if not os.path.exists(rf"{GLOBAL_DATA_PATH}/stablecoin"):
        os.makedirs(rf"{GLOBAL_DATA_PATH}/stablecoin")

    # load in the token library for v2 and v3
    token_lib_v2 = pd.DataFrame(
        {"Token": TOKEN_LIB_V2_TOKEN, "Stable": TOKEN_LIB_V2_STABLE}
    )
    token_lib_v3 = pd.DataFrame(
        {"Token": TOKEN_LIB_V3_TOKEN, "Stable": TOKEN_LIB_V3_STABLE}
    )

    # merge the token library for v2 and v3
    token_lib = pd.concat([token_lib_v2, token_lib_v3], ignore_index=True)

    # drop the duplicate token
    token_lib = token_lib.drop_duplicates(subset=["Token"])

    # load in the dataframe in data/data_global/token_market/primary_token_marketcap_2.csv
    token_marketcap = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_marketcap_2.csv"
    )

    # get the list of stablecoin
    stablecoin_list = token_lib[token_lib["Stable"] == 1]["Token"].tolist()

    # isolate the columns of stablecoin isin the stablecoin list
    stablecoin_list = [i for i in token_marketcap.columns if i in stablecoin_list]

    # isolate the columns of stablecoin isin the stablecoin list
    stablecoin_marketcap = token_marketcap[stablecoin_list + ["Date"]]

    # interpolate the missing value for USDT
    stablecoin_marketcap["USDT"] = stablecoin_marketcap["USDT"].interpolate()

    # create a new column for total stablecoin marketcap on that date
    stablecoin_marketcap["Total Stablecoin Marketcap"] = stablecoin_marketcap[
        stablecoin_list
    ].sum(axis=1)

    # replace the origin stablecoin marketcap with the stablecoin share
    for i in stablecoin_list:
        stablecoin_marketcap[i] = (
            stablecoin_marketcap[i] / stablecoin_marketcap["Total Stablecoin Marketcap"]
        )

    # drop the total stablecoin marketcap column
    stablecoin_marketcap = stablecoin_marketcap.drop(
        columns=["Total Stablecoin Marketcap"]
    )

    # convert the date column to datetime
    stablecoin_marketcap["Date"] = pd.to_datetime(stablecoin_marketcap["Date"])

    # specify the color for each token
    color_dict = {
        "USDC": "red",
        "USDT": "purple",
        "DAI": "brown",
        "FEI": "pink",
        "BUSD": "blue",
    }

    # other token will be black
    for i in stablecoin_list:
        if i not in color_dict.keys():
            color_dict[i] = "grey"

    # plot the stablecoin share
    stablecoin_marketcap.plot(
        x="Date",
        y=stablecoin_list,
        kind="line",
        figsize=(12, 8),
        color=color_dict,
    )

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        borderaxespad=0.0,
        prop={"size": 40},
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    # legend on the right side
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    # tight layout
    plt.tight_layout()

    # save the figure to FIGURE_PATH
    plt.savefig(rf"{FIGURE_PATH}/stablecoin_share.pdf")

    plt.show()

    # convert the dataframe to panel
    stablecoin_marketcap = stablecoin_marketcap.set_index("Date")

    # unstack the dataframe
    stablecoin_marketcap = stablecoin_marketcap.unstack().reset_index()

    # rename the columns
    stablecoin_marketcap.columns = ["Token", "Date", "stableshare"]

    # # Check point
    # # plot the stablecoin share for USDT
    # stablecoin_marketcap[stablecoin_marketcap["Token"] == "USDC"].plot(
    #     x="Date", y="stableshare", kind="line", figsize=(12, 8)
    # )

    # # place the legend outside the plot without border
    # plt.legend(
    #     bbox_to_anchor=(1.01, 1),
    #     loc="upper left",
    #     borderaxespad=0.0,
    #     prop={"size": 40},
    # )

    # # enlarge the font of ticker
    # plt.xticks(fontsize=40)
    # plt.yticks(fontsize=40)

    # # legend on the right side
    # plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    # # tight layout
    # plt.tight_layout()

    # plt.show()

    # save the stablecoin share to data/data_global/stablecoin/stablecoin_share.csv
    stablecoin_marketcap.to_csv(
        rf"{GLOBAL_DATA_PATH}/stablecoin/stablecoin_share.csv", index=False
    )


def prepare_stable_depeg() -> None:
    """
    Function to prepare the stablecoin depeg data.
    """

    # load in the token library for v2 and v3
    token_lib_v2 = pd.DataFrame(
        {"Token": TOKEN_LIB_V2_TOKEN, "Stable": TOKEN_LIB_V2_STABLE}
    )
    token_lib_v3 = pd.DataFrame(
        {"Token": TOKEN_LIB_V3_TOKEN, "Stable": TOKEN_LIB_V3_STABLE}
    )

    # merge the token library for v2 and v3
    token_lib = pd.concat([token_lib_v2, token_lib_v3], ignore_index=True)

    # drop the duplicate token
    token_lib = token_lib.drop_duplicates(subset=["Token"])

    # load in the dataframe in data/data_global/token_market/primary_token_marketcap_2.csv
    token_marketcap = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_marketcap_2.csv"
    )

    # get the list of stablecoin
    stablecoin_list = token_lib[token_lib["Stable"] == 1]["Token"].tolist()

    # load in the data/data_global/token_market/primary_token_price_2.csv
    token_price = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv"
    )

    # isolate the columns of stablecoin isin the stablecoin list
    stablecoin_list = [i for i in token_price.columns if i in stablecoin_list]

    # isolate the columns of stablecoin isin the stablecoin list
    stablecoin_price = token_price[stablecoin_list + ["Date"]]

    # convert the date column to datetime
    stablecoin_price["Date"] = pd.to_datetime(stablecoin_price["Date"])

    # specify the color for each token
    color_dict = {
        "USDC": "red",
        "USDT": "purple",
        "DAI": "brown",
        "FEI": "pink",
        "BUSD": "blue",
    }

    # other token will be grey
    for i in stablecoin_list:
        if i not in color_dict.keys():
            color_dict[i] = "grey"

    # give the grey some transparency
    for i in color_dict.keys():
        if color_dict[i] == "grey":
            color_dict[i] = (0.5, 0.5, 0.5, 0.5)

    # plot the price of stablecoin
    stablecoin_price.plot(
        x="Date",
        y=stablecoin_list,
        kind="line",
        figsize=(12, 8),
        color=color_dict,
    )

    # fix the y-axis to be between 0 and 3
    plt.ylim(0.8, 1.2)

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        borderaxespad=0.0,
        prop={"size": 40},
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # legend on the right side
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    # tight layout
    plt.tight_layout()

    # save the figure to FIGURE_PATH
    plt.savefig(rf"{FIGURE_PATH}/stablecoin_price.pdf")

    plt.show()


def prepare_marketcap_share() -> None:
    """
    Function to prepare the marketcap share data.
    """

    # load in the dataframe in data/data_global/token_market/primary_token_marketcap_2.csv
    token_marketcap = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_marketcap_2.csv"
    )

    # interpolate the missing value for USDT
    token_marketcap["USDT"] = token_marketcap["USDT"].interpolate()

    # drop the WETH column
    token_marketcap = token_marketcap.drop(columns=["WETH"])

    # load in the ethereum.csv from data/data_global/coingecko/token_data
    ethereum = pd.read_csv(rf"{GLOBAL_DATA_PATH}/coingecko/token_data/ethereum.csv")

    # only keep the time and market_caps columns
    ethereum = ethereum[["time", "market_caps"]]

    # rename the columns
    ethereum.columns = ["Date", "WETH"]

    # merge the ethereum dataframe with the token_marketcap dataframe
    token_marketcap = pd.merge(token_marketcap, ethereum, on="Date", how="left")

    # calculate the total marketcap
    token_marketcap["Total Marketcap"] = token_marketcap.sum(axis=1)

    # calculate the marketcap share except for the date column
    for i in token_marketcap.columns:
        if i != "Date":
            token_marketcap[i] = token_marketcap[i] / token_marketcap["Total Marketcap"]

    # drop the total marketcap column
    token_marketcap = token_marketcap.drop(columns=["Total Marketcap"])

    # convert the date column to datetime
    token_marketcap["Date"] = pd.to_datetime(token_marketcap["Date"])

    # specify the color for each token
    color_dict = {
        "WETH": "blue",
        "WBTC": "orange",
        "MATIC": "green",
        "USDC": "red",
        "USDT": "purple",
        "DAI": "brown",
        "FEI": "pink",
    }

    # keep only the token in the color_dict and the date column
    token_marketcap = token_marketcap[
        [i for i in token_marketcap.columns if i in color_dict.keys()] + ["Date"]
    ]

    # plot the marketcap share
    token_marketcap.plot(
        x="Date",
        y=[i for i in token_marketcap.columns if i not in ["Date"]],
        kind="line",
        figsize=(12, 8),
        color=color_dict,
    )

    # place the legend outside the plot without border
    plt.legend(
        [i for i in token_marketcap.columns if i not in color_dict.keys()],
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        borderaxespad=0.0,
        prop={"size": 40},
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # legend on the right side
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    # tight layout
    plt.tight_layout()

    # save the figure to FIGURE_PATH
    plt.savefig(rf"{FIGURE_PATH}/marketcap_share.pdf")

    plt.show()


def prepare_volatility() -> None:
    """
    Function to prepare the volatility data.
    """

    # load in the data/data_global/token_market/primary_token_price_2.csv
    token_price = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv"
    )

    # color dictionary
    color_dict = {
        "WETH": "blue",
        "WBTC": "orange",
        "MATIC": "green",
        "USDC": "red",
        "USDT": "purple",
        "DAI": "brown",
        "FEI": "pink",
    }

    # keep only the token in the color_dict and the date column
    token_price = token_price[
        [i for i in token_price.columns if i in color_dict.keys()] + ["Date"]
    ]

    # interpolate the missing value for USDT
    token_price["USDT"] = token_price["USDT"].interpolate()

    # convert the date column to datetime
    token_price["Date"] = pd.to_datetime(token_price["Date"])

    # sort the dataframe by date
    token_price = token_price.sort_values(by="Date")

    # calculate the log return for all the tokens
    token_price = token_price.set_index("Date").apply(np.log).diff()

    # calculate the 30-day rolling volatility for all the tokens
    token_price = token_price.rolling(30).std()

    # reset the index
    token_price = token_price.reset_index()

    # plot the volatility
    token_price.plot(
        x="Date",
        y=[i for i in token_price.columns if i not in ["Date"]],
        kind="line",
        figsize=(12, 8),
        color=color_dict,
    )

    # place the legend outside the plot without border
    plt.legend(
        [i for i in token_price.columns if i not in color_dict.keys()],
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        borderaxespad=0.0,
        prop={"size": 40},
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # legend on the right side
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    # tight layout
    plt.tight_layout()

    # save the figure to FIGURE_PATH
    plt.savefig(rf"{FIGURE_PATH}/volatility.pdf")

    plt.show()


if __name__ == "__main__":
    prepare_stable_share()
    # prepare_stable_depeg()
    # prepare_marketcap_share()
    # prepare_volatility()
