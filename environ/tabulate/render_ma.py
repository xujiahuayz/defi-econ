"""
Script to render the moving averages of the variables
"""

import pandas as pd
from environ.constants import NETWORK_DATA_PATH, PLOT_DATA_PATH
from environ.plot.plot_ma import preprocess_ma, plot_time_series

# from environ.plot.plot_ma import preprocess_ma, plot_ma, plot_time_series


if __name__ == """__main__""":
    # Iterate through all the csv files in the table path
    for graph_type in [
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
    ]:
        for source in ["v2", "v3", "v2v3"]:
            # read the csv file
            df = pd.read_csv(rf"{PLOT_DATA_PATH}/{graph_type}_{source}.csv")

            # preprocess the data
            df = preprocess_ma(df=df, value_colume=graph_type)

            # plot the moving average
            plot_time_series(df, file_name=f"{graph_type}_{source}")

    for graph_type in [
        "volume_share",
        "volume_in_share",
        "volume_out_share",
        "tvl_share",
        "eigen_in",
        "eigen_out",
    ]:
        for source in ["v2", "v3", "merged"]:
            # read the csv file
            df = pd.read_csv(rf"{PLOT_DATA_PATH}/{graph_type}_{source}.csv")

            # preprocess the data
            df = preprocess_ma(df=df, value_colume=graph_type)

            # plot the moving average
            plot_time_series(df, file_name=f"{graph_type}_{source}")
