"""
Script to prepare the data for the betweenness centrality graph
"""

import glob
from pathlib import Path
from typing import Literal

import pandas as pd

from environ.constants import BETWEENNESS_DATA_PATH, KEY_TOKEN_LIST, PLOT_DATA_PATH


def betweenness_prep(
    graph_type: Literal[
        "betweenness_centrality_count", "betweenness_centrality_volume"
    ],
    source: Literal["v2", "v3", "v2v3"],
) -> None:
    """
    Function to prepare the data for the betweenness centrality graph
    """

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
    frame = frame[frame["node"].isin(KEY_TOKEN_LIST)]

    # plot the 30-day moving average of betweenness centrality of each token
    # the x-axis is date, the y-axis is betweenness centrality
    # the plot is saved in data/data_betweenness/betweenness/betweenness.png
    frame[graph_type] = frame[graph_type].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=["node", "Date"])

    # rename the node column to Token and Date to time
    frame = frame.rename(columns={"node": "Token"})

    # save the dataframe to csv in table path
    frame.to_csv(Path(PLOT_DATA_PATH) / f"{graph_type}_{source}.csv", index=False)


if __name__ == "__main__":
    for graph_type in [
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
    ]:
        for source in ["v2", "v3", "v2v3"]:
            betweenness_prep(graph_type, source)
