import numpy as np
import pandas as pd


def name_boom_interact_var(variable: str) -> str:
    """
    Name the boom interact variable.

    Args:
        variable (str): The name of the variable.

    Returns:
        str: The name of the boom interact variable.
    """
    return f"{variable}_boom"


def name_lag_variable(variable: str, lag: int = 1) -> str:
    """
    Name the lagged variable.

    Args:
        variable (str): The name of the variable.

    Returns:
        str: The name of the lagged variable.
    """
    return f"{variable}_lag_{lag}"


# def name_lag_variable


# NAMING_DICT_LAG = {
#     name_lag_variable(k): "{" + v + "}_{t-1}" for k, v in NAMING_DICT.items()
# }


# # boom_naming_dict with NAMING_DICT and NAMING_DICT_LAG
# BOOM_INTERACTION_DICT = {
#     name_boom_interact_var(k): f"{v} : {NAMING_DICT['is_boom']}"
#     for k, v in {**NAMING_DICT_LAG, **NAMING_DICT}.items()
# }


def name_log_return_variable(variable: str, rolling_window_return: int) -> str:
    return f"{variable}_log_return_{rolling_window_return}"


def name_log_return_vol_variable(
    variable: str, rolling_window_return: int, rolling_window_vol: int
) -> str:
    return f"{variable}_log_return_vol_{rolling_window_return}_{rolling_window_vol}"


def lag_variable(
    panel_data: pd.DataFrame,
    variable: str,
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
    # Sort the dataset by the time variable
    panel_data = panel_data.sort_values(by=time_variable)

    # Lag the variable by lag 1
    # TODO: this assumes there is no gap in the time variable -- need to double check

    grouped_panel = (
        panel_data.groupby(entity_variable)[variable]
        if entity_variable
        else panel_data[variable]
    )
    panel_data[name_lag_variable(variable, lag=lag)] = grouped_panel.shift(lag)

    return panel_data


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
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", "2020-01-20").append(
                pd.date_range("2020-02-01", "2020-02-10")
            ),
            "price1": [1, 2, 0, 4, 5, 6, 0, 0, 9, 10] * 3,
            "price2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1] * 3,
        }
    )

    new_data = log_return(data, "price1", "Date", 2)
    new_data = return_vol(new_data, "price1", 2, 6)
