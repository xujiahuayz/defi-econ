"""

University College London
Project : defi_econ
Topic   : sum_generator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Generate the summary statistics.

"""

import pandas as pd
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
NAMING_DIC = {
    "TVL_share": "${\it LiquidityShare}$",
    "Inflow_centrality": "${\it EigenCent}^{In}$",
    "Outflow_centrality": "${\it EigenCent}^{Out}$",
    "Volume_share": "${\it VShare}$",
    "volume_in_share": "${\it VShare}^{\it In}$",
    "volume_out_share": "${\it VShare}^{\it Out}$",
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
    "betweenness_centrality_count": "${\it BetwCent}^C$",
    "betweenness_centrality_volume": "${\it BetwCent}^V$",
    "cov_gas": "${\it CovGas}$",
    "cov_sp": "${\it CovSP}$",
    "cov_eth": "${\it CovETH}$",
    "log_return": "${R}^{\it USD}$",
    "std": "${\it \sigma}^{USD}$",
    "borrow_rate": "${\it BorrowAPY}^{USD}$",
    "supply_rates": "${\it SupplyAPY}^{USD}$",
}


def generate_sum(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the summary statistics.
    """

    # create the correlation matrix and set the decimal places to 2 and keep the digits
    corr = reg_panel.corr().round(2)

    # change the column names to be more readable
    corr = corr.rename(columns=NAMING_DIC)

    # set the borrow_rate, borrow_rate to 1
    corr.loc["borrow_rate", "${\it BorrowAPY}^{USD}$"] = 1

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

    # plot the heatmap
    sns.heatmap(
        corr,
        xticklabels=corr.columns,
        yticklabels=corr.columns,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 7},
    )

    # tight layout
    plt.tight_layout()

    # save the figure
    plt.savefig(rf"{FIGURE_PATH}/correlation_matrix.pdf")

    # save the correlation matrix as a csv file
    corr.to_csv(rf"{TABLE_PATH}/correlation_matrix.csv")

    # rename the panel column names to be more readable
    reg_panel = reg_panel.rename(columns=NAMING_DIC)

    # calculate the summary statistics of the panel dataset
    summary = reg_panel.describe()

    # take the transpose of the summary statistics
    summary = summary.T

    # save the summary statistics as a csv file
    summary.to_csv(rf"{TABLE_PATH}/summary_statistics.csv")

    # save the summary statistics as a latex file
    with open(rf"{TABLE_PATH}/summary_statistics.tex", "w") as tf:
        tf.write(summary.to_latex())

    return reg_panel
