import glob
import matplotlib.pyplot as plt
import pandas as pd

graph_type = "volume_share"
source = "merged"


def plot_ma(graph_type, source):

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

    # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
    frame = frame[
        frame["Token"].isin(["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"])
    ]

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
    # the x-axis is date, the y-axis is volume share
    # the plot is saved in data/data_network/merged/volume_share/volume_share.png
    frame["Volume"] = frame["Volume"].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=["Token", "Date"])

    # each day from 2020-08-01 to 2022-12-31, calculate the past 30-day moving average of volume share of each token
    plot_df = frame.groupby(["Token"])["Volume"].rolling(window=30).mean().reset_index()

    # plot the 30-day moving average of volume share of each token
    fig, ax = plt.subplots(figsize=(15, 10))
    for token in plot_df["Token"].unique():
        date = frame.loc[frame["Token"] == token]["Date"]
        # plot the 30-day moving average of volume share of each token using date
        ax.plot(
            date,
            plot_df[plot_df["Token"] == token]["Volume"],
            label=token,
            color=color_dict[token],
        )

    # draw a thick vertical lines  with some transparency
    ax.axvline(x=pd.to_datetime("2020-11-26"), color="red", linewidth=3, alpha=0.5)
    ax.axvline(x=pd.to_datetime("2021-05-05"), color="red", linewidth=3, alpha=0.5)
    ax.axvline(x=pd.to_datetime("2022-03-10"), color="red", linewidth=3, alpha=0.5)
    ax.axvline(x=pd.to_datetime("2022-11-11"), color="red", linewidth=3, alpha=0.5)

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", borderaxespad=0.0, prop={"size": 15}
    )

    # tight layout
    plt.tight_layout()
    plt.savefig(f"figures/{graph_type}_{source}.pdf")
    # plt.show()


if __name__ == "__main__":

    for source in ["v2", "v3", "merged"]:
        for graph_type in ["volume_in_share", "volume_out_share", "volume_share"]:
            plot_ma(graph_type, source)
