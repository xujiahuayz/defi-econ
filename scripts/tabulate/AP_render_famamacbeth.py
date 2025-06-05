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
    QUANTILES,
)
from environ.process.asset_pricing.assetpricing_functions import (
    clean_weekly_panel,
    univariate_sort,
    get_dominance_portfolios,
    reg_fama_macbeth,
)


if __name__ == "__main__":
    # compute means for portfolio returns (can change to median)
    ret_agg = "value_weight"
    is_boom = -1
    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )
    # load factors
    ff3 = pd.read_csv(PROCESSED_DATA_PATH / "FF3.csv")
    ltw3 = pd.read_csv(PROCESSED_DATA_PATH / "LTW3.csv")
    for dom_variable in DEPENDENT_VARIABLES_ASSETPRICING:
        quantiles = QUANTILES
        df_panel = clean_weekly_panel(reg_panel, is_stablecoin=0, is_boom=is_boom)
        df_panel = df_panel[df_panel[dom_variable] > 0]
        df_panel = univariate_sort(
            df_panel, dom_variable, quantiles, separate_zero_value=False
        )
        dominance_factor = get_dominance_portfolios(df_panel)
        dominance_factor.rename(
            columns={dominance_factor.columns[-1]: "CDOM"}, inplace=True
        )
        # Get the test assets
        assets_panel = clean_weekly_panel(reg_panel, is_stablecoin=0, is_boom=-1)

        # Calculate the mean market cap for each token
        mean_market_cap = assets_panel.groupby("Token")["mcap"].median()

        # Identify tokens that had a market cap above 1 million most of the time
        tokens_above_1m = mean_market_cap[mean_market_cap > 1e6].index

        # Filter the original DataFrame to keep only these tokens
        assets_panel = assets_panel[assets_panel["Token"].isin(tokens_above_1m)]

        # Merge all factors
        data_fama_macbeth = pd.merge(dominance_factor, ff3, on=["WeekYear"], how="left")
        data_fama_macbeth = pd.merge(
            data_fama_macbeth, ltw3, on=["WeekYear"], how="left"
        )
        # Merge factors with returns
        data_fama_macbeth = pd.merge(
            data_fama_macbeth, assets_panel, on=["WeekYear"], how="left"
        )
        data_fama_macbeth = data_fama_macbeth.dropna()

        # Run the Fama–MacBeth regression
        data_fama_macbeth["excess_ret"] = (
            data_fama_macbeth["ret"] - data_fama_macbeth["RF"]
        )
        fama_macbeth_results = reg_fama_macbeth(
            data_fama_macbeth, formula="excess_ret ~ CMKT + CMOM + CSIZE + CDOM"
        )
        fama_macbeth_results = fama_macbeth_results.round(3)
        fama_macbeth_results.drop("t_stat", axis=1, inplace=True)
        fama_macbeth_results.rename(
            columns={
                "factor": "Factor",
                "risk_premium": "Risk Premium",
                "t_stat_NW": r"\emph{t}",
            },
            inplace=True,
        )
        file_name = (
            TABLE_PATH / "assetpricing" / f"assetpricing_famamacbeth_{dom_variable}"
        )

        fama_macbeth_results.to_latex(
            f"{file_name}.tex",
            index=True,
            escape=False,
            float_format="%.3f",
        )
