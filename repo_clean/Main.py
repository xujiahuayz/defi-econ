"""

University College London
Project : defi_econ
Topic   : Main.py
Author  : Yichen Luo
Date    : 2022-12-17

"""

# Import internal modules.
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd

if __name__ == "__main__":

    # Initize the config and parse the running date.
    print_info_log("DeFi script started", "progress")

    config = Config()
    args = arg_parse_cmd()
    parsed_args = args.parse_args()
    run_date = parsed_args.date

    print_info_log(run_date, "progress")
