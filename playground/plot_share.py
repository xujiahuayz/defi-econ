import glob
import matplotlib.pyplot as plt
import pandas as pd

graph_type = "volume_share"
source = "merged"


def volume_tvl_prep(graph_type, source):
    """
    Function to plot the 30-day moving average graph of each token
    """

    # combine all csv files in data/data_network/merged/volume_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_share
    path = rf"data/data_network/{source}/{graph_type}"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df["Date"] = date
        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

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

    # each day from 2020-08-01 to 2022-12-31, calculate the past 30-day moving average of volume share of each token
    plot_df = (
        frame.groupby([token_col_name])[y_col_name]
        .rolling(window=30)
        .mean()
        .reset_index()
    )
    x_col_name = "Date"
    return plot_df, token_col_name, x_col_name, y_col_name, frame


def borrow_supply_prep(graph_type):
    """
    Function to preprocess the data for the borrow
    """

    # combine all csv files with "_processed" at the end of the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow

    # get all csv files in data/data_compound
    path = rf"data/data_compound"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df["token"] = "WETH"
        else:
            df["token"] = token

        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

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

        # each day from 2020-08-01 to 2022-12-31, calculate the past 30-day moving average of borrow share of each token
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

        # each day from 2020-08-01 to 2022-12-31, calculate the past 30-day moving average of borrow share of each token
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


def plot_ma(graph_type, source):
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
    else:
        plot_df, token_col_name, x_col_name, y_col_name, frame = borrow_supply_prep(
            graph_type
        )

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

    # plot the 30-day moving average of volume share of each token
    fig, ax = plt.subplots(figsize=(15, 10))
    for token in plot_df[token_col_name].unique():
        date = frame.loc[frame[token_col_name] == token][x_col_name]
        # plot the 30-day moving average of volume share of each token using date

        ax.plot(
            date,
            plot_df[plot_df[token_col_name] == token][y_col_name],
            label=token,
            color=color_dict[token],
        )

    # draw a thick vertical lines  with some transparency
    ax.axvline(
        x=pd.to_datetime("2020-11-26"), color="red", linewidth=3, alpha=0.5
    )  # Compound attack of 2020
    ax.axvline(
        x=pd.to_datetime("2021-05-05"), color="red", linewidth=3, alpha=0.5
    )  # Introduction of Uniswap V3
    ax.axvline(
        x=pd.to_datetime("2022-05-10"), color="red", linewidth=3, alpha=0.5
    )  # Luna crash
    ax.axvline(
        x=pd.to_datetime("2022-11-11"), color="red", linewidth=3, alpha=0.5
    )  # FTX collapse

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", borderaxespad=0.0, prop={"size": 40}
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # add some rotation for x tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # tight layout
    plt.tight_layout()
    plt.savefig(f"figures/{graph_type}_{source}.pdf")
    # plt.show()


if __name__ == "__main__":

    for source in ["v2", "v3", "merged"]:
        for graph_type in [
            "volume_in_share",
            "volume_out_share",
            "volume_share",
            "tvl_share",
            "borrow_share",
            "supply_share",
        ]:
            plot_ma(graph_type, source)
