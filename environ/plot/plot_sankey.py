"""
Function to plot the sankey diagram
"""
from ast import literal_eval

import plotly.graph_objects as go
import pandas as pd

from environ.constants import KEY_TOKEN_LIST


def plot_sankey(
    data_path: str,
    save_path: str,
):
    """
    Function to plot the sankey diagram
    """

    # load the data
    data = pd.read_csv(
        data_path,
        index_col=0,
    )

    # exclude the label with error
    data = data[data["label"] != "Error"]

    # convert the voliume_usd columns to float
    data["volume_usd"] = data["volume_usd"].apply(float)

    # convert the intermediary columns to list
    data["intermediary"] = data["intermediary"].apply(literal_eval)

    # convert the route columns to list
    data["route"] = data["route"].apply(literal_eval)

    key_token_list = KEY_TOKEN_LIST + ["Others"]

    # get the unique list of ultimate_source, ultimate_target, and intermediary
    unique_lst = (
        [f"{i}_S" for i in key_token_list]
        + [f"{i}_B" for i in key_token_list]
        + [f"{i}_T" for i in key_token_list]
    )

    # lists to store the source and target
    source_lst = []
    target_lst = []
    value_lst = []

    # iterate through the dataframe
    for _, row in data.iterrows():
        source_idx = (
            unique_lst.index(f"{row['ultimate_source']}_S")
            if row["ultimate_source"] in key_token_list
            else unique_lst.index("Others_S")
        )
        target_idx = (
            unique_lst.index(f"{row['ultimate_target']}_T")
            if row["ultimate_target"] in key_token_list
            else unique_lst.index("Others_T")
        )

        if len(row["intermediary"]) != 0:
            for i in row["intermediary"]:
                # get the source and between index

                between_idx = (
                    unique_lst.index(f"{i}_B")
                    if i in key_token_list
                    else unique_lst.index("Others_B")
                )
                source_lst.append(source_idx)
                target_lst.append(between_idx)
                value_lst.append(row["volume_usd"])
                source_lst.append(between_idx)
                target_lst.append(target_idx)
                value_lst.append(row["volume_usd"])

        else:
            source_lst.append(source_idx)
            target_lst.append(target_idx)
            value_lst.append(row["volume_usd"])

    # create a dataframe
    df_sankey = pd.DataFrame(
        {
            "source": source_lst,
            "target": target_lst,
            "value": value_lst,
        }
    )

    # group by the source and target
    df_sankey = df_sankey.groupby(["source", "target"])["value"].sum().reset_index()

    # remove _S, _B, _T in the unique list
    unique_lst = [i.split("_")[0] for i in unique_lst]

    # create the figure
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=unique_lst,
                    color="blue",
                ),
                link=dict(
                    source=df_sankey["source"],
                    target=df_sankey["target"],
                    value=df_sankey["value"],
                ),
            )
        ]
    )

    # save the figure into jpg
    fig.write_image(save_path)
