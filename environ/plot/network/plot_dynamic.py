"""

University College London
Project : defi-econ
Topic   : plot_dynamic.py
Author  : Yichen Luo
Date    : 2022-01-05
Desc    : convert network graphs to vedio.

"""

# Import Python modules
import glob
import cv2
from tqdm import tqdm

# Import Internal modules
from environ.utils.config_parser import Config


def plot_dynamic(uniswap_version: str) -> None:
    """
    Function to convert network graphs to videos.
    """

    # Initialize config
    config = Config()

    # Constants
    framesize = (
        config["dev"]["config"]["dynamic"]["HEIGHT"],
        config["dev"]["config"]["dynamic"]["WIDTH"],
    )
    network_data_path = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]

    # Setting opencv object
    out = cv2.VideoWriter(
        f"{network_data_path}/dynamic_network_{uniswap_version}.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        3,
        framesize,
    )

    # Exhastive conversion
    for filename in tqdm(
        sorted(glob.glob(f"{network_data_path}/{uniswap_version}/network_graph/*.jpg"))
    ):
        img = cv2.imread(filename)
        _ = out.write(img)

    _ = out.release()
