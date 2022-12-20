"""

University College London
Project : defi_econ
Topic   : args_parser.py
Author  : Yichen Luo
Date    : 2022-12-17
Desc    : Parse the info from the terminal.

"""

import argparse


def arg_parse_cmd():
    parser = argparse.ArgumentParser(description="Date to update the defi data.")
    parser.add_argument(
        "--date", required=False, help="Provide date to update in format YYYY-MM-DD."
    )
    return parser
