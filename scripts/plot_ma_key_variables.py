"""
Script to render the moving averages of the variables
"""

from environ.constants import EVENT_DATE_LIST, NETWORK_DATA_PATH
from environ.plot.plot_ma import plot_ma_time_series
from environ.process.market.boom_bust import BOOM_BUST

for graph_type in [
    "volume_share",
    "volume_in",
    "volume_out",
    # "tvl",
    # "eigen_in",
    # "eigen_out",
    # "betweenness_centrality_count",
    # "betweenness_centrality_volume",
]:
    for source in [
        # "v2", "v3",
        "merged"
    ]:
        plot_ma_time_series(
            file_folder=NETWORK_DATA_PATH / source / graph_type,
            file_name=f"{graph_type}_{source}",
            value_colume="Volume",
            token_col_name="Token",
            ma_window=30,
            event_date_list=EVENT_DATE_LIST,
            boom_bust=BOOM_BUST,
        )
