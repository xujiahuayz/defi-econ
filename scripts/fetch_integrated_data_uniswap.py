# -*- coding: utf-8 -*-
"""
Work flow of fetching Uniswap data
"""


import datetime
from scripts.fetch_scripts_v2 import select_top50_pairs_v2_script
from scripts.fetch_scripts_v3 import select_top50_pairs_v3_script
from scripts.fetch_scripts_v2 import top50_pair_directional_volume_v2_script
from scripts.fetch_scripts_v3 import top50_pair_directional_volume_v3_script
from scripts import prepare_network_data, plot_network


if __name__ == "__main__":
    uniswap_version = "v2"
    top50_list_label = "2022JUL"

    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2022, 7, 11, 0, 0)
    end_date = datetime.datetime(2022, 8, 1, 0, 0)

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # Step 1: determine the list of monthly top 50 pools as candidates
    # if uniswap_version == "v2":
    #     select_top50_pairs_v2_script.select_top50_pairs_v2(
    #         end_date - datetime.timedelta(1), 30, top50_list_label
    #     )

    # elif uniswap_version == "v3":
    #     select_top50_pairs_v3_script.select_top50_pairs_v3(
    #         end_date - datetime.timedelta(1), 30, top50_list_label
    #     )

    print("------Step 1 Complete: monthly top token list------")

    # Step 2: get directional daily volume for all dates based on the list in Step 1
    for date in date_list:
        if uniswap_version == "v2":
            top50_pair_directional_volume_v2_script.top50_pair_directional_volume_v2(
                date, top50_list_label
            )

        elif uniswap_version == "v3":
            top50_pair_directional_volume_v3_script.top50_pair_directional_volume_v3(
                date, top50_list_label
            )

        print("------Step 2 Complete: fetch daily directional volume------")

        # Step 3: prepare the network data from the "top50_directional_volume.csv"
        prepare_network_data.prepare_network_data(date, uniswap_version)
        print("------Step 3 Complete: prepare network data------")

        # Step 4: generate network plot and degree dataset
        plot_network.plot_network(date, uniswap_version)
        print("------Step 4 Complete: plot network and generate degree")

        print("********Complete task for " + date.strftime("%Y%m%d") + "********")
