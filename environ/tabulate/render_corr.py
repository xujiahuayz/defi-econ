"""
Script to render the table of correlation heatmap.
"""
from typing import Literal, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import colors

from environ.constants import FIGURE_PATH, TABLE_PATH
from environ.utils.variable_constructer import (
    lag_variable_columns,
    map_variable_name_latex,
    name_lag_variable,
)

# This dictionary defines the colormap
COLOR_DICT = {
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
GnRd = colors.LinearSegmentedColormap("GnRd", COLOR_DICT)


def render_corr_cov_tab(
    data: pd.DataFrame,
    sum_column: list[str] = [
        "Volume_share",
        "Inflow_centrality",
    ],
    lag: Optional[int] = None,
    fig_type: Literal["corr", "cov"] = "corr",
) -> pd.DataFrame:
    """
    Function to render the correlation table.

    Args:
        data (pd.DataFrame): The panel data.
        sum_column (list[str]): The columns to be included in the correlation table.
        lag (int): The lag of the variables.
        fig_type (str): The type of the figure.

    Returns:
        pd.DataFrame: The correlation table.
    """

    # whether auto lag is enabled
    combi_column = sum_column + (
        [
            name_lag_variable(variable=col, lag=lag)
            for col in sum_column
            if col not in ["Stable", "is_boom"]
        ]
        if lag
        else []
    )

    # keep only the specified columns
    data = data[combi_column]

    # create the correlation table
    corr_cov_tab = data.corr() if fig_type == "corr" else data.cov()

    # if lag is enabled, remove the lagged variables from the rows
    # and remove the unlagged variables from the columns
    corr_cov_tab = (
        corr_cov_tab.drop(
            [name_lag_variable(variable=col, lag=lag) for col in sum_column],
            axis=0,
        )
        if lag
        else corr_cov_tab
    )

    corr_cov_tab = (
        corr_cov_tab.drop(
            [col for col in sum_column if col not in ["Stable", "is_boom"]], axis=1
        )
        if lag
        else corr_cov_tab
    )

    return corr_cov_tab


def render_corr_cov_figure(
    corr_cov_tab: pd.DataFrame,
    file_name: str,
):
    """
    Function to render the correlation table figure.

    Args:
        corr_tab (pd.DataFrame): The correlation table.
        file_name (str): The file name of the figure.
        lag (int): The lag of the variables.
        fig_type(str): The type of figure to be rendered.
    """
    # create a new dataframe with desired column names using map_variable_name_latex
    corr_cov_tab = corr_cov_tab.copy()

    corr_cov_tab.columns = corr_cov_tab.columns.map(map_variable_name_latex)
    corr_cov_tab.index = corr_cov_tab.index.map(map_variable_name_latex)

    # plot the correlation table
    hm = sns.heatmap(
        corr_cov_tab,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 6},
        fmt=".3f",
    )
    # set the x and y labels size
    hm.set_xticklabels(hm.get_xticklabels(), fontsize=8)
    hm.set_yticklabels(hm.get_yticklabels(), fontsize=8)

    # tight layout
    plt.tight_layout()
    # save the covariance matrix
    plt.savefig(FIGURE_PATH / f"{file_name}.pdf")
    plt.show()
    # close and clear everything
    plt.close()

    return hm


if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

    # columns to be included in the correlation table
    corr_columns = [
        "Volume_share",
        "avg_eigenvector_centrality",
        "TVL_share",
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
        "stableshare",
    ]

    # set the lag number
    LAG_NUM = 28

    # figure type
    FIGURE_TYPE = "corr"

    # file name
    FILE_NAME = "test"

    # lag the variables
    regression_panel = lag_variable_columns(
        data=regression_panel,
        variable=corr_columns,
        lag=LAG_NUM,
        time_variable="Date",
        entity_variable="Token",
    )

    # render the correlation table
    corr_cov_table = render_corr_cov_tab(
        data=regression_panel,
        sum_column=corr_columns,
        lag=LAG_NUM,
        fig_type=FIGURE_TYPE,
    )

    # render the correlation table figure
    render_corr_cov_figure(
        corr_cov_tab=corr_cov_table,
        file_name=FILE_NAME,
    )
