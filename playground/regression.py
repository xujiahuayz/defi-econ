# get the regression panel dataset from pickled file
from itertools import product
from os import path

import pandas as pd
from environ.constants import TABLE_PATH
from linearmodels.panel import PanelOLS
from environ.utils.lags import lag_variable, name_lag_variable


def regress(
    data: pd.DataFrame,
    dependent_v: str = "Volume_share",
    independent_v: list[str] = ["is_boom", "mcap_share"],
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
    y = data[dependent_v]

    # Define the independent variables
    X = data[independent_v]

    # Run the fixed-effect regression
    model = PanelOLS(y, X, entity_effects=entity_effect, drop_absorbed=True).fit()
    return model


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
    iv_chunk_stable = [["Stable", "stableshare"]]
    iv_chunk_eth = [["corr_eth"], ["corr_sp"]]

    # lag all iv above
    iv_chunk_main = [list(map(name_lag_variable, iv)) for iv in iv_chunk_main]
    iv_chunk_stable = [list(map(name_lag_variable, iv)) for iv in iv_chunk_stable]
    iv_chunk_eth = [list(map(name_lag_variable, iv)) for iv in iv_chunk_eth]

    result_table = pd.DataFrame()
    for dv in dependent_variables:
        dv_lag = [[], [name_lag_variable(dv)]]
        for iv_combi in product(dv_lag, iv_chunk_main, iv_chunk_stable, iv_chunk_eth):
            iv = [x for y in iv_combi for x in y]
            regression_result = regress(
                data=reg_panel, dependent_v=dv, independent_v=iv
            )
            # merge three pd.Series: regression_result.params, regression_result.std_errors, regression_result.pvalues into one dataframe
            result_column = pd.Series()
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
                # add standard error
                v = f"${v}$^{star} \n ({regression_result.std_errors[i]:.3f})"
                result_column[i] = v

            result_column["$R^2$"] = "{:.3f}".format(regression_result.rsquared)
            result_column.to_frame(name=dv)
            # merge result_column into result_table
            result_table = pd.concat([result_table, result_column], axis=1)
