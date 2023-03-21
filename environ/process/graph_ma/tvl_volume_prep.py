"""
Script to prepare the data for the volume centrality graph
"""

from typing import Literal
from pathlib import Path
import glob
import pandas as pd
from environ.constants import PLOT_DATA_PATH, NETWORK_DATA_PATH, KEY_TOKEN_LIST


def tvl_volume_prep(
    graph_type: Literal[
        "volume_share", "volume_in_share", "volume_out_share", "tvl_share"
    ],
    source: Literal["v2", "v3", "merged"],
) -> None:
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
        # rename the total_tvl to tvl_share
        frame = frame.rename(columns={"total_tvl": graph_type})

        # rename the token column to Token
        frame = frame.rename(columns={"token": "Token"})

    else:
        # rename the Volume column to graph_type
        frame = frame.rename(columns={"Volume": graph_type})

    token_col_name = "Token"
    y_col_name = graph_type

    # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
    frame = frame[frame[token_col_name].isin(KEY_TOKEN_LIST)]

    # plot the 30-day moving average of volume share of each token
    # the x-axis is date, the y-axis is volume share
    # the plot is saved in data/data_network/merged/volume_share/volume_share.png
    frame[y_col_name] = frame[y_col_name].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=[token_col_name, "Date"])

    # save the dataframe to csv in table path
    frame.to_csv(Path(PLOT_DATA_PATH) / f"{graph_type}_{source}.csv", index=False)


if __name__ == "__main__":
    for graph_type in [
        "volume_share",
        "volume_in_share",
        "volume_out_share",
        "tvl_share",
    ]:
        for source in ["v2", "v3", "merged"]:
            tvl_volume_prep(graph_type, source)
