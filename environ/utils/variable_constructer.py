"""
This module contains functions to construct variables in preparation for regression.
"""

from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd

from environ.constants import ALL_NAMING_DICT


def name_lag_variable(variable: str, lag: int = 1) -> str:
    """
    name the lag variable
    """
    return f"{variable}_lag_{lag}"


def name_interaction_variable(variable1: str, variable2: str) -> str:
    """
    name the interaction variable
    """
    return f"{variable1}*{variable2}"


def name_diff_variable(variable: str, lag: int = 1) -> str:
    """
    name the difference variable
    """
    return f"{variable}_diff_{lag}"


def name_log_return_variable(variable: str, rolling_window_return: int) -> str:
    """
    name the log return variable
    """
    return f"{variable}_log_return_{rolling_window_return}"


def name_ma_variable(variable: str, rolling_window_ma: int) -> str:
    """
    name the moving average variable
    """
    return f"{variable}_ma_{rolling_window_ma}"


def name_log_return_vol_variable(
    variable: str, rolling_window_return: int, rolling_window_vol: int
) -> str:
    """
    name the log return vol variable
    """
    return f"{variable}_log_return_vol_{rolling_window_return}_{rolling_window_vol}"


def name_share_variable(variable: str) -> str:
    """
    name the share variable
    """
    return f"{variable}_share"


def map_variable_name_latex(variable: str) -> str:
    """
    Map the variable name to its corresponding LaTeX representation.

    Args:
        variable (str): The variable name to be mapped.

    Returns:
        str: The LaTeX representation of the variable name.
    """

    def format_variable(var: str) -> str:
        """Format the given variable to its LaTeX representation."""
        if var in ALL_NAMING_DICT:
            return ALL_NAMING_DICT[var]

        has_lag = "_lag_" in var
        if has_lag:
            var, lag = var.split("_lag_")
            if var in ALL_NAMING_DICT:
                return f"{ALL_NAMING_DICT.get(var, var)}_{{t-{lag}}}"

        if "_diff_" in var:
            var, diff = var.split("_diff_")
            var = ALL_NAMING_DICT.get(var, var)
            var = f"\\Delta^{{{diff if diff != '1' else ''}}} {var}"

        if has_lag:
            var = f"{var}_{{t-{lag}}}"

        return var

    # Split the variable name by * for interaction variable
    variables = variable.split("*")

    # Format each variable
    formatted_variables = [format_variable(var) for var in variables]

    # Combine all with ":" for interaction variables, accommodating for the case of 3 variables
    return f'${":".join(formatted_variables)}$'


def column_manipulator(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    summary_func: Callable[[pd.Series], Any],
    new_col_name_func: Callable[[str], str],
    time_variable: str = "Date",
    group_variable: str | None = None,
) -> pd.DataFrame:
    """
    Manipulate the columns of a dataframe.
    """
    data = data.sort_values(by=time_variable)

    # Group by entity_variable if it is provided, otherwise use the whole panel_data as a group
    grouped_df = data.groupby(group_variable) if group_variable else data

    if isinstance(variable, str):
        variable = [variable]

    for var in variable:
        data[new_col_name_func(var)] = grouped_df[var].transform(summary_func)
    return data


def diff_variable_columns(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    time_variable: str = "Date",
    entity_variable: str | None = None,
    lag: int = 1,
) -> pd.DataFrame:
    """
    Take the difference of the variable by lag periods.
    """

    return column_manipulator(
        data=data,
        variable=variable,
        summary_func=lambda x: x.diff(lag),
        new_col_name_func=lambda x: name_diff_variable(x, lag=lag),
        time_variable=time_variable,
        group_variable=entity_variable,
    )


def lag_variable_columns(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    time_variable: str = "Date",
    entity_variable: str | None = None,
    lag: int = 1,
) -> pd.DataFrame:
    """
    Lag the variable by lag periods.
    """

    return column_manipulator(
        data=data,
        variable=variable,
        summary_func=lambda x: x.shift(lag),
        new_col_name_func=lambda x: name_lag_variable(x, lag=lag),
        time_variable=time_variable,
        group_variable=entity_variable,
    )


def share_variable_columns(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    time_variable: str = "Date",
    entity_variable: str | None = "Date",
) -> pd.DataFrame:
    """
    Calculate the share of the variable.
    """

    return column_manipulator(
        data=data,
        variable=variable,
        summary_func=lambda x: x / x.sum(),
        new_col_name_func=name_share_variable,
        time_variable=time_variable,
        group_variable=entity_variable,
    )


def ma_variable_columns(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    time_variable: str = "Date",
    entity_variable: str | None = None,
    rolling_window_ma: int = 1,
) -> pd.DataFrame:
    """
    Calculate the moving average of the variable.
    """

    return column_manipulator(
        data=data,
        variable=variable,
        summary_func=lambda x: x.rolling(rolling_window_ma).mean(),
        new_col_name_func=lambda x: name_ma_variable(
            x, rolling_window_ma=rolling_window_ma
        ),
        time_variable=time_variable,
        group_variable=entity_variable,
    )


def log_return(
    data: pd.DataFrame,
    variable: str | Iterable[str],
    time_variable: str = "Date",
    rolling_window_return: int = 1,
) -> pd.DataFrame:
    """
    Calculate the log return of the variable.
    """

    data = data.sort_values(by=time_variable)

    data = data.set_index(time_variable).resample("D").asfreq().reset_index()

    if isinstance(variable, str):
        variable = [variable]

    for var in variable:
        # fill the missing values with the previous value with linear interpolation
        data[var].fillna(method="ffill", inplace=True)

        # handle 0
        # first replace 0 with nan
        data[var].replace(0, np.nan, inplace=True)
        # impute all na with the previous value
        data[var] = data[var].interpolate(method="linear")

        data[name_log_return_variable(var, rolling_window_return)] = np.log(
            data[var] / data[var].shift(rolling_window_return)
        )
    return data


def return_vol(
    data: pd.DataFrame,
    variable: str,
    rolling_window_return: int = 1,
    rolling_window_vol: int = 4,
) -> pd.DataFrame:
    """
    Calculate the volatility of the variable.
    """
    data[
        name_log_return_vol_variable(
            variable, rolling_window_return, rolling_window_vol
        )
    ] = (
        data[name_log_return_variable(variable, rolling_window_return)]
        .rolling(rolling_window_vol)
        .std()
    )
    return data


def log_return_panel(
    data: pd.DataFrame,
    variable: str,
    output_variable: str,
    entity_variable: str = "Token",
    time_variable: str = "Date",
    rolling_window_return: int = 1,
) -> pd.DataFrame:
    """
    Calculate the log return of the panel variable
    """

    data = data.sort_values(by=time_variable, ascending=True)

    # # fill the missing values with the previous value with linear interpolation
    # data[variable] = data.groupby(entity_variable)[variable].fillna(method="ffill")

    # handle 0
    # first replace 0 with nan
    data[variable].replace(0, np.nan, inplace=True)

    # data.groupby(variable).apply(lambda group: group.interpolate(method="linear"))

    data[output_variable] = data.groupby(entity_variable)[variable].transform(
        lambda x: np.log(x / x.shift(rolling_window_return))
    )

    return data


def return_vol_panel(
    data: pd.DataFrame,
    variable: str,
    output_variable: str,
    entity_variable: str = "Token",
    time_variable: str = "Date",
    rolling_window_vol: int = 4,
) -> pd.DataFrame:
    """
    Calculate the volatility of the variable.
    """

    # sort the data by "Token" and "Date
    data = data.sort_values(by=[entity_variable, time_variable])

    data[output_variable] = (
        data.groupby(entity_variable)[variable]
        .rolling(rolling_window_vol)
        .std()
        .reset_index(0, drop=True)
    )

    return data


if __name__ == "__main__":
    # create a dummy dataset
    # dummy_data = pd.DataFrame(
    #     {
    #         "Date": pd.date_range("2020-01-01", "2020-01-20").append(
    #             pd.date_range("2020-02-01", "2020-02-10")
    #         ),
    #         "price1": [1, 2, 0, 4, 5, 6, 0, 0, 9, 10] * 3,
    #         "price2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1] * 3,
    #     }
    # )

    # new_data = log_return(dummy_data, "price1", "Date", 2)
    # new_data = return_vol(new_data, "price1", 2, 6)
    # var_name = name_interaction_variable(
    #     name_interaction_variable(
    #         name_log_return_vol_variable("price1", 2, 6), name_lag_variable("price2", 1)
    #     ),
    #     name_lag_variable("price2", 2),
    # )
    # map_variable_name_latex(variable=var_name)

    # create a dummy panel dataset
    dummy_data_panel = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", "2020-01-20").append(
                pd.date_range("2020-02-01", "2020-02-10")
            ),
            "price1": [1, 3, 0, 1, 1, 1, 0, 0, 1, np.nan] * 3,
            "price2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1] * 3,
            "entity": ["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"] * 3,
        }
    )

    print(
        log_return_panel(dummy_data_panel, "price1", "log_return", "entity", "Date", 1)
    )
