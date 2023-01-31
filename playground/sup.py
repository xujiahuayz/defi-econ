import pandas as pd
import glob

# use a for loop to read in all the files in data/data_betweenness/sup and change the file name

path = rf"data/data_betweenness/sup"  # use your path
all_files = glob.glob(path + "/*.csv")

for filename in all_files:
    df = pd.read_csv(filename)
    # change the file name from the format of betweeness_centrality_v2_*.csv to betweeness_centrality_v2v3_*.csv
    df.to_csv(
        filename.replace("betweenness_centrality_v2", "betweenness_centrality_v2v3"),
        index=False,
    )
