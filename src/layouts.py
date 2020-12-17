from dash import callback_context
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
import dash_core_components as dcc
from dash.dash import no_update

import pandas as pd
from requests import HTTPError

from app import app
from fpl_api_utils import league_dataframe, get_played_gameweeks
from loading_loop import progress
from plots import create_graphs

about_tab = dbc.Card(
    dbc.CardBody(
        [
            html.H4("About League Dashboard"),
            html.Br(),
            html.P(""" This dashboard aims to give you a more complete overview of the activity in your FPL
            league. Input your league id on the Input Tab to load the manager data into the dashboard.
            To find your league id: """),
            html.P("1. Log into the Official Fantasy Premier League site. Link below"),
            html.P("2. Click on the 'League' of interest."),
            html.P("3. Look for the number in the URL of that webpage. That is the unique FPL league ID."),
            dbc.Button("FPL Leagues", color="info", external_link=True, target="_blank", className="text-center",
                       href="https://fantasy.premierleague.com/leagues")
        ]
    )
)

input_tab = dbc.Card(
    dbc.CardBody(
        [
            dcc.Loading(
                dcc.Store(id='manager-list'),
                id='loading-1', type="default", className='text-center'
            ),
            html.Br(),
            dcc.Store(id='manager-df-path'),
            dcc.Store(id='gw-list'),
            dbc.Input(id="league-id", placeholder="Input League Id...", type="number"),
            dbc.Button(
                "Load League Data",
                color="primary",
                block=True,
                id="run-button",
            ),
            html.Br(),
            progress,
            html.Br(),
            dcc.RangeSlider(
                id='gw-slider',
                min=1,
                max=39,
                step=1,
                value=[1, 39],
            )
        ]
    ),

)

league_table = html.Div(
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
                    color="info",
                    block=True,
                ),
                width={'size': 4, 'offset': 4},
            ),
        ),
        dbc.Row(
            dbc.Col(
                dbc.Collapse(
                    dbc.Card(
                        dash_table.DataTable(id='league-table', style_as_list_view=True,
                                             style_cell={'textAlign': 'left', 'color': 'black'},)
                    ),
                    id="collapse",
                ),
            ),
            justify='center',
            className='mb-3'
        ),
    ],
    id='hidden-analysis-div',
    style={'display': 'none'}
)

gameweek_tabs = html.Div(
    [
        dbc.Form(
            [
                dbc.Label("Select Gameweek", html_for="gw-select"),
                dbc.Select(id="gw-select", className="ml-3", placeholder="Select Gameweek")
            ],
            inline=True,
            className="mt-3"
        ),
        dbc.Tabs(
            [
                dbc.Tab(label="Ownership", tab_id="prc-own",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Transfers In", tab_id="trans-in",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Transfers Out", tab_id="trans-out",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Captains", tab_id="captains",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Manager Correlation", tab_id="man-corr",
                        labelClassName="bg-primary text-white"),

            ],
            id="gameweek-tabs",
            active_tab="prc-own",
            className='mt-3'
        ),
        html.Div(id="gameweek-tab-content", className='mt-3'),
    ]
)


season_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="League Rankings", tab_id="rank",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="League Points", tab_id="total_points",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Manager Points", tab_id="points-box",
                        labelClassName="bg-primary text-white"),
                dbc.Tab(label="Team Value", tab_id="team-value",
                        labelClassName="bg-primary text-white"),

            ],
            id="season-tabs",
            active_tab="rank",
            className='mt-3'
        ),
        html.Div(id="season-tab-content", className='mt-3'),
    ]
)

control_tabs = dbc.Tabs(
    [
        dbc.Tab(about_tab, label="About", tab_id="a"),
        dbc.Tab(input_tab, label="Input", tab_id="i"),
    ],
    active_tab="i",
)

analysis = html.Div(
    [
        dcc.Store(id="fig_store"),
        league_table,
        dbc.Row(
            dbc.Col(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(season_tabs, label="Season Overview", tab_id="season",
                                    labelClassName="text-white"),
                            dbc.Tab(gameweek_tabs, label='Gameweek Analysis', tab_id='gws',
                                    labelClassName="text-white"),
                        ],
                        id="master-tabs"
                    ),
                ]
            )
        )
    ]
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
     Output("manager-list", "data"), Output("hidden-analysis-div", "style"),
     Output("gw-list", "data"), Output("league-name", "children"),
     Output("league-id", "valid"), Output("league-id", "invalid")],
    [Input("run-button", "n_clicks"), State("league-id", "value")]
)
def run(n_clicks, l_id):
    """
    Main entry callback. Triggered when user inputs league id and clicks run.
    :param n_clicks: Count of run clicks - used as callback trigger
    :param l_id: league id input in input field
    :return:
    """
    if l_id is None:
        raise PreventUpdate
    try:
        league_df, name = league_dataframe(l_id, manager_limit=100)
    except HTTPError:
        return no_update, no_update, no_update, no_update, no_update, no_update, False, True

    columns = [{"name": i, "id": i} for i in league_df.columns]
    manager_list = [x for x in zip(league_df['entry'].to_list(), league_df['entry_name'].to_list())]
    gw_list = get_played_gameweeks(including_active=True)

    return league_df.to_dict('records'), columns, manager_list, {'display': 'block'}, gw_list, name, True, False


@app.callback(
    [Output("season-tab-content", "children"), Output("gameweek-tab-content", "children")],
    [Input("season-tabs", "active_tab"), Input("gameweek-tabs", "active_tab"),
     Input("master-tabs", "active_tab"), Input("fig_store", "data")],
)
def render_tab_content(active_season_tab, active_gw_tab, master_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if data is None:
        return "Data Not Generated", "Data Not Generated"

    if (master_tab == "gws") and (active_gw_tab in data):
        return "Unrendered", dcc.Graph(figure=data[active_gw_tab])
    elif (master_tab == "season") and (active_season_tab in data):
        return dcc.Graph(figure=data[active_season_tab]), "Unrendered"
    else:
        return "Graph Not Generated", "Graph Not Generated"


@app.callback(
    Output("fig_store", "data"),
    [Input("load-complete", "children"),
     Input("gw-select", "value"),
     Input("gw-slider", "value"),
     State("fpl-data-paths", "data"),
     State("manager-df-path", "data")]
)
def create_figures(loaded, gw, gw_slider, data_paths, df_path):
    if loaded:
        stored_df = pd.read_feather(df_path)
        stored_df = stored_df[(stored_df['gw']>=min(gw_slider)) & (stored_df['gw']<=max(gw_slider))]
        players_df = pd.read_feather(data_paths['players'])
        return create_graphs(stored_df, players_df, int(gw))
    else:
        raise PreventUpdate


@app.callback(
    [Output("gw-select", "options"), Output("gw-select", "value")],
    [Input("gw-slider", "value"), State("gw-select", "value")],
)
def populate_gw_select(slider_vals, current_val):
    if isinstance(slider_vals, list):
        options = [{'label': f'Gameweek {x}', 'value': str(x)} for x in range(slider_vals[0], slider_vals[1]+1)]
        if current_val is None:
            value = slider_vals[1]
        elif int(current_val) > slider_vals[1]:
            value = slider_vals[1]
        elif int(current_val) < slider_vals[0]:
            value = slider_vals[0]
        else:
            value = int(current_val)
        return options, value
    else:
        raise PreventUpdate

@app.callback(
    [Output("gw-slider", "max"), Output("gw-slider", "value"), Output("gw-slider", "marks")],
    [Input("gw-list", "data")]
)
def populate_gw_slider(gw_list):
    if isinstance(gw_list, list):
        return max(gw_list), [1, max(gw_list)], {x: {'label': f'GW{x}', 'style': {'color': '#ffffff'}} for x in gw_list}
    else:
        raise PreventUpdate
