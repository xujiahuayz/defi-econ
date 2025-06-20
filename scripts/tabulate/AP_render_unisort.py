"""
Script to render unisort.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp
from environ.constants import (
    ALL_NAMING_DICT,
    DEPENDENT_VARIABLES,
    DEPENDENT_VARIABLES_ASSETPRICING,
    PROCESSED_DATA_PATH,
    TABLE_PATH,
    QUANTILES,
)
from environ.process.asset_pricing.assetpricing_functions import (
    clean_weekly_panel,
    univariate_sort,
    univariate_sort_table,
)


def render_unisort_table_latex(
    unisort_tab: pd.DataFrame,
    file_name: str | Path = "test",
) -> pd.DataFrame:

    # generate the latex table for unisort_tab
    unisort_tab.to_latex(
        f"{file_name}.tex",
        index=True,
        header=True,
        # Some options that help remove extra lines
        longtable=False,
        caption="",
        label="",
        float_format="%.4f",
        # "escape=False" if you have special LaTeX chars in your data
    )
    return


if __name__ == "__main__":
    # compute means for portfolio returns (can change to median)
    ret_agg = "value_weight"

    # load factors
    ff3 = pd.read_csv(PROCESSED_DATA_PATH / "FF3.csv")

    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main2.pickle.zip", compression="zip"
    )

    for dom_variable in DEPENDENT_VARIABLES:
        for is_boom in [-1, 0, 1]:
            for annualized in [False, True]:
                print(f"Processing unisort for {dom_variable}")
                quantiles = QUANTILES
                df_panel = clean_weekly_panel(
                    reg_panel, is_stablecoin=0, is_boom=is_boom
                )
                df_panel = df_panel[df_panel[dom_variable] > 0]
                # Substract risk free rate
                df_panel = pd.merge(df_panel, ff3, on="WeekYear")
                df_panel["ret_lead_1"] = df_panel["ret_lead_1"] - df_panel["RF"]

                df_panel = univariate_sort(
                    df_panel,
                    dom_variable,
                    quantiles=quantiles,
                    separate_zero_value=False,
                )
                summary_table = univariate_sort_table(
                    df_panel, ret_agg=ret_agg, annualized=annualized
                )
                summary_table = summary_table.round(4)

                # generate the summary table
                table_name = "unisort_" + dom_variable
                table_name += (
                    "_boom"
                    if is_boom == 1
                    else "_bust" if is_boom == 0 else "_allperiods"
                )
                table_name += "_annualized" if annualized == True else "_notannualized"
                res = render_unisort_table_latex(
                    file_name=TABLE_PATH / "assetpricing" / table_name,
                    unisort_tab=summary_table,
                )
