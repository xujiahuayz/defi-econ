"""
Script to render the table of correlation heatmap.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors
from environ.constants import TABLE_PATH, FIGURE_PATH
from environ.utils.variable_constructer import (
    lag_variable,
    name_lag_variable,
    map_variable_name_latex,
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
        "betweenness_centrality_count",
    ]
    lag: Optional[int] = 7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to render the correlation table.

    Args:
        data (pd.DataFrame): The panel data.
        sum_column (list[str]): The columns to be included in the correlation table.
        all_columns (bool): Whether to include all columns.
        auto_lag (bool): Whether to automatically lag the variables.
        lag (int): The lag of the variables.

    Returns:
        pd.DataFrame: The correlation table.
    """

    # whether auto lag is enabled
    if auto_lag is True:
        combi_column = sum_column + [
            name_lag_variable(variable=col, lag=lag)
            for col in sum_column
            if col not in ["Stable", "is_boom"]
        ]
    else:
        combi_column = sum_column

    # keep only the specified columns
    data = data[combi_column]

    # create the correlation table
    corr_tab = data.corr().round(2)

    # if lag is enabled, remove the lagged variables from the rows
    # and remove the unlagged variables from the columns
    if auto_lag is True:
        corr_tab = corr_tab.drop(
            [name_lag_variable(variable=col, lag=lag) for col in sum_column],
            axis=0,
        )
        corr_tab = corr_tab.drop(
            [col for col in sum_column if col not in ["Stable", "is_boom"]], axis=1
        )

    # iterate through the columns to map the variable names to latex
    for col in corr_tab.columns:
        corr_tab.rename(columns={col: map_variable_name_latex(col)}, inplace=True)

    # iterate through the rows to map the variable names to latex
    for row in corr_tab.index:
        corr_tab.rename(index={row: map_variable_name_latex(row)}, inplace=True)

    # create the covariance table
    cov_tab = data.cov().round(2)

    # if lag is enabled, remove the lagged variables from the rows
    # and remove the unlagged variables from the columns
    if auto_lag is True:
        cov_tab = cov_tab.drop(
            [name_lag_variable(variable=col, lag=lag) for col in sum_column],
            axis=0,
        )
        cov_tab = cov_tab.drop(
            [col for col in sum_column if col not in ["Stable", "is_boom"]], axis=1
        )

    # iterate through the columns to map the variable names to latex
    for col in cov_tab.columns:
        cov_tab.rename(columns={col: map_variable_name_latex(col)}, inplace=True)

    # iterate through the rows to map the variable names to latex
    for row in cov_tab.index:
        cov_tab.rename(index={row: map_variable_name_latex(row)}, inplace=True)

    return corr_tab, cov_tab


def render_corr_cov_figure(
    corr_tab: pd.DataFrame,
    cov_tab: pd.DataFrame,
    file_name: str = "test",
    # auto_lag: bool = True,
    lag: Optional[int] = None,
) -> None:
    """
    Function to render the correlation table figure.

    Args:
        file_name (str): The file name of the figure.
        corr_tab (pd.DataFrame): The correlation table.
        cov_tab (pd.DataFrame): The covariance table.
    """

    # plot the correlation table
    sns.heatmap(
        corr_tab,
        xticklabels=corr_tab.columns,
        yticklabels=corr_tab.index,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 6 if lag else 4},
    )

    # font size smaller
    plt.rcParams.update({"font.size": 6 if lag else 4})

    # tight layout
    plt.tight_layout()
    plt.show()
    # save the covariance matrix
    plt.savefig(
        FIGURE_PATH / f'correlation_matrix_{file_name}{f"_{lag}" if lag else ""}.pdf'
    )
    plt.clf()

    # plot the heatmap for the covariance matrix
    sns.heatmap(
        cov_tab,
        xticklabels=cov_tab.columns,
        yticklabels=cov_tab.index,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 6} if auto_lag else {"size": 4},
    )

    # font size smaller
    plt.rcParams.update({"font.size": 6} if auto_lag else {"font.size": 4})

    # tight layout
    plt.tight_layout()

    # save the covariance matrix
    plt.savefig(
        FIGURE_PATH / f"covariance_matrix_{file_name}_{lag}_lag.pdf"
        if auto_lag
        else rf"{FIGURE_PATH}/covariance_matrix_{file_name}.pdf"
    )
    plt.clf()


if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

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

    # whether to plot the auto lagged correlation table
    AUTO_LAG = True

    # file name
    FILE_NAME = "test"

    # lag the variables
    regression_panel = lag_variable(
        data=regression_panel,
        variable=corr_columns,
        lag=LAG_NUM,
        time_variable="Date",
        entity_variable="Token",
    )

    # render the correlation table
    corr_table, cov_table = render_corr_cov_tab(
        data=regression_panel, sum_column=corr_columns, auto_lag=AUTO_LAG, lag=LAG_NUM
    )

    # render the correlation table figure
    render_corr_cov_figure(
        corr_tab=corr_table,
        cov_tab=cov_table,
        file_name=FILE_NAME,
        auto_lag=AUTO_LAG,
        lag=LAG_NUM,
    )
