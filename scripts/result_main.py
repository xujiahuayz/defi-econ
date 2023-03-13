"""

University College London
Project : defi_econ
Topic   : result_tabulator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Tabulate the results.

"""

from environ.tabulate.panel.panel_generator import generate_panel
from environ.tabulate.summary.sum_generator import generate_sum, generate_sum_herfindahl
from environ.tabulate.panel.unit_of_acct import unit_of_acct
from environ.tabulate.regression.reg_generator import (
    generate_reg_property_of_dominance,
    generate_unit_of_account,
    generate_regression_herfindahl,
    generate_regression_herfindahl_boom_bust,
    generate_regression_specification,
    realized_holding_period,
)
from environ.tabulate.panel.series_herfin import generate_series_herfin
from environ.tabulate.panel.safeness_measurement import merge_safeness_measurement
from environ.tabulate.regression.reg_generator import change_in_r_squared
from environ.utils.info_logger import print_info_log

if __name__ == "__main__":
    """
    Tabulate the results.
    """

    print_info_log("Tabulating the results.", "process")

    # Generate the panel
    print_info_log("Generating the panel.", "process")
    reg_panel = generate_panel()
    print_info_log("Generating the series for Herfindahl index.", "process")
    reg_herfin = generate_series_herfin()

    # Extra factors
    print_info_log("Merging the safeness measurement.", "process")
    reg_panel = merge_safeness_measurement(reg_panel)
    print_info_log("Merging the unit-of-account.", "process")
    reg_panel = unit_of_acct(reg_panel)

    # Summary statistics
    print_info_log("Generating the summary for properties of dominance.", "process")
    reg_panel = generate_sum(reg_panel, file_name="properties_of_dominance", lag=True)
    print_info_log("Generating the summary for herfindal series.", "process")
    reg_herfin = generate_sum_herfindahl(reg_herfin, file_name="herfindahl_index")

    # Regression: properties of dominance
    print_info_log("Generating the regressions of properties of dominance.", "process")

    # full panel
    generate_reg_property_of_dominance(reg_panel, file_name="full_sample", lag=False)

    # two subsamples before and after the defi summer 2021
    generate_reg_property_of_dominance(
        reg_panel[reg_panel["Date"] < "2021-06-01"],
        file_name="two_subsamples_before_summer",
        lag=False,
    )
    generate_reg_property_of_dominance(
        reg_panel[reg_panel["Date"] >= "2021-06-01"],
        file_name="two_subsamples_after_summer",
        lag=False,
    )

    # three subsamples before defi summer 2021, after defi
    # summer 2021 and before the luna crisis, and after the luna crisis
    generate_reg_property_of_dominance(
        reg_panel[reg_panel["Date"] < "2021-06-01"],
        file_name="three_subsamples_before_summer",
        lag=False,
    )
    generate_reg_property_of_dominance(
        reg_panel[
            (reg_panel["Date"] >= "2021-06-01") & (reg_panel["Date"] < "2022-05-10")
        ],
        file_name="three_subsamples_after_summer_before_luna",
        lag=False,
    )
    generate_reg_property_of_dominance(
        reg_panel[reg_panel["Date"] >= "2022-05-10"],
        file_name="three_subsamples_after_luna",
        lag=False,
    )

    # Regression: unit-of-account
    print_info_log("Generating the unit-of-account regreesion.", "process")
    generate_unit_of_account(reg_panel)

    # Regression: herfindahl index
    print_info_log("Generating the regression of herfindahl index.", "process")
    generate_regression_herfindahl(reg_herfin, lag=True, standardized=True)

    # Regression: herfindahl index (boom-bust)
    print_info_log(
        "Generating the regression of herfindahl index (boom-bust).", "process"
    )
    generate_regression_herfindahl_boom_bust(reg_herfin, lag=True, standardized=True)

    # Regression: specification
    print_info_log("Generating the regression of specification.", "process")
    generate_regression_specification(reg_panel, lag=True)

    # Regression: realized holding period
    print_info_log("Generating the regression of realized holding period.", "process")
    realized_holding_period(reg_panel, lag=True)

    # Change in r-squared
    print_info_log("Generating the change in r-squared.", "process")
    change_in_r_squared(reg_panel)
