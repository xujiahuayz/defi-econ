from environ.process.betweeness_centrality.betweeness_scripts import get_betweenness_centrality
import datetime

if __name__ == "__main__":

    from multiprocessing import Pool
    from functools import partial

    involve_version = "subgraph_v3"  # candidate: v2, v3, v2v3

    top50_list_label = "2021MAY"
    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2021, 5, 4, 0, 0)
    end_date = datetime.datetime(2023, 1, 31, 0, 0)

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_str = date.strftime("%Y-%m-%d")
        date_list.append(date_str)

    # Multiprocess
    p = Pool()
    p.map(
        partial(
            get_betweenness_centrality,
            top_list_label=top50_list_label,
            uniswap_version=involve_version,
        ),
        date_list,
    )
