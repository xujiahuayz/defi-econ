"""

University College London
Project : defi_econ
Topic   : sum_generator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Generate the summary statistics.

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as colors
from environ.utils.config_parser import Config

# Initialize the config parser
config = Config()

# Initialize the path
FIGURE_PATH = config["dev"]["config"]["result"]["FIGURE_PATH"]
TABLE_PATH = config["dev"]["config"]["result"]["TABLE_PATH"]


# Initialize constants
NAMING_DIC_PROPERTIES_OF_DOMINANCE = {
    # Dominance
    "Volume_share": "${\it VShare}$",
    "volume_in_share": "${\it VShare}^{\it In}$",
    "volume_out_share": "${\it VShare}^{\it Out}$",
    # Eigenvector
    "Inflow_centrality": "${\it EigenCent}^{In}$",
    "Outflow_centrality": "${\it EigenCent}^{Out}$",
    # Betweenness
    "betweenness_centrality_count": "${\it BetwCent}^C$",
    "betweenness_centrality_volume": "${\it BetwCent}^V$",
    # Store
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
    "borrow_rate": "${\it BorrowAPY}^{USD}$",
    "supply_rates": "${\it SupplyAPY}^{USD}$",
    "beta": "${\it Beta}$",
    "std": "${\it \sigma}^{USD}$",
    "average_return": "${\it \mu}^{USD}$",
    # Other
    "corr_gas": "${\it CorrGas}$",
    "corr_sp": "${\it CorrSP}$",
    "corr_eth": "${\it CorrETH}$",
    "log_return": "${R}^{\it USD}$",
    "mcap": "${\it MCap}^{USD}$",
    "Nonstable": "${\i Nonstable}$",
    "IsWETH": "${\i IsWETH}$",
    "Gas_fee": "${\t GasPrice}$",
    "dollar_exchange_rate": "${\it ExchangeRate}^{USD}$",
    "TVL_share": "${\it LiquidityShare}$",
    "exceedance": "${\it exceedance}^{USD}$",
    "Gas_fee_volatility": "${\t \sigma}_{Gas}$",
    # Drop
    "corr_sentiment": "${\it CorrSent}$",
}

NAMING_DIC_HERFINDAHL = {
    "herfindahl_volume": "${\t HHIVolume}$",
    "herfindahl_inflow_centrality": "${\t HHIEigenCent}^{In}$",
    "herfindahl_outflow_centrality": "${\t HHIEigenCent}^{Out}$",
    "herfindahl_betweenness_centrality_count": "${\t HHIBetwCent}^C$",
    "herfindahl_betweenness_centrality_volume": "${\t HHIBetwCent}^V$",
    "total_volumes": "${\t TotalVolume}$",
    "S&P": "${\t R}^{USD}_{SP}$",
    "S&P_volatility": "${\t \sigma}^{USD}_{SP}$",
    "Gas_fee": "${\t GasPrice}$",
    "Gas_fee_volatility": "${\t \sigma}_{Gas}$",
}

# Initialize constants
NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG = {
    # Dominance
    "${\it VShare}$": "${\it-1 VShare}$",
    "${\it VShare}^{\it In}$": "${\it-1 VShare}^{\it-1 In}$",
    "${\it VShare}^{\it Out}$": "${\it-1 VShare}^{\it-1 Out}$",
    # Eigenvector
    "${\it EigenCent}^{In}$": "${\it-1 EigenCent}^{In}$",
    "${\it EigenCent}^{Out}$": "${\it-1 EigenCent}^{Out}$",
    # Betweenness
    "${\it BetwCent}^C$": "${\it-1 BetwCent}^C$",
    "${\it BetwCent}^V$": "${\it-1 BetwCent}^V$",
    # Store
    "${\it BorrowShare}$": "${\it-1 BorrowShare}$",
    "${\it SupplyShare}$": "${\it-1 SupplyShare}$",
    "${\it BorrowAPY}^{USD}$": "${\it-1 BorrowAPY}^{USD}$",
    "${\it SupplyAPY}^{USD}$": "${\it-1 SupplyAPY}^{USD}$",
    "${\it Beta}$": "${\it-1 Beta}$",
    "${\it \sigma}^{USD}$": "${\it-1 \sigma}^{USD}$",
    "${\it \mu}^{USD}$": "${\it-1 \mu}^{USD}$",
    # Other
    "${\it CorrGas}$": "${\it-1 CorrGas}$",
    "${\it CorrSP}$": "${\it-1 CorrSP}$",
    "${\it CorrETH}$": "${\it-1 CorrETH}$",
    "${R}^{\it USD}$": "${R}^{\it-1 USD}$",
    "${\it MCap}^{USD}$": "${\it-1 MCap}^{USD}$",
    "${\i Nonstable}$": "${\i Nonstable}$",
    "${\i IsWETH}$": "${\i IsWETH}$",
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\it ExchangeRate}^{USD}$": "${\it-1 ExchangeRate}^{USD}$",
    "${\it LiquidityShare}$": "${\it-1 LiquidityShare}$",
    "${\it exceedance}^{USD}$": "${\it-1 exceedance}^{USD}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
    # Drop
    "${\it CorrSent}$": "${\it-1 CorrSent}$",
}

NAMING_DIC_HERFINDAHL_LAG = {
    "${\t HHIVolume}$": "${\t-1 HHIVolume}$",
    "${\t HHIEigenCent}^{In}$": "${\t-1 HHIEigenCent}^{In}$",
    "${\t HHIEigenCent}^{Out}$": "${\t-1 HHIEigenCent}^{Out}$",
    "${\t HHIBetwCent}^C$": "${\t-1 HHIBetwCent}^C$",
    "${\t HHIBetwCent}^V$": "${\t-1 HHIBetwCent}^V$",
    "${\t TotalVolume}$": "${\t-1 TotalVolume}$",
    "${\t R}^{USD}_{SP}$": "${\t-1 R}^{USD}_{SP}$",
    "${\t \sigma}^{USD}_{SP}$": "${\t-1 \sigma}^{USD}_{SP}$",
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
}


def generate_sum_herfindahl(
    reg_panel: pd.DataFrame, file_name: str, lag=False
) -> pd.DataFrame:
    """
    Generate the summary statistics for the herfindahl
    """

    # drop inf and -inf
    reg_panel = reg_panel.replace([np.inf, -np.inf], np.nan)

    # rename the panel column names to be more readable
    reg_panel = reg_panel.rename(columns=NAMING_DIC_HERFINDAHL)

    # This dictionary defines the colormap
    cdict3 = {
        "red": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.8, 1.0),
            (0.75, 1.0, 1.0),
            (1.0, 0.4, 1.0),
        ),
        "green": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.9, 0.9),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "blue": (
            (0.0, 0.0, 0.4),
            (0.25, 1.0, 1.0),
            (0.5, 1.0, 0.8),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "alpha": ((0.0, 1.0, 1.0), (0.5, 0.3, 0.3), (1.0, 1.0, 1.0)),
    }

    # Create the colormap using the dictionary with the range of -1 to 1
    # make sure the range of the ledgend is -1 to 1
    GnRd = colors.LinearSegmentedColormap("GnRd", cdict3)

    if lag:
        # create lagged columns except for the token and the date
        for col_name in reg_panel.keys():
            if col_name not in ["Date"]:
                reg_panel[f"{col_name}_lag"] = reg_panel[col_name].shift(1)

    # create the correlation matrix and set the decimal places to 2 and keep the digits
    corr = reg_panel.corr().round(2)

    # plot the correlation matrix
    plt.figure(figsize=(20, 20))
    sns.heatmap(
        corr,
        xticklabels=corr.columns,
        yticklabels=corr.columns,
        annot=True,
        cmap=GnRd,
        annot_kws={"size": 10},
    )

    # font size smaller
    plt.rcParams.update({"font.size": 10})

    # save the figure
    plt.savefig(rf"{FIGURE_PATH}/correlation_matrix_{file_name}.pdf")

    # save the correlation matrix as a csv file
    corr.to_csv(rf"{TABLE_PATH}/correlation_matrix_{file_name}.csv")

    # calculate the summary statistics of the panel dataset
    summary = reg_panel.describe()

    # take the transpose of the summary statistics
    summary = summary.T

    # save the summary statistics as a csv file
    summary.to_csv(rf"{TABLE_PATH}/summary_statistics_{file_name}.csv")

    # save the summary statistics as a latex file
    with open(rf"{TABLE_PATH}/summary_statistics_{file_name}.tex", "w") as tf:
        tf.write(summary.to_latex())

    return reg_panel


def generate_sum(reg_panel: pd.DataFrame, file_name: str, lag=False) -> pd.DataFrame:
    """
    Generate the summary statistics.
    """

    # sort the values by Token and Date
    reg_panel = reg_panel.sort_values(by=["Token", "Date"])

    # drop inf and -inf
    reg_panel = reg_panel.replace([np.inf, -np.inf], np.nan)

    # rename the panel column names to be more readable
    reg_panel = reg_panel.rename(columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE)

    # if lag is true
    if lag:
        # create lagged columns except for the token and the date
        for col_name in reg_panel.keys():
            if col_name not in ["Token", "Date"]:
                reg_panel[f"{col_name}_lag"] = reg_panel.groupby("Token")[
                    col_name
                ].shift(1)

    # create the correlation matrix and set the decimal places to 2 and keep the digits
    corr = reg_panel.corr().round(2)

    # # change the column names to be more readable
    # corr = corr.rename(columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE)

    # set the borrow_rate, borrow_rate to 1
    corr.loc["${\it BorrowAPY}^{USD}$", "${\it BorrowAPY}^{USD}$"] = 1

    # This dictionary defines the colormap
    cdict3 = {
        "red": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.8, 1.0),
            (0.75, 1.0, 1.0),
            (1.0, 0.4, 1.0),
        ),
        "green": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.9, 0.9),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "blue": (
            (0.0, 0.0, 0.4),
            (0.25, 1.0, 1.0),
            (0.5, 1.0, 0.8),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "alpha": ((0.0, 1.0, 1.0), (0.5, 0.3, 0.3), (1.0, 1.0, 1.0)),
    }

    # Create the colormap using the dictionary with the range of -1 to 1
    # make sure the range of the ledgend is -1 to 1
    GnRd = colors.LinearSegmentedColormap("GnRd", cdict3)

    if lag:
        sns.heatmap(
            corr,
            xticklabels=corr.columns,
            yticklabels=corr.columns,
            annot=True,
            cmap=GnRd,
            vmin=-1,
            vmax=1,
            annot_kws={"size": 2},
        )

        # lanel font size higher
        plt.xticks(fontsize=3)
        plt.yticks(fontsize=3)
    else:
        # plot the heatmap
        sns.heatmap(
            corr,
            xticklabels=corr.columns,
            yticklabels=corr.columns,
            annot=True,
            cmap=GnRd,
            vmin=-1,
            vmax=1,
            annot_kws={"size": 4},
        )

        # font size smaller
        plt.rcParams.update({"font.size": 4})

    # tight layout
    plt.tight_layout()

    # save the figure
    plt.savefig(rf"{FIGURE_PATH}/correlation_matrix_{file_name}.pdf")

    # save the correlation matrix as a csv file
    corr.to_csv(rf"{TABLE_PATH}/correlation_matrix_{file_name}.csv")

    # calculate the summary statistics of the panel dataset
    summary = reg_panel.describe()

    # take the transpose of the summary statistics
    summary = summary.T

    # save the summary statistics as a csv file
    summary.to_csv(rf"{TABLE_PATH}/summary_statistics_{file_name}.csv")

    # save the summary statistics as a latex file
    with open(rf"{TABLE_PATH}/summary_statistics_{file_name}.tex", "w") as tf:
        tf.write(summary.to_latex())

    return reg_panel
