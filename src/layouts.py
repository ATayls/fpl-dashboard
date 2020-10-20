from dash import callback_context
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table

from app import app
from fpl_api_utils import league_dataframe


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

graph_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="League Rankings", tab_id="rank"),
                dbc.Tab(label="Ownership", tab_id="prc_own"),
                dbc.Tab(label="Transfers In", tab_id="trans_in"),
                dbc.Tab(label="Transfers Out", tab_id="trans_out"),
                dbc.Tab(label="Captains", tab_id="captains"),
                dbc.Tab(label="Manager Correlation", tab_id="man_corr"),
                dbc.Tab(label="Manager Points", tab_id="man_box"),

            ],
            id="tabs",
            active_tab="prc_own",
            className='mt-3'
        ),
        html.Div(id="graph-tab-content"),
    ]
)


analysis = html.Div(
    [
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
                        dbc.Tab(label="Season Overview", tab_id="season"),
                        dbc.Tab(graph_tabs, label='Gameweek Analysis', tab_id='gws'),
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
