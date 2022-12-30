"""

University College London
Project : defi_econ
Topic   : args_parser.py
Author  : Yichen Luo
Date    : 2022-12-17
Desc    : Parse the info from the terminal.

"""

# Import python modules
import argparse


def arg_parse_cmd() -> None:

    """
    Function for user to interact with terminal.
    """

    # Argument description
    parser = argparse.ArgumentParser(description="Date to update the defi data.")

    # Add argument to input start date
    parser.add_argument(
        "--start",
        required=True,
        help="Provide start date (included) to update in format YYYY-MM-DD.",
    )

    # Add argument to input end date
    parser.add_argument(
        "--end",
        required=True,
        help="Provide end date (excluded) to update in format YYYY-MM-DD.",
    )

    return parser
