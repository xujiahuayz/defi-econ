# get the regression panel dataset from pickled file
from itertools import product
from os import path

import pandas as pd
from environ.constants import NAMING_DICT, TABLE_PATH, NAMING_DICT_LAG, ALL_NAMING_DICT
from linearmodels.panel import PanelOLS
from environ.utils.lags import lag_variable, name_lag_variable

REGRESSION_NAMING_DICT = {
    "r2": "$R^2$",
    "r2_within": "$R^2_{within}$",
    "nobs": "N",
    "fe": "\midrule fixed effect",
    "regressand": "Regressand",
}


def regress(
    data: pd.DataFrame,
    dv: str = "Volume_share",
    iv: list[str] = ["is_boom", "mcap_share"],
    entity_effect: bool = True,
):
    """
    Run the fixed-effect regression.

    Args:
        data (pd.DataFrame): The dataset.
        iv (str, optional): The name of the independent variable. Defaults to "Volume_share".
        dv (list[str], optional): The name of the dependent variables. Defaults to ["is_boom", "mcap_share"].
    """
    # Define the dependent variable
    y = data[dv]

    # Define the independent variables
    X = data[iv]

    # Run the fixed-effect regression
    # catch error and print y and X
    model = PanelOLS(
        y, X, entity_effects=entity_effect, drop_absorbed=True, check_rank=False
    ).fit()
    return model


def render_regression_column(
    reg_panel: pd.DataFrame, dv: str, iv: list[str], entity_effect: bool = True
) -> pd.Series:
    regression_result = regress(
        data=reg_panel, dv=dv, iv=iv, entity_effect=entity_effect
    )
    # merge three pd.Series: regression_result.params, regression_result.std_errors, regression_result.pvalues into one dataframe
    result_column = pd.Series({"regressand": dv})
    for i, v in regression_result.params.items():
        # format v to exactly 3 decimal places
        v = "{:.3f}".format(v)
        # add * according to p-value
        if regression_result.pvalues[i] < 0.01:
            star = "**"
        elif regression_result.pvalues[i] < 0.05:
            star = "*"
        else:
            star = ""
        star = "{" + star + "}"
        # add standard error
        line1 = f"${v}^{star}$"
        line2 = f"({regression_result.std_errors[i]:.3f})"

        v = "\makecell{" + line1 + " \\\\" + line2 + "}"
        result_column[i] = v

    result_column["fe"] = "yes" if entity_effect else "no"
    # number of observations with thousands separator
    result_column["nobs"] = "{:,}".format(regression_result.nobs)
    result_column["r2"] = "{:.3f}".format(regression_result.rsquared)
    # add within r2
    result_column["r2_within"] = "{:.3f}".format(regression_result.rsquared_within)
    return result_column


if __name__ == "__main__":

    # Get the regression panel dataset from pickled file
    reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))

    # Lag all variable except the Date and Token
    for variable in reg_panel.columns:
        if variable not in ["Date", "Token"]:
            reg_panel = lag_variable(reg_panel, variable, "Date", "Token")

    dependent_variables = [
        "avg_eigenvector_centrality",
        "betweenness_centrality_volume",
        "betweenness_centrality_count",
        "Volume_share",
    ]

    iv_chunk_main = [["std", "corr_gas", "mcap_share", "Supply_share"]]
    iv_chunk_eth = [["corr_eth"], ["corr_sp"]]

    # lag all iv above
    iv_chunk_main = [list(map(name_lag_variable, iv)) for iv in iv_chunk_main]
    iv_chunk_eth = [list(map(name_lag_variable, iv)) for iv in iv_chunk_eth]
    iv_chunk_stable = [["Stable", name_lag_variable("stableshare")]]
    LAG_DV_NAME = "$\it Dominance_{t-1}$"

    # flatten all possible iv
    all_ivs = iv_chunk_main + iv_chunk_stable + iv_chunk_eth

    result_table = pd.DataFrame()
    counter = 0
    for dv in dependent_variables:
        lag_dv_name = name_lag_variable(dv)
        dv_lag = [[], [lag_dv_name]]
        for iv_combi in product(dv_lag, iv_chunk_main, iv_chunk_stable, iv_chunk_eth):
            iv = [x for y in iv_combi for x in y]
            result_column = render_regression_column(
                reg_panel,
                dv,
                iv,
                entity_effect=True
                # False if "Stable" in iv else True
            )
            # rename result_column index
            result_column = result_column.rename(
                index={
                    lag_dv_name: LAG_DV_NAME,
                }
            )
            result_column["regressand"] = ALL_NAMING_DICT[dv]

            counter += 1
            result_column_df = result_column.to_frame(name=f"({counter})")

            # merge result_column into result_table, keep  name as column name
            result_table = pd.concat([result_table, result_column_df], axis=1)

    # replace all na with empty string
    result_table_raw = result_table.fillna("")

    # reorder rows in result_table
    result_table_fine = result_table_raw.reindex(
        [
            "regressand",
            LAG_DV_NAME,
        ]
        + [x for y in all_ivs for x in y]
        + [
            "fe",
            "nobs",
            "r2",
            "r2_within",
        ]
    )

    # rename result_table index with REGRESSION_NAMING_DICT and NAMING_DICT_LAG and NAMING_DICT combined
    result_table_fine = result_table_fine.rename(index=REGRESSION_NAMING_DICT).rename(
        index=ALL_NAMING_DICT
    )

    # transform result_table to latex table
    result_table_fine.to_latex(
        path.join(TABLE_PATH, "regression_table.tex"), escape=False
    )
