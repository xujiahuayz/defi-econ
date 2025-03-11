"""
Script to render the table of Fama Macbeth.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp
from environ.constants import (
    ALL_NAMING_DICT,
    DEPENDENT_VARIABLES_ASSETPRICING,
    PROCESSED_DATA_PATH,
    TABLE_PATH,
)
from environ.process.asset_pricing.assetpricing_functions import (
    clean_weekly_panel,
    double_sort,
)


def render_doublesort_table_latex(
    doublesort_tab: pd.DataFrame,
    file_name: str | Path = "test",
) -> pd.DataFrame:

    # rename the columns
    doublesort_tab.rename(columns=ALL_NAMING_DICT, inplace=True)

    # generate the latex table for doublesort_tab
    doublesort_tab.to_latex(
        f"{file_name}.tex",
        index=True,
        escape=False,
    )

    return doublesort_tab


if __name__ == "__main__":

    ret_agg = "mean"  # compute means for portfolio returns (can change to median)
    n_quantiles = 3  # number of portfolios

    # load factors
    ff3 = pd.read_csv(PROCESSED_DATA_PATH / "FF3.csv")

    # load the regression panel dataset
    regression_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )

    for dom_variable in DEPENDENT_VARIABLES_ASSETPRICING:
        print(f"Processing doublesort for {dom_variable}")
        # clean data, which will be different for each dominant variable
        df_panel = clean_weekly_panel(
            regression_panel, dom_variable, is_stablecoin=0, is_boom=-1
        )

        # Substract risk free rate
        df_panel = pd.merge(df_panel, ff3, on="WeekYear")
        df_panel["ret"] = df_panel["ret"] - df_panel["RF"]

        # doublevariate sorting into portfolios
        summary_table = double_sort(
            df_panel,
            dom_variable,
            secondary_variable="mcap",
            n_quantiles=n_quantiles,
            ret_agg=ret_agg,
        )

        # generate the summary table
        table_name = "doublesort_" + dom_variable
        res = render_doublesort_table_latex(
            file_name=TABLE_PATH / "assetpricing" / table_name,
            doublesort_tab=summary_table,
        )
