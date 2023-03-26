"""
Script to render the moving averages of the variables
"""

from environ.constants import EVENT_DATE_LIST, NETWORK_DATA_PATH
from environ.plot.plot_ma import plot_ma_time_series
from environ.process.market.boom_bust import BOOM_BUST

for version in ["v2", "v3", "merged"]:
    for plot_type in ["Inflow_centrality", "Outflow_centrality"]:
        plot_ma_time_series(
            file_folder=str(NETWORK_DATA_PATH / version / "eigen_centrality_swap"),
            file_name=f"eigen_in_swap_{version}"
            if plot_type == "Inflow_centrality"
            else f"eigen_out_swap_{version}",
            value_colume=plot_type,
            token_col_name="Token",
            ma_window=30,
            event_date_list=EVENT_DATE_LIST,
            boom_bust=BOOM_BUST,
        )

        # plot_ma_time_series(
        #     file_folder=str(NETWORK_DATA_PATH / "eigen_centrality_pool")
        #     + rf"/*_{version}_*",
        #     file_name=f"eigen_in_{version}"
        #     if plot_type == "Inflow_centrality"
        #     else f"eigen_out_{version}",
        #     value_colume=plot_type,
        #     token_col_name="Token",
        #     ma_window=30,
        #     event_date_list=EVENT_DATE_LIST,
        #     boom_bust=BOOM_BUST,
        # )
