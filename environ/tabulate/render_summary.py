"""
Script to render the table of summary statistics.
"""
import warnings
from pathlib import Path
import pandas as pd
from environ.constants import ALL_NAMING_DICT, TABLE_PATH

warnings.filterwarnings("ignore")


def _render_summary_table(
    data: pd.DataFrame,
    sum_column: list[str] = ["is_boom", "mcap_share"],
    all_columns: bool = False,
) -> pd.DataFrame:
    """
    Function to render the summary table.

    Args:
        data (pd.DataFrame): The panel data.
        sum_column (list[str]): The columns to be included in the summary table.
        all_columns (bool): Whether to include all columns.

    Returns:
        pd.DataFrame: The summary table.
    """

    # whether to include all columns
    if all_columns is True:
        sum_tab = data.describe()

    # otherwise, only include the specified columns
    else:
        sum_tab = data[sum_column].describe()

    return sum_tab


def render_summary_table_latex(file_name: str = "test", **kwargs) -> None:
    """
    Function to render the summatr table in latex.

    Args:
        sum_tab (pd.DataFrame): The summary table.
        file_name (str): The file name of the summary table in latex.
    Returns:
        pd.DataFrame: The summary table in latex.
    """

    # generate the summary table in latex
    sum_tab = _render_summary_table(**kwargs)

    # rename the columns
    sum_tab.rename(columns=ALL_NAMING_DICT, inplace=True)

    # transpose the summary table
    sum_tab = sum_tab.T

    # save the summary statistics as a csv file
    sum_tab.to_csv(rf"{TABLE_PATH}/summary_statistics_{file_name}.csv")

    # generate the latex table for sum_tab
    sum_tab_latex = sum_tab.to_latex()

    # save the summary statistics as a latex file
    with open(
        rf"{TABLE_PATH}/summary_statistics_{file_name}.tex", "w", encoding="utf-8"
    ) as to_file:
        to_file.write(sum_tab_latex)


if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # generate the summary table
    render_summary_table_latex(
        file_name="test",
        data=regression_panel,
        sum_column=None,
        all_columns=True,
    )
