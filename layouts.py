from dash import dcc, html
from dash.dash_table import DataTable

from app import get_df

_flex_style = {"display": "flex", "flex-direction": "row"}


def _stores() -> html.Div:
    """Stores"""
    store_current_page = dcc.Store(id="current-page", data=0)
    store_data_sample = dcc.Store(id="data-sample")
    layout_stores = html.Div(
        [store_current_page, store_data_sample], style={"display": "none"}
    )
    return layout_stores


def _layout_filters() -> html.Div:
    """Layout for filters"""
    button_add_filter = html.Div(
        "Add filter",
        id="btn-add-filter",
        style={
            "font-size": "20px",
            "backgroundColor": "#007FFF",
            "width": "100px",
            "color": "#FFFFFF",
            "textAlign": "center",
        },
        n_clicks=0,
    )
    filter_container = html.Div(id="filter-container", children=[])

    layout_filters = html.Div([button_add_filter, filter_container], style=_flex_style)
    layout_center = html.Div(
        layout_filters,
        style={
            "display": "block",
            "width": "50%",
            "margin-left": "auto",
            "margin-right": "auto",
        },
    )
    return layout_center


def _layout_table() -> html.Div:
    df = get_df()
    button_display_table = html.Button(
        "Display Table",
        id="btn-display-table",
        n_clicks=0,
    )
    txt_select_fields = dcc.Markdown("Select fields to display:")
    dropdown_fields = dcc.Dropdown(
        options=df.columns,
        value=df.columns[1:],
        id="dpd-fields",
        multi=True,
        style={"margin-left": "2%"},
    )
    layout_fields = html.Div(
        [txt_select_fields, dropdown_fields],
        style={
            "margin-left": "auto",
            "margin-right": "auto",
            "width": "60%",
            **_flex_style,
        },
    )
    txt_numb_rows = dcc.Markdown("Number of rows:")
    input_numb_rows = dcc.Input(
        value=5,
        placeholder="rows",
        type="number",
        id="num-rows",
        debounce=True,
        style={"textAlign": "center", "width": "50px"},
    )
    layout_numb_rows = html.Div([txt_numb_rows, input_numb_rows], style=_flex_style)

    button_first_page = html.Button(
        "<<",
        id="first-page",
        n_clicks=0,
        style={"width": "50px", "textAlign": "center"},
    )
    button_previous_page = html.Button(
        "<",
        id="previous-page",
        n_clicks=0,
        style={"width": "50px", "textAlign": "center"},
    )
    button_next_page = html.Button(
        ">", id="next-page", n_clicks=0, style={"width": "50px", "textAlign": "center"}
    )
    button_last_page = html.Button(
        ">>", id="last-page", n_clicks=0, style={"width": "50px", "textAlign": "center"}
    )
    input_page_number = dcc.Input(
        value=0,
        type="number",
        placeholder="page",
        id="input-page",
        debounce=True,
        style={"textAlign": "center", "width": "50px"},
    )
    layout_pages = html.Div(
        [
            button_first_page,
            button_previous_page,
            input_page_number,
            button_next_page,
            button_last_page,
        ],
        style={"margin-left": "10%", **_flex_style},
    )
    layout_navi = html.Div(
        [layout_numb_rows, layout_pages],
        style={
            "display": "block",
            "margin-left": "auto",
            "margin-right": "auto",
            "width": "50%",
            **_flex_style,
        },
    )
    table = DataTable(
        id="table",
        style_cell_conditional=[
            {"if": {"column_id": c}, "textAlign": "left"} for c in ["Date", "Region"]
        ],
        style_data={"color": "black", "backgroundColor": "white"},
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#ABD3FF",
            }
        ],
        style_header={
            "backgroundColor": "#007FFF",
            "color": "white",
            "fontWeight": "bold",
        },
    )
    layout_table_content = html.Div(
        [layout_fields, layout_navi, html.Br(), table],
        id="layout-table-content",
    )
    layout_table = html.Div([button_display_table, html.Br(), layout_table_content])
    return layout_table


def _layout_figure() -> html.Div:
    button_display_figure = html.Button(
        "Display Figure",
        id="btn-display-figure",
        n_clicks=0,
    )
    fig = dcc.Graph(id="fig")
    layout_fig = html.Div([button_display_figure, fig])
    return layout_fig


def layout_server():
    title = html.H1(
        "Dash Demo: Life Expectancy vs GPD Per Capita",
        style={
            "display": "block",
            "width": "50%",
            "margin-left": "auto",
            "margin-right": "auto",
        },
    )
    stores = _stores()
    layout_filters = _layout_filters()
    layout_table = _layout_table()
    layout_fig = _layout_figure()

    layout = html.Div(
        [stores, title, layout_filters, html.Br(), layout_table, html.Br(), layout_fig]
    )
    return layout
