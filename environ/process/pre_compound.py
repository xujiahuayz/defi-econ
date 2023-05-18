"""
Script to preprocess the compound data
"""

import os

import pandas as pd

from environ.constants import COMPOUND_DATA_PATH, COMPOUND_DEPLOYMENT_DATE


def calculate_borrow_supply(file_name: str) -> pd.DataFrame:
    """
    function to calculate the borrow and supply in USD
    """

    compound_info = pd.read_csv(file_name)

    # Calculate the borrow rata in USD
    compound_info["total_borrow_usd"] = (
        compound_info["total_borrows_history"] * compound_info["prices_usd"]
    )
    compound_info["total_supply_usd"] = (
        compound_info["total_supply_history"]
        * compound_info["exchange_rates"]
        * compound_info["prices_usd"]
    )
    # convert the timestamp to datetime
    compound_info["block_timestamp"] = pd.to_datetime(
        compound_info["block_timestamp"], unit="s"
    )

    # only keep the required columns
    compound_info = compound_info[
        [
            "block_timestamp",
            "total_borrow_usd",
            "total_supply_usd",
            "borrow_rate",
            "supply_rates",
        ]
    ]
    return compound_info


if __name__ == "__main__":
    # check if the processed data folder exists
    if not os.path.exists(str(COMPOUND_DATA_PATH / "processed")):
        os.makedirs(str(COMPOUND_DATA_PATH / "processed"))

    # get the list of ctoken symbols
    ctoken_symbol_lst = [ctoken["Token"] for ctoken in COMPOUND_DEPLOYMENT_DATE]

    # a list to store the processed data
    processed_data = []

    # iterate through the ctoken symbols
    for ctoken_symbol in ctoken_symbol_lst:
        # Calculate the borrow and supply in USD
        compound_info = calculate_borrow_supply(
            str(COMPOUND_DATA_PATH / ("compound_" + ctoken_symbol + ".csv"))
        )

        if ctoken_symbol == "WBTC":
            # Calculate the borrow and supply in USD
            compound_info2 = calculate_borrow_supply(
                str(COMPOUND_DATA_PATH / ("compound_" + "WBTC2" + ".csv"))
            )

            compound_info = pd.concat(
                [compound_info, compound_info2], ignore_index=True
            )

            # aggregate the data by timestamp, and take the first borrow rate and supply rate
            compound_info = (
                compound_info.groupby(["block_timestamp"])
                .agg(
                    {
                        "total_borrow_usd": "sum",
                        "total_supply_usd": "sum",
                        "borrow_rate": "first",
                        "supply_rates": "first",
                    }
                )
                .reset_index()
            )

            # compound_info = (
            #     compound_info.groupby(["block_timestamp"])[
            #         ["total_borrow_usd", "total_supply_usd"]
            #     ]
            #     .sum()
            #     .reset_index()
            # )

        # skip the wbtc2 data
        if ctoken_symbol == "WBTC2":
            continue

        # sort the data by timestamp
        compound_info = compound_info.sort_values(by=["block_timestamp"])

        # create the Token column
        compound_info["Token"] = ctoken_symbol if ctoken_symbol != "ETH" else "WETH"

        # rename the Time column
        compound_info = compound_info.rename(columns={"block_timestamp": "Date"})

        # append the data to the list
        processed_data.append(compound_info)

    # concatenate the data
    processed_data = pd.concat(processed_data, ignore_index=True)

    # calculate teh supply share and borrow share
    for share in ["supply", "borrow"]:
        processed_data[f"total_{share}"] = processed_data.groupby("Date")[
            f"total_{share}_usd"
        ].transform("sum")
        processed_data[f"{share}_share"] = (
            processed_data[f"total_{share}_usd"] / processed_data[f"total_{share}"]
        )

    # get the unique dates
    unique_dates = processed_data["Date"].unique()

    # iterate through the dates
    for date in unique_dates:
        # get the data for the date
        date_data = processed_data[processed_data["Date"] == date]

        # convert the date to %Y%m%d format
        date = date.strftime("%Y%m%d")

        # save the data
        date_data.to_csv(
            str(COMPOUND_DATA_PATH / "processed" / f"compound_{date}.csv"),
            index=False,
        )
