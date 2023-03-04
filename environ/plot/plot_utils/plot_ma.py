"""

University College London
Project : defi-econ
Topic   : plot_ma.py
Author  : Yichen Luo
Date    : 2022-01-05
Desc    : plot the 30-day moving averages of time-series data.

"""

import glob
import matplotlib.pyplot as plt
import pandas as pd
from environ.utils.config_parser import Config

# Initialize config
config = Config()

# Path constants
BETWEENNESS_DATA_PATH = config["dev"]["config"]["data"]["BETWEENNESS_DATA_PATH"]
NETWORK_DATA_PATH = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
COMPOUND_DATA_PATH = config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"]
COMPOUND_DATA_PATH = config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"]
FIGURE_PATH = config["dev"]["config"]["result"]["FIGURE_PATH"]

# specify the color for each token
COLOR_DICT = {
    "WETH": "blue",
    "WBTC": "orange",
    "MATIC": "green",
    "USDC": "red",
    "USDT": "purple",
    "DAI": "brown",
    "FEI": "pink",
}


def betweenness_prep(graph_type: str, source: str) -> tuple:
    """
    Function to prepare the data for the betweenness centrality graph
    """

    # combine all csv files in data/data_betweenness/betweenness
    # with the format of "betweenness_{source}_date.csv"
    # each csv file's title contains the date, and has columes:
    # Token, Betweenness, and has row number
    # the new combined dataframe has colume: Date, Token, Betweenness
    # get all csv files in data/data_betweenness/betweenness

    path = rf"{BETWEENNESS_DATA_PATH}/betweenness"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        if filename.split("_")[-2].split(".")[0] == source:
            df_betweenness = pd.read_csv(filename, index_col=None, header=0)
            date = filename.split("_")[-1].split(".")[0]
            df_betweenness["Date"] = date
            list_df.append(df_betweenness)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
    frame = frame[
        frame["node"].isin(
            config["dev"]["config"]["moving_average_plot"]["KEY_TOKEN_LIST"]
        )
    ]

    # plot the 30-day moving average of betweenness centrality of each token
    # the x-axis is date, the y-axis is betweenness centrality
    # the plot is saved in data/data_betweenness/betweenness/betweenness.png
    frame[graph_type] = frame[graph_type].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=["node", "Date"])

    # each day from 2020-08-01 to 2022-12-31, calculate the past
    # 30-day moving average of betweenness centrality of each token
    plot_df = (
        frame.groupby(["node"])[graph_type].rolling(window=30).mean().reset_index()
    )
    x_col_name = "Date"
    return plot_df, "node", x_col_name, graph_type, frame


def volume_tvl_prep(graph_type: str, source: str) -> tuple:
    """
    Function to plot the 30-day moving average graph of each token
    """

    # combine all csv files in data/data_network/merged/volume_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume
    # get all csv files in data/data_network/merged/volume_share
    path = rf"{NETWORK_DATA_PATH}/{source}/{graph_type}"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_vol_tvl = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_vol_tvl["Date"] = date
        list_df.append(df_vol_tvl)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    if graph_type == "tvl_share":
        token_col_name = "token"
        y_col_name = "total_tvl"
    else:
        token_col_name = "Token"
        y_col_name = "Volume"

    # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
    frame = frame[
        frame[token_col_name].isin(
            ["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"]
        )
    ]

    # plot the 30-day moving average of volume share of each token
    # the x-axis is date, the y-axis is volume share
    # the plot is saved in data/data_network/merged/volume_share/volume_share.png
    frame[y_col_name] = frame[y_col_name].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=[token_col_name, "Date"])

    # each day from 2020-08-01 to 2022-12-31, calculate the past
    # 30-day moving average of volume share of each token
    plot_df = (
        frame.groupby([token_col_name])[y_col_name]
        .rolling(window=30)
        .mean()
        .reset_index()
    )
    x_col_name = "Date"
    return plot_df, token_col_name, x_col_name, y_col_name, frame


def borrow_supply_prep(graph_type: str) -> tuple:
    """
    Function to preprocess the data for the borrow
    """

    # combine all csv files with "_processed" at the end of
    # the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"{COMPOUND_DATA_PATH}"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    list_df = []
    for filename in all_files:
        df_borrow_supply = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue
        if token == "ETH":
            df_borrow_supply["token"] = "WETH"
        else:
            df_borrow_supply["token"] = token

        list_df.append(df_borrow_supply)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # check whether the graph type is borrow or supply
    if graph_type == "borrow_share":

        # calculate the borrow share of each token each day
        frame["total_borrow_usd"] = frame["total_borrow_usd"].astype(float)
        frame["total_borrow"] = frame.groupby("block_timestamp")[
            "total_borrow_usd"
        ].transform("sum")
        frame["total_borrow_usd"] = frame["total_borrow_usd"] / frame["total_borrow"]
        frame = frame.drop(columns=["total_borrow"])

        # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
        frame = frame[
            frame["token"].isin(["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"])
        ]

        # each day from 2020-08-01 to 2022-12-31, calculate the
        # past 30-day moving average of borrow share of each token
        plot_df = (
            frame.groupby(["token"])["total_borrow_usd"]
            .rolling(window=30)
            .mean()
            .reset_index()
        )

    else:
        # calculate the supply share of each token each day
        frame["total_supply_usd"] = frame["total_supply_usd"].astype(float)
        frame["total_supply"] = frame.groupby("block_timestamp")[
            "total_supply_usd"
        ].transform("sum")
        frame["total_supply_usd"] = frame["total_supply_usd"] / frame["total_supply"]
        frame = frame.drop(columns=["total_supply"])

        # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
        frame = frame[
            frame["token"].isin(["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"])
        ]

        # each day from 2020-08-01 to 2022-12-31, calculate the past
        # 30-day moving average of borrow share of each token
        plot_df = (
            frame.groupby(["token"])["total_supply_usd"]
            .rolling(window=30)
            .mean()
            .reset_index()
        )

    # convert the date to datetime format for the frame
    frame["block_timestamp"] = pd.to_datetime(frame["block_timestamp"])

    token_col_name = "token"
    y_col_name = (
        "total_borrow_usd" if graph_type == "borrow_share" else "total_supply_usd"
    )
    x_col_name = "block_timestamp"
    return plot_df, token_col_name, x_col_name, y_col_name, frame


def borrow_supply_apy_prep(graph_type: str) -> tuple:
    """
    Function to preprocess the data for the borrow
    """

    # combine all csv files with "_processed" at the end of
    # the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"{COMPOUND_DATA_PATH}"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    list_df = []
    for filename in all_files:
        df_apy = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df_apy["token"] = "WETH"
        else:
            df_apy["token"] = token

        list_df.append(df_apy)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    frame = frame[
        frame["token"].isin(["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"])
    ]

    # convert the date to datetime format for the frame
    frame["block_timestamp"] = pd.to_datetime(frame["block_timestamp"])

    token_col_name = "token"
    y_col_name = "borrow_rate" if graph_type == "borrow_apy" else "supply_rates"
    x_col_name = "block_timestamp"

    # each day from 2020-08-01 to 2022-12-31, calculate the past
    # 30-day moving average of borrow share of each token
    plot_df = (
        frame.groupby(["token"])[y_col_name].rolling(window=30).mean().reset_index()
    )

    return plot_df, token_col_name, x_col_name, y_col_name, frame


def plot_ma(graph_type: str, source: str) -> None:
    """
    Function to plot the
    """
    # preprocessing for volume and tvl share
    if graph_type in [
        "volume_share",
        "tvl_share",
        "volume_in_share",
        "volume_out_share",
    ]:
        plot_df, token_col_name, x_col_name, y_col_name, frame = volume_tvl_prep(
            graph_type, source
        )
    elif graph_type in ["borrow_share", "supply_share"]:
        plot_df, token_col_name, x_col_name, y_col_name, frame = borrow_supply_prep(
            graph_type
        )
    elif graph_type in ["borrow_apy", "supply_apy"]:
        plot_df, token_col_name, x_col_name, y_col_name, frame = borrow_supply_apy_prep(
            graph_type
        )
    else:
        plot_df, token_col_name, x_col_name, y_col_name, frame = betweenness_prep(
            graph_type=graph_type, source=source
        )

    # plot the 30-day moving average of volume share of each token
    _, ax_ma = plt.subplots(figsize=(15, 10))
    for token in plot_df[token_col_name].unique():
        date = frame.loc[frame[token_col_name] == token][x_col_name]
        # plot the 30-day moving average of volume share of each token using date

        ax_ma.plot(
            date,
            plot_df[plot_df[token_col_name] == token][y_col_name],
            label=token,
            color=COLOR_DICT[token],
        )

        # fix the y-axis to be between 0 and 0.3 if the graph is apy
        if graph_type in ["borrow_apy", "supply_apy"]:
            ax_ma.set_ylim([0, 0.3])

        # # Check point: the correlated of TVL to the WETH price
        # # if the graph_type is tvl, then load in the data/data_global/gas_fee/avg_gas_fee.csv
        # # and plot the average gas fee on the same plot ETH Price (USD)
        # if graph_type == "tvl":
        #     # load in the data/data_global/gas_fee/avg_gas_fee.csv
        #     avg_gas_fee_df = pd.read_csv(
        #         rf"{GLOBAL_DATA_PATH}/gas_fee/avg_gas_fee.csv", index_col=None, header=0
        #     )
        #     # convert the date to datetime format for the frame
        #     avg_gas_fee_df["Date"] = pd.to_datetime(avg_gas_fee_df["Date(UTC)"])

        #     # keep the data after 2020-01-01
        #     avg_gas_fee_df = avg_gas_fee_df[avg_gas_fee_df["Date"] >= "2020-01-01"]

        #     # plot the ETH Price (USD) in different y-axis
        #     ax_gas_fee = ax_ma.twinx()
        #     ax_gas_fee.plot(
        #         avg_gas_fee_df["Date"],
        #         avg_gas_fee_df["ETH Price (USD)"],
        #         label="ETH Price (USD)",
        #         color="black",
        #     )

    for event_date in config["dev"]["config"]["moving_average_plot"]["EVENT_DATE_LIST"]:
        # Compound attack of 2020
        # Introduction of Uniswap V3
        # Luna crash
        # FTX collapse
        ax_ma.axvline(x=pd.to_datetime(event_date), color="red", linewidth=3, alpha=0.5)

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", borderaxespad=0.0, prop={"size": 40}
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # add some rotation for x tick labels
    plt.setp(ax_ma.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # tight layout
    plt.tight_layout()

    # save the figure

    if graph_type in [
        "volume_share",
        "tvl_share",
        "volume_in_share",
        "volume_out_share",
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
    ]:
        plt.savefig(f"{FIGURE_PATH}/{graph_type}_{source}.pdf")
    else:
        plt.savefig(f"{FIGURE_PATH}/{graph_type}.pdf")
    # plt.show()


if __name__ == "__main__":

    for iter_source in ["v2", "v3", "merged"]:
        for iter_graph_type in [
            "volume_in_share",
            "volume_out_share",
            "volume_share",
            "tvl_share",
        ]:
            plot_ma(graph_type=iter_graph_type, source=iter_source)

    for iter_graph_type in ["borrow_share", "supply_share", "borrow_apy", "supply_apy"]:
        plot_ma(graph_type=iter_graph_type, source=iter_source)

    for iter_source in ["v2", "v3", "v2v3"]:
        for iter_graph_type in [
            "betweenness_centrality_count",
            "betweenness_centrality_volume",
        ]:
            plot_ma(graph_type=iter_graph_type, source=iter_source)
