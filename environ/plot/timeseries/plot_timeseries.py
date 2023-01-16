"""

University College London
Project : defi-econ
Topic   : plot_timeseries.py
Author  : Yichen Luo
Date    : 2022-01-05
Desc    : plot the time series data.

"""

# Import Python modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Import internal modules
from environ.utils.config_parser import Config


def plot_timeseries(date_list: list, uniswap_version: str) -> None:

    """
    Plot the time series data of eigenvector centrality
    """

    # Initialize configuration
    config = Config()

    # Constants
    network_data_path = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
    token_list = ["DAI", "FEI", "USDC", "USDT", "WETH", "WBTC", "MATIC"]
    # Load the dataframe for eigenvector centrality

    fig_in, eigen_in_plot = plt.subplots(figsize=(10, 8))
    fig_out, eigen_out_plot = plt.subplots(figsize=(10, 8))

    for token in tqdm(token_list):
        eigen_in_list = []

        for date in date_list:
            date_str = date.strftime("%Y%m%d")
            eigen_in_df = pd.read_csv(
                f"{network_data_path}/{uniswap_version}/inflow_centrality/centrality_{uniswap_version}_{date_str}.csv"
            )

            if (
                eigen_in_df.loc[
                    eigen_in_df["token"] == token, "eigenvector_centrality"
                ].shape[0]
                == 0
            ):
                eigen_in_list.append(np.nan)
            else:
                eigen_in_list.append(
                    eigen_in_df.loc[
                        eigen_in_df["token"] == token, "eigenvector_centrality"
                    ].values[0]
                )

        eigen_in_plot.plot(pd.to_datetime(date_list), eigen_in_list, label=token)
        eigen_in_plot.set_xlabel("Date")
        eigen_in_plot.set_ylabel("Eigenvector Centrality")
        eigen_in_plot.set_title("Inflow Eigenvector Centrality")
        eigen_in_plot.tick_params(axis="x", labelrotation=30)
        eigen_in_plot.legend()

    fig_in.savefig(f"{network_data_path}/eigen_in.png")

    for token in tqdm(token_list):
        eigen_out_list = []

        for date in date_list:
            date_str = date.strftime("%Y%m%d")
            eigen_out_df = pd.read_csv(
                f"{network_data_path}/{uniswap_version}/outflow_centrality/centrality_{uniswap_version}_{date_str}.csv"
            )

            if (
                eigen_out_df.loc[
                    eigen_out_df["token"] == token, "eigenvector_centrality"
                ].shape[0]
                == 0
            ):
                eigen_out_list.append(np.nan)
            else:
                eigen_out_list.append(
                    eigen_out_df.loc[
                        eigen_out_df["token"] == token, "eigenvector_centrality"
                    ].values[0]
                )

        eigen_out_plot.plot(pd.to_datetime(date_list), eigen_out_list, label=token)
        eigen_out_plot.set_xlabel("Date")
        eigen_out_plot.set_ylabel("Eigenvector Centrality")
        eigen_out_plot.set_title("Outflow Eigenvector Centrality")
        eigen_out_plot.tick_params(axis="x", labelrotation=30)
        eigen_out_plot.legend()

    fig_out.savefig(f"{network_data_path}/eigen_out.png")
