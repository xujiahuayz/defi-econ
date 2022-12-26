"""

University College London
Project : defi_econ
Topic   : info_logger
Author  : Yichen Luo
Date    : 2022-12-17
Desc    : print info log in the terminal.

"""

# Import python modules
import datetime

# -- Print info log
# --- helper/util function for logging script info into console
# args:
#   category = 'progress'
#   msg = 'test message'


def print_info_log(msg: str, category: str) -> None:

    """
    Print information in terminal
    """

    now_time = datetime.datetime.now()
    msg_out = (
        now_time.strftime("%Y-%m-%d %H:%M:%S")
        + " --- [ "
        + category.upper()
        + " ] --- "
        + msg
    )
    print(msg_out)
