"""
plot stablecoin price
"""

from os import path

import matplotlib.pyplot as plt
import pandas as pd

from environ.constants import TABLE_PATH, STABLE_DICT

# read pickled reg_panel
series_name = "exchange_to_underlying"
reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))
# get only token, date and dollar price for only stablecoins
reg_panel.reset_index(inplace=True)
stablecoin_price = reg_panel[["Token", "Date", series_name]].loc[
    reg_panel["Stable"] == 1
]

# plot stablecoin price with different colors AND different markers for each stablecoin
# prepare a dictionary of colors and line type for
# ['BUSD', 'DAI', 'DSD', 'ESD', 'EURS', 'EURT', 'FEI', 'FRAX', 'LUSD', 'MIM', 'PAX', 'TUSD', 'USDC', 'USDT', 'UST', 'XSGD', 'agEUR','oneUNI', 'sUSD']


for token in stablecoin_price["Token"].unique():
    # get the color and line type for each token
    spec = STABLE_DICT[token]
    color = spec["color"]
    line_type = spec["line_type"]
    # plot the price
    plt.plot(
        stablecoin_price.loc[stablecoin_price["Token"] == token]["Date"],
        stablecoin_price.loc[stablecoin_price["Token"] == token][series_name],
        color=color,
        linestyle=line_type,
        label=token,
    )
# y axis 0 - 3

plt.ylim(0, 2.5)

# add horizontal line at 1, with transparency 0.5
plt.axhline(y=1, color="black", linestyle="--", alpha=0.5)
# have legend outside the plot
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
# add x and y labels
plt.xlabel("Date")
plt.ylabel("Exchange rate to underlying")
plt.show()
