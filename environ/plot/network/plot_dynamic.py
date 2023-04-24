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

from environ.constants import NETWORK_DATA_PATH

HEIGHT = 1600
WIDTH = 1200


def plot_dynamic(uniswap_version: str) -> None:
    """
    Function to convert network graphs to videos.
    """

    # Constants
    framesize = (
        HEIGHT,
        WIDTH,
    )

    # Setting opencv object
    out = cv2.VideoWriter(
        f"{NETWORK_DATA_PATH}/dynamic_network_{uniswap_version}.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        3,
        framesize,
    )

    # Exhastive conversion
    for filename in tqdm(
        sorted(glob.glob(f"{NETWORK_DATA_PATH}/{uniswap_version}/network_graph/*.jpg"))
    ):
        img = cv2.imread(filename)
        _ = out.write(img)

    _ = out.release()
