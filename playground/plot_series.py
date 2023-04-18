"""
Script to plot the series of a given dataset.
"""

import matplotlib.pyplot as plt
import pandas as pd

panel_main = pd.read_csv("test/panel_main.csv")

# calculate the ulti_volume_fraction group by date
panel_main = (
    panel_main.groupby(["Date"])
    .apply(
        lambda x: x["volume_ultimate"].sum()
        / (x["vol_inter_full_len"].sum() + x["volume_ultimate"].sum()),
    )
    .reset_index()
)

# rename the columns
panel_main.columns = ["Date", "ulti_volume_fraction"]

# convert the date to datetime
panel_main["Date"] = pd.to_datetime(panel_main["Date"])

# plot the series using plt
plt.plot(panel_main["Date"], panel_main["ulti_volume_fraction"])

# rotate the x-axis labels
plt.xticks(rotation=45)

# tight layout
plt.tight_layout()

plt.show()
