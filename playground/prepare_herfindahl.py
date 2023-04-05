import pandas as pd
import matplotlib.pyplot as plt
import glob

# load in all the data data/data_network/merged/volume_share in chronological order
# each csv file's title contains the date, and has columes: Token, Volume, and has row number
# the new combined dataframe has colume: Date, Token, Volume

# get all csv files in data/data_network/merged/volume_share
path = rf"data/data_network/merged/clustering_ind"  # use your path
all_files = glob.glob(path + "/*.csv")

# extract date from file name
# calculate the herfindahl index
# combine data from all csv files into one dataframe, dropping row number of each csv file
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    date = filename.split("_")[-1].split(".")[0]
    df["clustering_coefficient"] = df["clustering_coefficient"].astype(float)
    # convert the "yyyymmdd" date to datetime format
    date = pd.to_datetime(date, format="%Y%m%d")
    li.append((date, (df["clustering_coefficient"] ** 2).sum()))

# calculate the herfindahl index that's all
herfindahl = pd.DataFrame(li, columns=["Date", "Herfindahl Index"])
herfindahl = herfindahl.set_index("Date")

# sort the dataframe by date
herfindahl = herfindahl.sort_index()

# calculate the 30-day moving average of herfindahl index
# the x-axis is date, the y-axis is herfindahl index
# the plot is saved in data/data_network/merged/volume_share/herfindahl.pdf
herfindahl["Herfindahl Index MA"] = (
    herfindahl["Herfindahl Index"].rolling(window=30).mean()
)

# Plot the Herfindahl Index with some transparency as well as the Herfindahl Index MA
plt.figure(figsize=(10, 5))
plt.plot(herfindahl["Herfindahl Index"], alpha=0.5)
plt.plot(herfindahl["Herfindahl Index MA"], color="olive", linewidth=3)

# draw a thick vertical lines  with some transparency
plt.axvline(
    x=pd.to_datetime("2020-11-26"), color="red", linewidth=3, alpha=0.5
)  # Compound attack of 2020
plt.axvline(
    x=pd.to_datetime("2021-05-05"), color="red", linewidth=3, alpha=0.5
)  # Introduction of Uniswap V3
plt.axvline(
    x=pd.to_datetime("2022-05-10"), color="red", linewidth=3, alpha=0.5
)  # Luna crash
plt.axvline(
    x=pd.to_datetime("2022-11-11"), color="red", linewidth=3, alpha=0.5
)  # FTX collapse
plt.xlabel("Date")
plt.ylabel("Herfindahl Index")
plt.title("Herfindahl Index of Uniswap")
plt.savefig("figures/herfindahl_cluster_coef.pdf")
plt.show()
