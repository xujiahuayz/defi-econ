import pandas as pd


def depeg_persistancy(price_series: pd.Series, rolling_window: int = 14) -> pd.Series:
    """
    Function to count how many times a Token's price in the past 14 days falls below 0.95 or above 1.05.
    """
    return price_series.rolling(rolling_window).apply(
        lambda x: (sum(x < 0.95) + sum(x > 1.05)) >= rolling_window / 2
    )


def _merge_depeg_persistancy(
    reg_panel: pd.DataFrame,
    price_col_name: str = "dollar_exchange_rate",
    new_col_name: str = "depeg_pers",
    rolling_window: int = 14,
) -> pd.DataFrame:
    """
    function to merge the depeg persistancy
    """
    # sort by date
    reg_panel = reg_panel.sort_values(by=["Token", "Date"], ascending=True)
    # group the reg_panel by Token
    group = reg_panel.groupby("Token")

    # calculate the depeg persistancy
    reg_panel[new_col_name] = group[price_col_name].apply(
        lambda x: depeg_persistancy(x, rolling_window=rolling_window)
    )
    reg_panel[new_col_name] = reg_panel[new_col_name] * reg_panel["Stable"]
    return reg_panel


if __name__ == "__main__":
    # create some dummy data to test the functions above
    import numpy as np

    reg_panel = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", "2020-01-05").repeat(2),
            "Token": ["A", "B"] * 5,
            "dollar_exchange_rate": np.random.uniform(0.9, 1.1, 10),
            "Stable": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        }
    )
    print(_merge_depeg_persistancy(reg_panel, rolling_window=4))
