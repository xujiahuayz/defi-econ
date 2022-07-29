# -*- coding: utf-8 -*-
"""
Tidy up and Pre-Processing the dataset for the regression
"""

from os import path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from defi_econ.constants import REGRESSION_DATA_PATH


def standardize_data(pd_data) -> pd.DataFrame:
    """
    Standardize the X variables for the dataset as pre-processing
    """
    X = pd_data.loc[:, "asset_price":]
    scaler = StandardScaler()
    scaler = scaler.fit(X)
    X_scaled = scaler.transform(X)
    pd_data.loc[:, "asset_price":] = X_scaled

    return pd_data


if __name__ == "__main__":
    data = pd.read_csv(
        path.join(REGRESSION_DATA_PATH, "regression_data_sample.csv"),
        index_col=["symbol", "date"],
    )
