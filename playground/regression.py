# get the regression panel dataset from pickled file
from os import path

import pandas as pd
from environ.constants import TABLE_PATH
from linearmodels.panel import PanelOLS


def lag_variable(
    panel_data: pd.DataFrame,
    variable: str,
    time_variable: str,
    entity_variable: str = "",
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
    if entity_variable:
        panel_data[f"{variable}_lag"] = panel_data.groupby(entity_variable)[
            variable
        ].shift(1)
    else:
        panel_data[f"{variable}_lag"] = panel_data[variable].shift(1)

    return panel_data


def regress(
    data: pd.DataFrame,
    iv: str = "Volume_share",
    dv: list[str] = ["is_boom", "mcap_share"],
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
    y = data[iv]

    # Define the independent variables
    X = data[dv]

    # Run the fixed-effect regression
    model = PanelOLS(y, X, entity_effects=entity_effect, drop_absorbed=True).fit()

    # Print the summary of the regression results
    print(model.summary)


if __name__ == "__main__":
    # Get the regression panel dataset from pickled file
    reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))

    # Lag the variables
    reg_panel = lag_variable(reg_panel, "Volume_share", "Date", "Token")

    # Run the regression
    regress(reg_panel, entity_effect=False)
