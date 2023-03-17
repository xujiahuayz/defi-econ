import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from environ.constants import FIGURE_PATH, TABLE_PATH

# create the correlation matrix and set the decimal places to 2 and keep the digits
corr = summary_panel.corr().round(4)

# create the covariance matrix and set the decimal places to 2 and keep the digits
cov = summary_panel.cov().round(4)

# # drop the lagged columns
# corr = corr.drop(
#     [f"{i}_lag" for i in col_list],
#     axis=1,
# )

# # drop the non-lagged columns
# corr = corr.drop(
#     col_list,
#     axis=0,
# )

# # change the column names to be more readable
# corr = corr.rename(columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE)

# set the borrow_rate, borrow_rate to 1
# corr.loc["${\it BorrowAPY}^{USD}$", "${\it BorrowAPY}^{USD}$"] = 1

# This dictionary defines the colormap
cdict3 = {
    "red": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.5, 0.8, 1.0),
        (0.75, 1.0, 1.0),
        (1.0, 0.4, 1.0),
    ),
    "green": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.5, 0.9, 0.9),
        (0.75, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    ),
    "blue": (
        (0.0, 0.0, 0.4),
        (0.25, 1.0, 1.0),
        (0.5, 1.0, 0.8),
        (0.75, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    ),
    "alpha": ((0.0, 1.0, 1.0), (0.5, 0.3, 0.3), (1.0, 1.0, 1.0)),
}

# Create the colormap using the dictionary with the range of -1 to 1
# make sure the range of the ledgend is -1 to 1
GnRd = colors.LinearSegmentedColormap("GnRd", cdict3)

sns.heatmap(
    corr,
    xticklabels=corr.columns,
    yticklabels=corr.columns,
    annot=True,
    cmap=GnRd,
    vmin=-1,
    vmax=1,
    annot_kws={"size": 4},
)

# font size smaller
plt.rcParams.update({"font.size": 4})

# tight layout
plt.tight_layout()

if lag:
    # save the figure
    plt.savefig(
        rf"{FIGURE_PATH}/correlation_matrix_{file_name}_{lag_num}_lag_{status}.pdf"
    )
    plt.clf()
else:
    # save the figure
    plt.savefig(rf"{FIGURE_PATH}/correlation_matrix_{file_name}.pdf")
    plt.clf()

# save the correlation matrix as a csv file
corr.to_csv(rf"{TABLE_PATH}/correlation_matrix_{file_name}.csv")

if lag:
    # plot the heatmap for the covariance matrix
    sns.heatmap(
        cov,
        xticklabels=cov.columns,
        yticklabels=cov.columns,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 4},
    )

    # font size smaller
    plt.rcParams.update({"font.size": 4})

    # tight layout
    plt.tight_layout()

    # save the figure
    plt.savefig(
        rf"{FIGURE_PATH}/covariance_matrix_{file_name}_{lag_num}_lag_{status}.pdf"
    )
    plt.clf()
