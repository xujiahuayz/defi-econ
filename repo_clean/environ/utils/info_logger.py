"""

University College London
Project : defi_econ
Topic   : info_logger
Author  : Yichen Luo
Date    : 2022-12-17
Desc    : print info log in the terminal.

"""

import datetime

# -- Print info log
# --- helper/util function for logging script info into console
# args:
#   type = 'progress'
#   msg = 'test message'


def print_info_log(msg, type):
    now_time = datetime.datetime.now()
    msg_out = (
        now_time.strftime("%Y-%m-%d %H:%M:%S")
        + " --- [ "
        + type.upper()
        + " ] --- "
        + msg
    )
    print(msg_out)
