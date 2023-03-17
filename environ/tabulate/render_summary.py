"""
Script to render the table of summary statistics.
"""
from pathlib import Path
import pandas as pd

from environ.constants import ALL_NAMING_DICT, TABLE_PATH
from environ.utils.variable_constructer import lag_variable, name_lag_variable


def render_summary_table(
    reg_panel: pd.DataFrame, sum_column: list[str] = list(), all_columns: bool = False
) -> pd.DataFrame:
    """
    Function to render the summary table.

    Args:
        reg_panel (pd.DataFrame): The panel data.
        sum_column (list[str]): The columns to be included in the summary table.
        all_columns (bool): Whether to include all columns.

    Returns:
        pd.DataFrame: The summary table.
    """

    # initiate the summary table
    sum_tab = pd.DataFrame()

    # whether to include all columns
    if all_columns is True:
        sum_tab = reg_panel.describe().T

    # otherwise, only include the specified columns
    else:
        sum_tab = reg_panel[sum_column].describe().T

    return sum_tab


# def render_summary_table_latex(
#     sum_tab: pd.DataFrame, file_name: str = "summary_table"
# ) -> pd.DataFrame:
#     """
#     Function to render the summatr table in latex.

#     Args:
#         sum_tab (pd.DataFrame): The summary table.
#         file_name (str): The file name of the summary table in latex.

#     Returns:
#         pd.DataFrame: The summary table in latex.
#     """

#     # generate the latex table for sum_tab
#     sum_tab_latex = sum_tab.to_latex(
#         float_format="{:,.2f}".format,
#         column_format="l" + "c" * (len(sum_tab.columns) - 1),
#         escape=False,
#     )

#     # write the latex table to file


if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # generate the summary table
    sum_tab = render_summary_table(
        reg_panel=reg_panel, sum_column=list(), all_columns=True
    )

    # print the summary table
    print(sum_tab)
