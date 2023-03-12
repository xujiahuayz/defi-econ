# get the regression panel dataset from pickled file
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS

from environ.constants import ALL_NAMING_DICT, TABLE_PATH
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
    dependent_var = data[dv]

    # Define the independent variables
    independent_var = data[iv]

    # Run the fixed-effect regression
    # catch error and print y and X
    model = PanelOLS(
        dependent_var,
        independent_var,
        entity_effects=entity_effect,
        drop_absorbed=True,
        check_rank=False,
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
        pvalue = regression_result.pvalues[i]
        star = f"{{{'***' if pvalue < 0.01 else '**' if pvalue < 0.05 else '*' if pvalue < 0.1 else ''}}}"
        # add standard error
        line1 = f"${v}^{star}$"
        line2 = f"({regression_result.std_errors[i]:.3f})"

        v = "\makecell{" + line1 + " \\\\" + line2 + "}"
        result_column[i] = v

    result_column["fe"] = "yes" if entity_effect else "no"
    # number of observations with thousands separator
    result_column["nobs"] = f"{regression_result.nobs:,}"
    result_column["r2"] = f"{regression_result.rsquared:.3f}"
    # add within r2
    result_column["r2_within"] = f"{regression_result.rsquared_within:.3f}"
    return result_column


def render_regress_table(
    reg_panel: pd.DataFrame,
    file_name: str,
    reg_combi: list[tuple[str, list[str]]],
    lag_dv: str = "$\it Dominance_{t-1}$",
) -> pd.DataFrame:

    result_table = pd.DataFrame()
    counter = 0
    # initiate all_ivs set
    all_ivs = set()
    for reg_spec in reg_combi:
        dv = reg_spec[0]
        iv = reg_spec[1]
        lag_dv_name = name_lag_variable(dv)
        result_column = render_regression_column(
            reg_panel, dv, iv, entity_effect=False if "Stable" in iv else True
        )
        # rename result_column index
        result_column = result_column.rename(
            index={
                lag_dv_name: lag_dv,
            }
        )
        result_column["regressand"] = ALL_NAMING_DICT[dv]

        counter += 1
        result_column_df = result_column.to_frame(name=f"({counter})")

        # merge result_column into result_table, keep  name as column name
        result_table = result_table.join(result_column_df, how="outer")
        # add iv elements to all_ivs
        all_ivs.update(iv)

    # reorder rows in result_table, include only rows in index already

    rows = [
        x
        for x in (
            [
                "regressand",
                lag_dv,
            ]
            + [x for x in all_ivs]
            + [
                "fe",
                "nobs",
                "r2",
            ]
        )
        if x in result_table.index
    ]
    result_table_fine = result_table.reindex(rows).fillna("")

    # rename result_table index with REGRESSION_NAMING_DICT and NAMING_DICT_LAG and NAMING_DICT combined
    result_table_fine = result_table_fine.rename(index=REGRESSION_NAMING_DICT).rename(
        index=ALL_NAMING_DICT
    )

    # transform result_table to latex table
    result_table_fine.to_latex(
        Path(TABLE_PATH) / f"regression_table_{file_name}.tex", escape=False
    )
    return result_table_fine


if __name__ == "__main__":

    # Get the regression panel dataset from pickled file
    reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # Lag all variable except the Date and Token
    for variable in reg_panel.columns:
        if variable not in ["Date", "Token"]:
            reg_panel = lag_variable(reg_panel, variable, "Date", "Token")

    result_full = render_regress_table(
        reg_panel=reg_panel,
        file_name="full",
        reg_combi=[("Volume_share", ["corr_eth", "std"]), ("Volume_share", ["std"])],
    )
