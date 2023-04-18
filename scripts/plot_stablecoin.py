"""
plot stablecoin price
"""

import matplotlib.pyplot as plt
import pandas as pd

from environ.constants import FIGURE_PATH, DATA_PATH, STABLE_DICT, SAMPLE_PERIOD

# read pickled reg_panel
series_name = "exchange_to_underlying"
reg_panel = pd.read_pickle(DATA_PATH / "reg_panel.pkl")
# get only token, date and dollar price for only stablecoins
reg_panel.reset_index(inplace=True)
# restrict to stablecoins and SAMPLE_PERIOD
stablecoin_price = reg_panel[["Token", "Date", series_name]].loc[
    (reg_panel["Stable"] == 1)
    & (reg_panel["Date"] >= SAMPLE_PERIOD[0])
    & (reg_panel["Date"] <= SAMPLE_PERIOD[1])
]

# sort by date
stablecoin_price.sort_values(by="Date", inplace=True)

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
# log scale on y axis
# plt.yscale("log")

plt.ylim(0.01, 1.99)

# add horizontal line at 1, with transparency 0.5
plt.axhline(y=1, color="black", linestyle="--", alpha=0.5)
# rotate x axis labels by 45 degrees
plt.xticks(rotation=45)

# have legend outside the plot
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
# add x and y labels
plt.xlabel("Date")
plt.ylabel("Exchange rate to underlying")
# save to figures folder
plt.savefig(FIGURE_PATH / "stablecoin_price.pdf", bbox_inches="tight")
plt.show()
plt.close()
