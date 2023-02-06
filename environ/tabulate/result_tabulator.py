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
from environ.utils.info_logger import print_info_log


def tabulate_result() -> None:
    """
    Tabulate the results.
    """

    print_info_log("Tabulating the results.", "process")
    reg_panel = generate_panel()
    reg_panel = generate_sum(reg_panel)
    generate_reg(reg_panel)
