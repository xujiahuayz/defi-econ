import pandas as pd
import glob
import os
from environ.constants import BETWEENNESS_DATA_PATH, PROCESSED_DATA_PATH
# Find all files matching the pattern
file_pattern = "betweenness_centrality_subgraph_v3_*.csv"
file_list = list((BETWEENNESS_DATA_PATH / "betweenness").glob(file_pattern))

# Create a list to hold the dataframes
all_dataframes = []

# Loop through the files and process them
for file in file_list:
    # Read the file into a dataframe
    df = pd.read_csv(file)

    # Extract the date from the filename
    # This assumes the date is the last part of the filename and is separated by '_'
    date_part = file.stem.split('_')[-1]
    df['Date'] = date_part

    # Add the dataframe to the list
    all_dataframes.append(df)

# Concatenate all dataframes in the list
combined_df = pd.concat(all_dataframes, ignore_index=True)

# Save the combined dataframe to a new CSV file
combined_df.to_csv(PROCESSED_DATA_PATH/"combined_betweenness_centrality.csv", index=False)

# Display the first few rows of the combined dataframe
print("Successfully combined daily betw data")