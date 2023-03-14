# get the regression panel dataset from pickled file
from itertools import product
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

from environ.constants import ALL_NAMING_DICT, TABLE_PATH
from environ.utils.variable_constructer import lag_variable, name_lag_variable

REGRESSION_NAMING_DICT = {
    "r2": "$R^2$",
    "r2_within": "$R^2_{within}$",
    "nobs": "N",
    "fe": "fixed effect",
    "regressand": "Regressand",
}


def fix_effect(iv: list[str]) -> bool:
    """
    Check whether the fixed-effect regression should be run.

    Args:
        iv (list[str]): The independent variables.

    Returns:
        bool: Whether the fixed-effect regression should be run.
    """
    return False if "Stable" in iv else True


def regress(
    data: pd.DataFrame,
    dv: str = "Volume_share",
    iv: list[str] = ["is_boom", "mcap_share"],
    # method can be "ols", or "panel"
    method: str = "panel",
):
    """
    Run the fixed-effect regression.

    Args:
        data (pd.DataFrame): The data to run the regression on.
        dv (str, optional): The dependent variable. Defaults to "Volume_share".
        iv (list[str], optional): The independent variables. Defaults to ["is_boom", "mcap_share"].
        entity_effect (bool, optional): Whether to include entity effect. Defaults to True.
    """
    # Define the dependent variable
    dependent_var = data[dv]

    # Define the independent variables
    independent_var = data[iv]

    # Run the fixed-effect regression
    # catch error and print y and X
    if method == "panel":
        model = PanelOLS(
            dependent_var,
            independent_var,
            entity_effects=fix_effect(iv),
            drop_absorbed=True,
            check_rank=False,
        ).fit()
    elif method == "ols":
        model = sm.OLS(dependent_var, independent_var, missing="drop").fit()
    else:
        raise ValueError(f"method {method} must be either 'ols' or 'panel'")
    return model


def render_regression_column(
    data: pd.DataFrame,
    dv: str,
    iv: list[str],
    method: str = "panel",
    standard_beta: bool = False,
) -> pd.Series:
    """
    Render the regression column.

    Args:
        reg_panel (pd.DataFrame): The data to run the regression on.
        dv (str): The dependent variable.
        iv (list[str]): The independent variables.
        method (str, optional): The method to run the regression. Defaults to "panel".
        standard_beta (bool, optional): Whether to use standard beta. Defaults to False.

    Returns:
        pd.Series: The regression column.
    """
    regression_result = regress(data=data, dv=dv, iv=iv, method=method)

    # merge three pd.Series: regression_result.params, regression_result.std_errors, regression_result.pvalues into one dataframe
    result_column = pd.Series({"regressand": dv})
    if standard_beta:
        # calculate the standard deviation of [dv] + iv
        line2_items = data[iv].std() / data[dv].std()
    else:
        line2_items = (
            regression_result.std_errors if method == "panel" else regression_result.bse
        )

    for i, v in regression_result.params.items():
        # format v to exactly 3 decimal places
        beta = "{:.3f}".format(v)
        # add * according to p-value
        pvalue = regression_result.pvalues[i]
        star = f"{{{'***' if pvalue < 0.01 else '**' if pvalue < 0.05 else '*' if pvalue < 0.1 else ''}}}"
        # add standard error
        line1 = f"${beta}^{star}$"
        line2 = f"(${line2_items[i] * v**standard_beta :.3f}$)"

        result_column[i] = rf"{line1} \\ {line2}"

    if method == "panel":
        result_column["fe"] = "yes" if fix_effect(iv) else "no"
    # number of observations with thousands separator and without decimal places
    result_column["nobs"] = f"{regression_result.nobs:,.0f}"
    result_column["r2"] = f"{regression_result.rsquared:.3f}"
    return result_column


def construct_regress_vars(
    dependent_variables: list[str],
    iv_chunk_list: list[list[list[str]]],
    lag_iv: bool = False,
    with_lag_dv: bool = True,
    without_lag_dv: bool = False,
) -> list[tuple[str, list[str]]]:
    """
    Construct the regressand and independent variables.

    Args:
        dependent_variables (list[str]): The dependent variables.
        iv_chunk_list (list[list[list[str]]]): The independent variables.
        lag_iv (bool, optional): Whether to lag the independent variables. Defaults to False.
        with_lag_dv (bool, optional): Whether to include the lagged dependent variable. Defaults to True.
        without_lag_dv (bool, optional): Whether to include the dependent variable without lag. Defaults to False.

    Returns:
        list[tuple[str, list[str]]]: The list of regressand and independent variables.
    """
    if lag_iv:
        # lag all iv above
        iv_chunk_list = [
            [
                [
                    name_lag_variable(v)
                    if v not in ["Stable", "is_boom", "const"]
                    and v in list(ALL_NAMING_DICT.keys())
                    else v
                    for v in iv
                ]
                for iv in iv_chunk
            ]
            for iv_chunk in iv_chunk_list
        ]
    without_lag_dv_part = [[]] if without_lag_dv else []
    return [
        (dv, [x for y in iv_combi for x in y])
        for dv in dependent_variables
        for iv_combi in product(
            *(
                [
                    [([name_lag_variable(dv)] if with_lag_dv else [])]
                    + without_lag_dv_part
                ]
                + iv_chunk_list
            )
        )
    ]


def render_regress_table(
    reg_panel: pd.DataFrame,
    reg_combi: list[tuple[str, list[str]]],
    lag_dv: str = "$\it Dominance_{t-1}$",
    **kargs,
    # method: str = "panel",
) -> pd.DataFrame:
    """
    Render the regression table.

    Args:
        reg_panel (pd.DataFrame): The data to run the regression on.
        file_name (str): The file suffix of the regression table in latex.
        reg_combi (list[tuple[str, list[str]]]): The list of regressand and independent variables.
        lag_dv (str, optional): The name of the lagged dependent variable. Defaults to "$\it Dominance_{t-1}$".

    Returns:
        pd.DataFrame: The regression table.
    """

    result_table = pd.DataFrame()
    counter = 0
    # initiate all_ivs set
    all_ivs = []
    for dv, ivs in reg_combi:
        lag_dv_name = name_lag_variable(dv)
        result_column = render_regression_column(
            reg_panel,
            dv,
            ivs,
            **kargs,
        )
        # rename result_column index
        result_column = result_column.rename(
            index={
                lag_dv_name: lag_dv,
            }
        )
        result_column["regressand"] = dv

        counter += 1
        result_column_df = result_column.to_frame(name=f"({counter})")

        # merge result_column into result_table, keep  name as column name
        result_table = result_table.join(result_column_df, how="outer")
        # add iv elements to all_ivs
        all_ivs.extend([x for x in ivs if x not in all_ivs])

    # reorder rows in result_table, include only rows in index already

    rows = [
        x
        for x in (
            [
                "regressand",
                lag_dv,
            ]
            + all_ivs
            + [
                "fe",
                "nobs",
                "r2",
            ]
        )
        if x in result_table.index
    ]
    result_table_fine = result_table.reindex(rows).fillna("")
    return result_table_fine


def render_regress_table_latex(
    result_table: pd.DataFrame, file_name: str = "test", method: str = "panel"
) -> pd.DataFrame:
    """
    Render the regression table in latex.
    """

    result_table_latex = result_table.rename(index=ALL_NAMING_DICT)
    # rename each cell in the "regressand" row with ALL_NAMING_DICT[xxx]
    result_table_latex.loc["regressand"] = result_table_latex.loc["regressand"].map(
        ALL_NAMING_DICT
    )
    result_table_latex.rename(index=REGRESSION_NAMING_DICT, inplace=True)

    iv_end = -3 if method == "panel" else -2
    # for each cell from row 2 to 4th last row, add \makecell{xx} to make the cell wrap
    for row in result_table_latex.index[1:iv_end]:
        for col in result_table_latex.columns:
            result_table_latex.loc[
                row, col
            ] = f"\\makecell{{{result_table_latex.loc[row, col]}}}"
    # add \midrule to the 4th last row
    original_index = result_table_latex.index[iv_end]
    result_table_latex = result_table_latex.rename(
        index={original_index: f"\\midrule {original_index}"}
    )
    result_table_latex.to_latex(
        Path(TABLE_PATH) / f"regression_table_{file_name}.tex", escape=False
    )
    return result_table_latex


if __name__ == "__main__":

    # Get the regression panel dataset from pickled file
    reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # Lag all variable except the Date and Token
    for variable in reg_panel.columns:
        if variable not in ["Date", "Token"]:
            reg_panel = lag_variable(reg_panel, variable, "Date", "Token")

    reg_combi = construct_regress_vars(
        dependent_variables=["Volume_share", "avg_eigenvector_centrality"],
        iv_chunk_list=[[["corr_eth"]], [["Stable"], ["std", "Stable"]]],
        lag_iv=True,
        with_lag_dv=False,
        without_lag_dv=False,
    )

    result_full = render_regress_table(
        reg_panel=reg_panel,
        reg_combi=reg_combi,
        method="panel",
        standard_beta=True,
    )
    result_in_latex = render_regress_table_latex(
        result_table=result_full, file_name="test"
    )
    # test one column
    result_one_column = render_regression_column(
        data=reg_panel,
        dv=reg_combi[0][0],
        iv=reg_combi[0][1],
        method="panel",
        standard_beta=True,
    )
