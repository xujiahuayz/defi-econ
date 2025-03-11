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
    univariate_sort,
)


def render_unisort_table_latex(
    unisort_tab: pd.DataFrame,
    file_name: str | Path = "test",
) -> pd.DataFrame:

    # rename the columns
    unisort_tab.rename(columns=ALL_NAMING_DICT, inplace=True)

    # generate the latex table for unisort_tab
    unisort_tab.to_latex(
        f"{file_name}.tex",
        index=True,
        escape=False,
    )

    return unisort_tab


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
        print(f"Processing unisort for {dom_variable}")
        # clean data, which will be different for each dominant variable
        df_panel = clean_weekly_panel(
            regression_panel, dom_variable, is_stablecoin=0, is_boom=-1
        )

        # Substract risk free rate
        df_panel = pd.merge(df_panel, ff3, on="WeekYear")
        df_panel["ret"] = df_panel["ret"] - df_panel["RF"]

        # univariate sorting into portfolios
        summary_table = univariate_sort(
            df_panel, dom_variable, n_quantiles, ret_agg=ret_agg
        )

        # Compute the difference: H minus L
        pivot = df_panel.pivot_table(
            index="WeekYear", columns="portfolio", values="ret"
        )
        diff_returns = pivot[f"P{n_quantiles}"] - pivot["P1"]
        mean_diff = diff_returns.mean() if ret_agg == "mean" else diff_returns.median()
        std_diff = diff_returns.std(ddof=1)
        t_stat_diff, p_value_diff = ttest_1samp(diff_returns, popmean=0)

        summary_table[f"P{n_quantiles}-P1"] = {
            "Mean": mean_diff,
            "t-Stat": t_stat_diff,
            "StdDev": std_diff,
            "Sharpe": np.sqrt(365 / 7) * mean_diff / std_diff,
        }

        # generate the summary table
        table_name = "unisort_" + dom_variable
        res = render_unisort_table_latex(
            file_name=TABLE_PATH / "assetpricing" / table_name,
            unisort_tab=summary_table,
        )
