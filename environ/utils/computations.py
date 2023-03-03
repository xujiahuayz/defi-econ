import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)


def boom_bust_one_period(
    time_price: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> dict:
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

    # logging.info(f"boom_at: {boom[0]}, bust_at: {bust[0]}")

    if boom:
        boom_end = boom[0]
        if bust and bust[0] < boom_end:
            # bust before boom
            bust_end = bust[0] - 1
            while time_price["price"][bust_end + 1] < time_price["price"][bust_end]:
                bust_end += 1
                if bust_end + 1 >= len(time_price["price"]):
                    break
            cycle = "bust", bust_end
        else:
            # no bust, def just boom, find the next peak before price goes down
            # calculate rolling difference of price after i
            # find the first index that is positive
            boom_end = boom_end - 1
            while time_price["price"][boom_end + 1] > time_price["price"][boom_end]:
                boom_end += 1
                if boom_end + 1 >= len(time_price["price"]):
                    break
            cycle = "boom", boom_end
    elif bust:
        # no boom, just bust
        bust_end = bust[0] - 1
        while time_price["price"][bust_end + 1] < time_price["price"][bust_end]:
            bust_end += 1
            if bust_end + 1 >= len(time_price["price"]):
                break
        cycle = "bust", bust_end
    else:
        # no boom, no bust
        cycle = "none", len(time_price["time"]) - 1

    cycle_dict = {"main_trend": cycle[0], "end": time_price["time"][cycle[1]]}

    # find the price peak within the cycle
    price_peak = max(time_price["price"][: cycle[1] + 1])
    price_trough = min(time_price["price"][: cycle[1] + 1])

    if cycle[0] == "boom":
        # find the first index that is equal to price trough
        start = time_price["time"][time_price["price"] == price_trough].index[0]
        # print(start)
        if start > 0:
            cycle_dict["pre_trend_end"] = time_price["time"][start]
    elif cycle[0] == "bust":
        # find the first index that is equal to price peak
        start = time_price["time"][time_price["price"] == price_peak].index[0]
        if start > 0:
            cycle_dict["pre_trend_end"] = time_price["time"][start]

    return cycle_dict


def boom_bust_periods(
    time_price: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> list:
    boom_bust_list = []
    # Sort the time_price dataframe by time
    time_price = time_price.sort_values(by="time").reset_index(drop=True)
    end = time_price["time"][0]
    previous_trend = "none"
    while end < time_price["time"].iloc[-1]:
        time_price = time_price[time_price["time"] >= end].reset_index(drop=True)
        cycle_dict = boom_bust_one_period(time_price, boom_change, bust_change)
        if cycle_dict["main_trend"] != "none" and previous_trend != "none":
            if cycle_dict["main_trend"] == previous_trend:
                boom_bust_list[-1]["end"] = cycle_dict["end"]
            else:
                if "pre_trend_end" in cycle_dict:
                    boom_bust_list[-1]["end"] = cycle_dict["pre_trend_end"]
                    boom_bust_list.append(
                        {
                            "main_trend": cycle_dict["main_trend"],
                            "start": cycle_dict["pre_trend_end"],
                            "end": cycle_dict["end"],
                        }
                    )
                else:
                    boom_bust_list.append(
                        {
                            "main_trend": cycle_dict["main_trend"],
                            "start": end,
                            "end": cycle_dict["end"],
                        }
                    )
        else:
            boom_bust_list.append(
                {
                    "main_trend": cycle_dict["main_trend"],
                    "start": end,
                    "end": cycle_dict["end"],
                }
            )
        end = cycle_dict["end"]
        previous_trend = cycle_dict["main_trend"]
    return boom_bust_list


def boom_bust(
    time_price: pd.DataFrame, boom_change: float = 0.3, bust_change: float = 0.3
) -> dict[str, list[tuple[int, int]]]:
    """
    change the format of boom_bust_list to a dict
    {"boom": [(start, end)], "bust": [(start, end)], "none": [(start, end)]}
    """
    boom_bust_list = boom_bust_periods(time_price, boom_change, bust_change)
    boom_bust_dict = {"boom": [], "bust": [], "none": []}
    for i in boom_bust_list:
        boom_bust_dict[i["main_trend"]].append((i["start"], i["end"]))
    return boom_bust_dict


if __name__ == "__main__":

    price = pd.DataFrame(
        {
            "time": [
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                1000,
                1100,
                1200,
            ],
            "price": [
                9,
                10,
                29,
                2,
                69,
                10,
                2,
                69,
                120,
                6,
                7,
            ],
        }
    )

    periods = boom_bust_periods(price)

    # plot the price with the boom bust periods
    import matplotlib.pyplot as plt

    # sort the price by time
    price = price.sort_values(by="time").reset_index(drop=True)

    plt.plot(price["time"], price["price"])

    # plot boom as green and bust as red
    for i in periods:
        if i["main_trend"] == "boom":
            plt.axvspan(i["start"], i["end"], color="green", alpha=0.5)
        elif i["main_trend"] == "bust":
            plt.axvspan(i["start"], i["end"], color="red", alpha=0.5)
