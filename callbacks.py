import json
import math
import operator

import dash
import pandas as pd
import plotly.express as px
from dash import ALL, Input, Output, State, dcc, html

from app import app, get_df

_base_button_style = {
    "width": "50%",
    "fontSize": "24px",
    "margin-left": "auto",
    "margin-right": "auto",
    "display": "block",
}
_blue_button_style = {
    "color": "#FFFFFF",
    "backgroundColor": "#007FFF",
    **_base_button_style,
}

op_mapping = {
    ">": operator.gt,
    ">=": operator.ge,
    "=": operator.eq,
    "<=": operator.le,
    "<": operator.lt,
}


@app.callback(
    Output("filter-container", "children"),
    [
        Input("btn-add-filter", "n_clicks"),
        Input({"type": "dynamic-delete", "index": ALL}, "n_clicks"),
    ],
    State("filter-container", "children"),
)
def update_filters(n_clicks, delete_clicks, children):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "dynamic-delete" in input_id:
        delete_idx = json.loads(input_id)["index"]
        children = [
            child for child in children if f"'index': {delete_idx}" not in str(child)
        ]
    else:
        df = get_df()
        new_field = dcc.Dropdown(
            df.columns,
            value=None,
            id={"type": "filter-field", "index": n_clicks},
            placeholder="Select a field to filter",
            style={"width": "250px"},
        )
        new_op = dcc.Dropdown(
            [">", ">=", "=", "<=", "<", "contains"],
            value="=",
            id={"type": "filter-op", "index": n_clicks},
            style={"textAlign": "Center", "width": "120px"},
        )
        new_input = dcc.Input(
            id={"type": "filter-value", "index": n_clicks},
            value=None,
            placeholder="Add filter value",
        )
        layout_filter = html.Div(
            [new_field, new_op, new_input],
            style={"display": "flex", "flex-direction": "row"},
        )
        new_add = html.Button(
            "Filter",
            id={"type": "filter-add", "index": n_clicks},
            n_clicks=0,
            style={"width": "100px", "textAlign": "center"},
        )
        new_delete = html.Button(
            "Remove",
            id={"type": "dynamic-delete", "index": n_clicks},
            n_clicks=0,
            style={"width": "100px", "textAlign": "center"},
        )
        new_buttons = html.Div([new_add, html.Br(), new_delete])
        new_child = html.Div(
            [layout_filter, new_buttons],
            style={"display": "flex", "flex-direction": "row"},
        )
        children.append(new_child)
    return children


@app.callback(
    Output("data-sample", "data"),
    Input({"type": "filter-add", "index": ALL}, "n_clicks"),
    [
        State({"type": "filter-field", "index": ALL}, "value"),
        State({"type": "filter-op", "index": ALL}, "value"),
        State({"type": "filter-value", "index": ALL}, "value"),
    ],
)
def update_sample(n_clicks, filter_fields, filter_ops, filter_values):
    idx = True
    df = get_df()
    for filter_field, filter_op, filter_value in zip(
        filter_fields, filter_ops, filter_values
    ):
        if not all((filter_field, filter_op, filter_values)):
            continue
        if filter_op == "contains":
            idx = idx & df[filter_field].str.upper().str.contains(filter_value.upper())
        else:
            value = cast_value(filter_value, filter_op, df[filter_field].dtype.name)
            idx = idx & op_mapping[filter_op](df[filter_field], value)

    df = get_df()
    if isinstance(idx, bool):
        df_selected = df
    else:
        df_selected = df[idx]
    return df_selected.to_json(orient="split")


def cast_value(value, op, dtype):
    if op != "=":
        return float(value)
    elif dtype.upper().startswith("INT"):
        return int(value)

    return value


@app.callback(
    [
        Output("table", "data"),
        Output("table", "columns"),
    ],
    [
        Input("data-sample", "data"),
        Input("dpd-fields", "value"),
        Input("num-rows", "value"),
        Input("current-page", "data"),
    ],
)
def display_data(data, fields, n_rows, current_page):
    df = pd.read_json(data, orient="split")
    df_selected = df.iloc[current_page * n_rows : (current_page + 1) * n_rows][fields]
    return df_selected.to_dict("records"), [
        {"name": i, "id": i} for i in df_selected.columns
    ]


@app.callback(
    [
        Output("current-page", "data"),
        Output("input-page", "value"),
    ],
    [
        Input("next-page", "n_clicks"),
        Input("previous-page", "n_clicks"),
        Input("first-page", "n_clicks"),
        Input("last-page", "n_clicks"),
        Input("num-rows", "value"),
        Input("input-page", "value"),
    ],
    State("current-page", "data"),
)
def update_page(
    next_clicks,
    previous_clicks,
    first_clicks,
    last_clicks,
    num_rows,
    input_page,
    current_page,
):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    df = get_df()
    max_page = math.ceil(len(df) / num_rows) - 1
    if input_id == "next-page":
        current_page += 1
    elif input_id == "previous-page":
        current_page -= 1
    elif input_id == "last-page":
        current_page = max_page
    elif input_id == "input-page":
        current_page = input_page
    else:
        current_page = 0
    page = min(max(current_page, 0), max_page)
    return page, page


@app.callback(
    [
        Output("btn-display-figure", "style"),
        Output("fig", "figure"),
        Output("fig", "style"),
    ],
    [
        Input("btn-display-figure", "n_clicks"),
        Input("data-sample", "data"),
    ],
)
def display_figure(n_clicks, data):
    if n_clicks % 2 == 0:
        style = _base_button_style
        fig = {}
        graph_style = {"display": "none"}
    else:
        style = _blue_button_style
        df = pd.read_json(data, orient="split")

        fig = px.scatter(
            df,
            x="gdp per capita",
            y="life expectancy",
            size="population",
            color="continent",
            hover_name="country",
            log_x=True,
            size_max=60,
        )
        fig.update_layout(transition_duration=500)
        graph_style = {}
    return style, fig, graph_style


@app.callback(
    [
        Output("btn-display-table", "style"),
        Output("layout-table-content", "style"),
    ],
    Input("btn-display-table", "n_clicks"),
)
def display_table(n_clicks):
    if n_clicks % 2 == 0:
        return _base_button_style, {"display": "none"}
    else:
        return _blue_button_style, {}
