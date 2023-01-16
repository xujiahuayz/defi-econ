"""

University College London
Project : defi_econ
Topic   : data_processor.py
Author  : Yichen Luo
Date    : 2022-12-18
Desc    : Process DeFi data.

"""
# Import python modules
import datetime
from tqdm import tqdm

# Import internal modules
from environ.utils.args_parser import arg_parse_cmd
from environ.utils.info_logger import print_info_log
from .network.prepare_network_data import prepare_network_data


def process_data():

    """
    Aggregate function to process defi data.
    """

    # Initialize argument parser
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Input start date and end date
    start_date = datetime.datetime.strptime(parsed_args.start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(parsed_args.end, "%Y-%m-%d")

    # Generate date list
    date_list = []
    for i in range((end_date - start_date).days + 1):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # Process network data
    print_info_log(
        f"Process Network Data from {parsed_args.start} to {parsed_args.end}",
        "progress",
    )

    for date in tqdm(date_list, total=len(date_list)):
        prepare_network_data(date, "v2")
        prepare_network_data(date, "v3")
