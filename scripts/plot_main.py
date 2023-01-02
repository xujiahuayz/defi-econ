# -*- coding: utf-8 -*-
"""

University College London
Project : defi_econ
Topic   : plot_main.py
Author  : Yichen Luo
Date    : 2023-01-02

"""

# Import internal modules.
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log
from environ.utils.args_parser import arg_parse_cmd
from environ.plot.graph_plotter import plot_graph

if __name__ == "__main__":

    # Initize the config and parse the running date.
    print_info_log("DeFi graph plot script started", "progress")

    config = Config()
    args = arg_parse_cmd()
    parsed_args = args.parse_args()

    # Plot graphs.
    plot_graph()

    # Finish.
    print_info_log("Plot script finished", "progress")
