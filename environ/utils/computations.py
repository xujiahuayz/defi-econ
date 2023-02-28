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
    boom = [i for i, w in enumerate(time_price["price"]) if w > time_price["price"][0] * (1 + boom_change)]
    bust = [i for i, w in enumerate(time_price["price"]) if w < time_price["price"][0] * (1 - bust_change)]

    if boom:
         if bust:
              pass
         else:
            #   no bust, def just boom, find the next peak before price goes down
            # calculate rolling difference of price after i
            # find the first index that is positive
             = [i for i, w in enumerate(time_price["price"]) if (
                 time_price['time'][i] > time_price['time'][boom[0]] and w > time_price["price"][i-1]) ]








    booms = []
    busts = []

    while sum(boom) > 0:
        if sum(bust) > 0:
            first_price_up = boom.index(True)
            first_price_down = bust.index(True)
            if first_price_up > first_price_down:
                # boom first
                # check if there is a bust of boom after the boom
                min_price_up = time_price["price"][first_price_up] * (1 + boom_change)
                max_price_down = time_price["price"][first_price_up] * (1 - bust_change)
            else:
                # bust first
        else:
            # no bust at the beginning, boom first
            


                boom = [0]

    # boom = [i for i, w in enumerate(time_price["price"]) if w > min_price_up]
    # bust = [i for i, w in enumerate(time_price["price"]) if w < max_price_down]

    # if boom:
    #     if bust:
    #         if boom[0] > bust[0]:
    #             # boom first
    #             boom = [0]

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
