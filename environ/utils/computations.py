import pandas as pd


def boom_bust_one_period(
    time_price: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> tuple[str, tuple[int, int]]:
    """
    Return the boom and bust periods of the given price.
    """
    # Sort the time_price dataframe by time
    # assume already sorted
    # time_price = time_price.sort_values(by="time").reset_index(drop=True)

    # find the next price that is crosses the threshold
    boom = [
        i
        for i, w in enumerate(time_price["price"])
        if w > time_price["price"][0] * (1 + boom_change)
    ]
    bust = [
        i
        for i, w in enumerate(time_price["price"])
        if w < time_price["price"][0] * (1 - bust_change)
    ]

    if boom:
        boom_end = boom[0]
        if bust and bust[0] < boom_end:
            # bust before boom
            bust_end = bust[0] - 1
            while time_price["price"][bust_end + 1] < time_price["price"][bust_end]:
                bust_end += 1
            return "bust", (time_price["time"][0], time_price["time"][bust_end])
        else:
            # no bust, def just boom, find the next peak before price goes down
            # calculate rolling difference of price after i
            # find the first index that is positive
            boom_end = boom_end - 1
            while time_price["price"][boom_end + 1] > time_price["price"][boom_end]:
                boom_end += 1
        return "boom", (time_price["time"][0], time_price["time"][boom_end])
    elif bust:
        # no boom, just bust
        bust_end = bust[0] - 1
        while time_price["price"][bust_end + 1] < time_price["price"][bust_end]:
            bust_end += 1
        return "bust", (time_price["time"][0], time_price["time"][bust_end])
    else:
        # no boom, no bust
        return "none", (time_price["time"][0], time_price["time"].iloc[-1])


def boom_bust(
    time_price: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> dict[str, list[tuple[int, int]]]:
    boom_bust_dict = {"boom": [], "bust": [], "none": []}
    # Sort the time_price dataframe by time
    time_price = time_price.sort_values(by="time").reset_index(drop=True)
    end = time_price["time"][0]
    while end < time_price["time"].iloc[-1]:
        print(end)
        time_price = time_price[time_price["time"] >= end].reset_index(drop=True)
        print(time_price)
        boom_or_bust, (start, end) = boom_bust_one_period(
            time_price, boom_change, bust_change
        )
        boom_bust_dict[boom_or_bust].append((start, end))
        print(boom_or_bust, start, end, "====")
    return boom_bust_dict


if __name__ == "__main__":

    price = pd.DataFrame(
        {
            "time": [
                1469966400,
                1472558505,
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
