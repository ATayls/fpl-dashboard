from dash import callback_context
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
import dash_core_components as dcc

import pandas as pd

from app import app
from fpl_api_utils import league_dataframe
from plots import create_graphs


control = dbc.Row(
    [
        html.Div(id='manager-list', style={'display': 'none'}),
        html.Div(id='manager-df-path', style={'display': 'none'}),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Input(id="league-id", placeholder="Input League Id...", type="number"),
                    dbc.Button(
                        "Load League Data",
                        color="primary",
                        block=True,
                        id="run-button",
                    ),
                ]
            ),
            outline=False,
            color='light',
            className="w-100 mb-3",
        ),
    ]
)

gameweek_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Ownership", tab_id="prc-own"),
                dbc.Tab(label="Transfers In", tab_id="trans-in"),
                dbc.Tab(label="Transfers Out", tab_id="trans-out"),
                dbc.Tab(label="Captains", tab_id="captains"),
                dbc.Tab(label="Manager Correlation", tab_id="man-corr"),

            ],
            id="gameweek-tabs",
            active_tab="prc-own",
            className='mt-3'
        ),
        html.Div(id="gameweek-tab-content"),
    ]
)


season_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="League Rankings", tab_id="rank"),
                dbc.Tab(label="Manager Points", tab_id="man-box"),

            ],
            id="season-tabs",
            active_tab="rank",
            className='mt-3'
        ),
        html.Div(id="season-tab-content"),
    ]
)


analysis = html.Div(
    [
        dcc.Store(id="fig_store"),
        html.Div(
            [
                dbc.Row(
                    dbc.Col(
                        html.H1(id='league-name', className='text-center font-weight-bold'),
                        width={'size': 6, 'offset': 3}
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            "Display League Table",
                            id="collapse-button",
                            className="mb-3 text-center",
                            color="primary",
                            block=True,
                        ),
                        width={'size': 4, 'offset': 4},
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Collapse(
                            dbc.Card(
                                dash_table.DataTable(id='league-table')
                            ),
                            id="collapse",
                        ),
                    ),
                    justify='center'
                ),
            ],
            id='hidden-analysis-div',
            style={'display': 'none'}
        ),
        dbc.Row(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(season_tabs, label="Season Overview", tab_id="season"),
                        dbc.Tab(gameweek_tabs, label='Gameweek Analysis', tab_id='gws'),
                    ]
                ),
            ]
        )
    ],
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output("league-table", "data"), Output("league-table", "columns"),
     Output("manager-list", "children"), Output("hidden-analysis-div", "style"),
     Output("league-name", "children")],
    [Input("run-button", "n_clicks"), State("league-id", "value")]
)
def run(n_clicks, l_id):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    league_df, name = league_dataframe(l_id)
    columns = [{"name": i, "id": i} for i in league_df.columns]
    manager_list = league_df['entry'].to_list()
    return league_df.to_dict('records'), columns, manager_list, {'display': 'block'}, name


@app.callback(
    [Output("season-tab-content", "children"), Output("gameweek-tab-content", "children")],
    [Input("season-tabs", "active_tab"), Input("gameweek-tabs", "active_tab"), Input("fig_store", "data")],
)
def render_tab_content(active_season_tab, active_gw_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if data is not None:
        return dcc.Graph(figure=data[active_season_tab]), dcc.Graph(figure=data[active_gw_tab])

    return "Data Not Generated", "Data Not Generated"


@app.callback(
    Output("fig_store", "data"),
    [Input("load-complete", "children"), State("manager-df-path", "children")]
)
def create_figures(loaded, df_path):
    if loaded:
        stored_df = pd.read_feather(df_path)
        return create_graphs(stored_df)
    else:
        raise PreventUpdate
