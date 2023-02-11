"""
Function to fetch the crypto sentiment data
"""

import pandas as pd
import requests
from environ.utils.config_parser import Config

# Initialize the config parser
config = Config()

# Initialize the path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]


def fetch_fear_and_greed_index() -> None:
    """
    Fecth the fear and greed index in the crypto market.
    """

    # Fetch the fear and greed index
    url = "https://api.alternative.me/fng/?limit=0"
    response = requests.get(url)
    data = response.json()
    data = data["data"]

    # Convert the data into a dataframe
    data = pd.DataFrame(data)
    data = data[["timestamp", "value"]]
    data.columns = ["Date", "sentiment"]

    # Convert the timestamp to datetime
    data["Date"] = pd.to_datetime(data["Date"], unit="s")

    # Sort the data by date
    data = data.sort_values(by="Date")

    # Convert the sentiment to float
    data["sentiment"] = data["sentiment"].astype(int)

    # Save the data to a csv file
    data.to_csv(
        rf"{GLOBAL_DATA_PATH}/sentiment/sentiment.csv",
        index=False,
    )


if __name__ == "__main__":
    fetch_fear_and_greed_index()
