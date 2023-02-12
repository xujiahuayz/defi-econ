"""

University College London
Project : defi_econ
Topic   : result_tabulator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Tabulate the results.

"""

import pandas as pd
from environ.tabulate.panel.panel_generator import generate_panel
from environ.tabulate.summary.sum_generator import generate_sum
from environ.tabulate.regression.reg_generator import generate_reg
from environ.tabulate.panel.store_proxy import merge_safeness_measurement
from environ.tabulate.regression.reg_generator import change_in_r_squared
from environ.utils.info_logger import print_info_log


def tabulate_result() -> None:
    """
    Tabulate the results.
    """

    print_info_log("Tabulating the results.", "process")
    print_info_log("Generating the panel.", "process")
    reg_panel = generate_panel()
    print_info_log("Merging the safeness measurement.", "process")
    reg_panel = merge_safeness_measurement(reg_panel)
    print_info_log("Generating the summary.", "process")
    reg_panel = generate_sum(reg_panel)
    print_info_log("Generating the regression.", "process")
    generate_reg(reg_panel)
    print_info_log("Generating the change in r-squared.", "process")
    change_in_r_squared(reg_panel)
