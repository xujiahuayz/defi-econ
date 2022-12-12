# -*- coding: utf-8 -*-
"""
Merge the day-by-day result for betweenness centrality
"""

from os import path
from defi_econ.constants import BETWEENNESS_DATA_PATH
import pandas as pd
import datetime


if __name__ == "__main__":
    involve_version = "v2v3"  # candidate: v2, v3, v2v3

    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2021, 5, 5, 0, 0)
    end_date = datetime.datetime(2022, 8, 1, 0, 0)

    merge_file = path.join(
        BETWEENNESS_DATA_PATH,
        str("betweenness_centrality_merge_v2v3.csv"),
    )

    merge_data = pd.read_csv(merge_file)

    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # for each day
    for date in date_list:
        date_str = date.strftime("%Y%m%d")

        date_file = path.join(
            BETWEENNESS_DATA_PATH,
            str(
                "betweenness/betweenness_centrality_"
                + involve_version
                + "_"
                + date_str
                + ".csv"
            ),
        )

        betweenness_date_data = pd.read_csv(date_file)
        betweenness_date_data["date"] = date

        # merge
        merge_data = pd.concat([merge_data, betweenness_date_data], ignore_index=True)

        print("-----Merge betweenness centrality in " + date_str + "-----")

    merge_data.to_csv(merge_file, index=False)
