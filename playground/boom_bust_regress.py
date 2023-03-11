# get the regression panel dataset from pickled file
from itertools import product
from os import path

import pandas as pd
from playground.regression import (
    REGRESSION_NAMING_DICT,
    render_regression_column,
)
from environ.constants import TABLE_PATH, ALL_NAMING_DICT
from environ.utils.lags import lag_variable, name_lag_variable

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
iv_chunk_stable = [
    ["Stable", name_lag_variable("depeg_pers")],
    [name_lag_variable("stableshare")],
]
LAG_DV_NAME = "$\it Dominance_{t-1}$"

# flatten all possible iv
all_ivs = iv_chunk_main + iv_chunk_stable + iv_chunk_eth


def boom_bust_regress(reg_panel: pd.DataFrame, file_name: str) -> pd.DataFrame:

    result_table = pd.DataFrame()
    counter = 0
    for dv in dependent_variables:
        lag_dv_name = name_lag_variable(dv)
        dv_lag = [[], [lag_dv_name]]
        for iv_combi in product(dv_lag, iv_chunk_main, iv_chunk_stable, iv_chunk_eth):
            iv = [x for y in iv_combi for x in y]
            result_column = render_regression_column(
                reg_panel, dv, iv, entity_effect=False if "Stable" in iv else True
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
        ]
    )

    # rename result_table index with REGRESSION_NAMING_DICT and NAMING_DICT_LAG and NAMING_DICT combined
    result_table_fine = result_table_fine.rename(index=REGRESSION_NAMING_DICT).rename(
        index=ALL_NAMING_DICT
    )

    # transform result_table to latex table
    result_table_fine.to_latex(
        path.join(TABLE_PATH, f"regression_table_{file_name}.tex"), escape=False
    )
    return result_table_fine


if __name__ == "__main__":

    # Get the regression panel dataset from pickled file
    reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))

    # Lag all variable except the Date and Token
    for variable in reg_panel.columns:
        if variable not in ["Date", "Token"]:
            reg_panel = lag_variable(reg_panel, variable, "Date", "Token")

    result_full = boom_bust_regress(reg_panel, "full")
    result_bust = boom_bust_regress(reg_panel[reg_panel["is_boom"] != True], "bust")
    result_boom = boom_bust_regress(reg_panel[reg_panel["is_boom"] == True], "boom")
