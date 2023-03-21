"""
Script to render the moving averages of the variables
"""

from pathlib import Path
import glob
import pandas as pd
from environ.constants import TABLE_PATH, PLOT_DATA_PATH, KEY_TOKEN_LIST
from environ.plot.plot_ma import preprocess_ma, plot_time_series

# from environ.plot.plot_ma import preprocess_ma, plot_ma, plot_time_series


if __name__ == """__main__""":
    # read the csv file
    df = pd.read_csv(rf"{PLOT_DATA_PATH}/betweenness_centrality_count_v2.csv")

    # preprocess the data
    df = preprocess_ma(df=df, value_colume="betweenness_centrality_count")

    # plot the moving average
    plot_time_series(df)
