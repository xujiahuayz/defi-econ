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

# Initialize configuration
config = Config()

# Constants
network_data_path = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
figure_path = config["dev"]["config"]["result"]["FIGURE_PATH"]
token_list = ["DAI", "FEI", "USDC", "USDT", "WETH", "WBTC", "MATIC"]


def plot_timeseries(date_list: list, uniswap_version: str) -> None:

    """
    Plot the time series data of eigenvector centrality
    """
    # Load the dataframe for eigenvector centrality

    fig_in, eigen_in_plot = plt.subplots(figsize=(15, 10))

    # DataFrame to store inflow eigenvector of all tokens
    eigen_in = pd.DataFrame()

    for token in tqdm(token_list):

        # List to store inflow eigenvector of a specific token and
        eigen_in_list = []

        for date in date_list:
            date_str = date.strftime("%Y%m%d")
            eigen_in_df = pd.read_csv(
                f"{network_data_path}/{uniswap_version}/inflow_centrality/\
centrality_{uniswap_version}_{date_str}.csv"
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

        # Calculate moving averages
        eigen_in_ma_df = pd.DataFrame.from_dict(
            {"date": pd.to_datetime(date_list), "eigen_in": eigen_in_list}
        )
        eigen_in_ma_df["eigen_in_ma_30"] = eigen_in_ma_df["eigen_in"].rolling(30).mean()
        eigen_in_plot.plot(
            pd.to_datetime(date_list),
            eigen_in_ma_df["eigen_in_ma_30"],
            label=token,
            color=color_dict[token],
        )

        # DataFrame to implement the summary statistics
        eigen_in[token] = eigen_in_ma_df["eigen_in"]

    for event_date in config["dev"]["config"]["moving_average_plot"]["EVENT_DATE_LIST"]:
        # Compound attack of 2020
        # Introduction of Uniswap V3
        # Luna crash
        # FTX collapse
        eigen_in_plot.axvline(
            x=pd.to_datetime(event_date), color="red", linewidth=3, alpha=0.5
        )

    # place the legend outside the plot without border
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", borderaxespad=0.0, prop={"size": 40}
    )

    # enlarge the font of ticker
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)

    # add some rotation for x tick labels
    plt.setp(
        eigen_in_plot.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
    )

    # tight layout
    plt.tight_layout()

    fig_in.savefig(f"{figure_path}/eigen_in_{uniswap_version}.pdf")
    eigen_in.to_csv(f"{network_data_path}/eigen_in_{uniswap_version}.csv", index=False)

    fig_out, eigen_out_plot = plt.subplots(figsize=(15, 10))
    eigen_out = pd.DataFrame()

    for token in tqdm(token_list):

        # List to store inflow eigenvector of a specific token and
        eigen_out_list = []

        for date in date_list:
            date_str = date.strftime("%Y%m%d")
            eigen_out_df = pd.read_csv(
                f"{network_data_path}/{uniswap_version}/outflow_centrality/\
centrality_{uniswap_version}_{date_str}.csv"
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
        # Calculate moving averages
        eigen_out_ma_df = pd.DataFrame.from_dict(
            {"date": pd.to_datetime(date_list), "eigen_out": eigen_out_list}
        )
        eigen_out_ma_df["eigen_out_ma_30"] = (
            eigen_out_ma_df["eigen_out"].rolling(30).mean()
        )

        eigen_out_plot.plot(
            pd.to_datetime(date_list),
            eigen_out_ma_df["eigen_out_ma_30"],
            label=token,
            color=color_dict[token],
        )
        for event_date in config["dev"]["config"]["moving_average_plot"][
            "EVENT_DATE_LIST"
        ]:
            # Compound attack of 2020
            # Introduction of Uniswap V3
            # Luna crash
            # FTX collapse
            eigen_out_plot.axvline(
                x=pd.to_datetime(event_date), color="red", linewidth=3, alpha=0.5
            )

        # place the legend outside the plot without border
        _ = plt.legend(
            bbox_to_anchor=(1.01, 1),
            loc="upper left",
            borderaxespad=0.0,
            prop={"size": 40},
        )

        # enlarge the font of ticker
        plt.xticks(fontsize=40)
        plt.yticks(fontsize=40)

        # add some rotation for x tick labels
        plt.setp(
            eigen_out_plot.get_xticklabels(),
            rotation=45,
            ha="right",
            rotation_mode="anchor",
        )

        # tight layout
        plt.tight_layout()

        # DataFrame to implement the summary statistics
        eigen_out[token] = eigen_out_ma_df["eigen_out"]

    fig_out.savefig(f"{figure_path}/eigen_out_{uniswap_version}.pdf")
    eigen_out.to_csv(
        f"{network_data_path}/eigen_out_{uniswap_version}.csv", index=False
    )
