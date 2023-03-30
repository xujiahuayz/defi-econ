"""
Script to render the table of summary statistics.
"""
from pathlib import Path

import pandas as pd

from environ.constants import ALL_NAMING_DICT, DATA_PATH, TEST_RESULT_PATH


def render_summary_table_latex(
    data: pd.DataFrame,
    sum_column: list[str] | None = None,
    file_name: str | Path = "test",
) -> pd.DataFrame:
    sum_tab = data[sum_column] if sum_column else data
    sum_tab = sum_tab.describe()

    # rename the columns
    sum_tab.rename(columns=ALL_NAMING_DICT, inplace=True)

    # transpose the summary table
    sum_tab = sum_tab.T

    # reformat count column to include thousands separator without decimal
    sum_tab["count"] = sum_tab["count"].apply(lambda x: f"{x:,.0f}")

    # generate the latex table for sum_tab
    sum_tab.to_latex(f"{file_name}.tex", escape=False)

    return sum_tab


if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(DATA_PATH / "processed" / "reg_panel_new.pkl")

    # generate the summary table
    res = render_summary_table_latex(
        file_name=TEST_RESULT_PATH / "test",
        data=regression_panel,
        sum_column=["Volume_share", "volume_in_share", "volume_out_share"],
    )
