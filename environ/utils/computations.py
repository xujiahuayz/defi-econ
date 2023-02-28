import pandas as pd


def boom_bust(
    time_pirce: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> dict[str, tuple[int, int]]:
    """
    Return the boom and bust periods of the given price.
    """
    # Sort the time_price dataframe by time
    time_price = time_pirce.sort_values(by="time")
    # TODO: finish
    return


if __name__ == "__main__":

    price = pd.DataFrame(
        {
            "time": [
                1469966400,
                1472558500,
                1469966800,
                1469966900,
                1472558500,
                1475150600,
                1469966900,
                1469967000,
            ],
            "price": [9, 10, 29, 2, 69, 10, 2, 69],
        }
    )
    print(boom_bust(price))
