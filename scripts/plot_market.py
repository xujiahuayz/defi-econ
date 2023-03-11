"""
plot market with boom bust cycles
"""


from os import path

import matplotlib.dates as md
import matplotlib.pyplot as plt

from environ.constants import FIGURE_PATH
from environ.process.market.boom_bust import BOOM_BUST, sp_df

if __name__ == "__main__":
    # plot price with boom bust cycles
    plt.plot(sp_df["time"], sp_df["price"])
    for i in BOOM_BUST:
        if i["main_trend"] == "boom":
            plt.axvspan(
                i["start"],
                i["end"],
                color="green",
                alpha=0.2,
            )
        if i["main_trend"] == "bust":
            plt.axvspan(
                i["start"],
                i["end"],
                color="red",
                alpha=0.2,
            )

    # change x axis from datetime timestamp to date
    plt.gca().xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()

    # save the plot to file in the figure folder in pdf format
    plt.savefig(path.join(FIGURE_PATH, "sp500.pdf"))
    plt.show()
