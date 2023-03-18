"""
This module contains functions to construct variables in preparation for regression.
"""

from typing import Any, Callable, Iterable, Optional, Union

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


def name_log_return_vol_variable(
    variable: str, rolling_window_return: int, rolling_window_vol: int
) -> str:
    """
    name the log return vol variable
    """
    return f"{variable}_log_return_vol_{rolling_window_return}_{rolling_window_vol}"


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
    variable: Union[str, Iterable[str]],
    summary_func: Callable[[pd.Series], Any],
    new_col_name_func: Callable[[str], str],
    time_variable: str = "Date",
    entity_variable: Optional[str] = None,
) -> pd.DataFrame:
    """
    Manipulate the columns of a dataframe.
    """
    data = data.sort_values(by=time_variable)

    # Group by entity_variable if it is provided, otherwise use the whole panel_data as a group
    groupby = data.groupby(entity_variable) if entity_variable else data

    if isinstance(variable, str):
        variable = [variable]

    for var in variable:
        data[new_col_name_func(var)] = groupby[var].transform(summary_func)
    return data


def diff_variable(
    data: pd.DataFrame,
    variable: Union[str, Iterable[str]],
    time_variable: str = "Date",
    entity_variable: Optional[str] = None,
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
        entity_variable=entity_variable,
    )


def lag_variable(
    data: pd.DataFrame,
    variable: Union[str, Iterable[str]],
    time_variable: str = "Date",
    entity_variable: Optional[str] = None,
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
        entity_variable=entity_variable,
    )


def log_return(
    data: pd.DataFrame,
    variable: Union[str, Iterable[str]],
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


if __name__ == "__main__":
    # create a dummy dataset
    dummy_data = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", "2020-01-20").append(
                pd.date_range("2020-02-01", "2020-02-10")
            ),
            "price1": [1, 2, 0, 4, 5, 6, 0, 0, 9, 10] * 3,
            "price2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1] * 3,
        }
    )

    new_data = log_return(dummy_data, "price1", "Date", 2)
    new_data = return_vol(new_data, "price1", 2, 6)
    var_name = name_interaction_variable(
        name_interaction_variable(
            name_log_return_vol_variable("price1", 2, 6), name_lag_variable("price2", 1)
        ),
        name_lag_variable("price2", 2),
    )
    map_variable_name_latex(variable=var_name)
