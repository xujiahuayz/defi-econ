from typing import Union
import numpy as np
import pandas as pd

from environ.constants import ALL_NAMING_DICT


def name_lag_variable(variable: str, lag: int = 1) -> str:
    """
    Name the lagged variable.

    Args:
        variable (str): The name of the variable.

    Returns:
        str: The name of the lagged variable.
    """
    return f"{variable}_lag_{lag}"


def name_interaction_variable(variable1: str, variable2: str) -> str:
    """
    Name the interaction variable.

    Args:
        variable1 (str): The name of the first variable.
        variable2 (str): The name of the second variable.

    Returns:
        str: The name of the interaction variable.
    """
    return f"{variable1}*{variable2}"


def map_variable_name_latex(variable: str) -> str:
    """
    map the variable name to latex.
    """

    # split the variable name by * for interaction variable
    variables = variable.split("*")
    # check lag for each variable
    for i, var in enumerate(variables):
        if "_lag_" in var:
            var, lag = var.split("_lag_")
            var = ALL_NAMING_DICT[var] if var in ALL_NAMING_DICT else var
            variables[i] = f"{var}_{{t-{lag}}}"
        else:
            variables[i] = ALL_NAMING_DICT[var] if var in ALL_NAMING_DICT else var

    # combine all with ":" for interaction variables, accommodating for the case of 3 variables
    return f'${":".join(variables)}$'


def name_log_return_variable(variable: str, rolling_window_return: int) -> str:
    return f"{variable}_log_return_{rolling_window_return}"


def name_log_return_vol_variable(
    variable: str, rolling_window_return: int, rolling_window_vol: int
) -> str:
    return f"{variable}_log_return_vol_{rolling_window_return}_{rolling_window_vol}"


def lag_variable(
    data: pd.DataFrame,
    variable: Union[str, list[str]],
    time_variable: str,
    entity_variable: str = "",
    lag: int = 1,
) -> pd.DataFrame:
    """
    Lag the variable by lag 1.

    Args:
        data (pd.DataFrame): The dataset.
        variable (str): The name of the variable to lag.
        time_variable (str): The name of the time variable.
    """

    # Define the lagged variable name using the name_lag_variable helper function
    if isinstance(variable, str):
        variable = [variable]
    lagged_names = [name_lag_variable(var, lag) for var in variable]

    # Sort the dataset by the time variable
    data = data.sort_values(by=time_variable)
    # Group by entity_variable if it is provided, otherwise use the whole panel_data as a group
    groupby = data.groupby(entity_variable) if entity_variable else data
    # Apply the shift to each group
    data[lagged_names] = groupby[variable].apply(lambda x: x.shift(lag))

    return data


def log_return(
    data: pd.DataFrame,
    variable: str,
    time_variable: str = "Date",
    rolling_window_return: int = 1,
) -> pd.DataFrame:
    """
    Calculate the log return of the variable.

    Args:
        data (pd.DataFrame): The dataset.
        variable (str): The name of the variable to calculate the log return.
        time_variable (str): The name of the time variable.
        entity_variable (str): The name of the entity variable.

    Returns:
        pd.DataFrame: The dataset with the log return as well as the log return volatility.
    """
    # Sort the dataset by the time variable
    data = data.sort_values(by=time_variable)

    # make Date with all days included without gap
    data = data.set_index(time_variable).resample("D").asfreq().reset_index()
    # fill the missing values with the previous value with linear interpolation
    data[variable].fillna(method="ffill", inplace=True)

    # handle 0
    # first replace 0 with nan
    data[variable].replace(0, np.nan, inplace=True)
    # impute all na with the previous value
    data[variable] = data[variable].interpolate(method="linear")

    # calculate daily log return
    data[name_log_return_variable(variable, rolling_window_return)] = np.log(
        data[variable] / data[variable].shift(rolling_window_return)
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

    Args:
        data (pd.DataFrame): The dataset.
        variable (str): The name of the variable to calculate the log return.
        rolling_window (int): The rolling window.

    Returns:
        pd.DataFrame: The dataset with the log return volatility.
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
