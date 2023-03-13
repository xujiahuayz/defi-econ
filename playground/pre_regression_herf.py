import re
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.process.market.prepare_market_data import market_data

# read csv file as pd.DataFrame where Date column is parsed as datetime
herf_panel = pd.read_csv(
    Path(TABLE_PATH) / "series_herfindahl.csv", parse_dates=["Date"]
)


# merge boom bust cycles
herf_panel = _merge_boom_bust(herf_panel)
herf_panel = herf_panel.merge(market_data, on=["Date"], how="left")

herf_panel = herf_panel.set_index(["Date"])

herf_panel.to_pickle(Path(TABLE_PATH) / "herf_panel.pkl")
