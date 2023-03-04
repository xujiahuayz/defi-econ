"""
plot market with boom bust cycles
"""

from environ.process.spindex.sp import sp_df
from environ.utils.computations import boom_bust
import matplotlib.pyplot as plt
import matplotlib.dates as md

# convert date to timestamp
sp_df["time"] = sp_df["Date"].apply(md.date2num)

# replace s&p colume with price
sp_df = sp_df.rename(columns={"S&P": "price"})

BOOM_BUST = boom_bust(sp_df)

# plot price with boom bust cycles
plt.plot(sp_df["time"], sp_df["price"])
for i in BOOM_BUST["boom"]:
    plt.axvspan(i[0], i[1], color="green", alpha=0.3)
for i in BOOM_BUST["bust"]:
    plt.axvspan(i[0], i[1], color="red", alpha=0.3)

# format the x axis
plt.gca().xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
plt.gcf().autofmt_xdate()

plt.show()
