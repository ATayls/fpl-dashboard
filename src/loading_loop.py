import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd

from app import app, DATA_STORE
from fpl_api_utils import scrape_manager_team

progress = html.Div(
    [
        dcc.Interval(id="progress-interval", interval=0.5*1000, disabled=False),
        html.Div(id="latest-output", style={'display': 'none'}),
        html.Div(id="progress-output", style={'display': 'none'}),
        html.Div(0, id="run-index", style={'display': 'none'}),
        html.Div(id="load-complete", style={'display': 'none'}),
        dbc.Progress(id="progress", striped=True, className='mb-3'),
    ]
)


@app.callback(
    Output("run-index", "children"),
    [Input("progress-interval", "n_intervals"), State("latest-output", "children"), State("run-index", "children")]
)
def check(interval_trigger, latest_output, run_index):
    if run_index != latest_output:
        raise PreventUpdate
    else:
        return run_index+1


@app.callback(
    [Output("progress", "value"), Output("latest-output", "children"),
     Output("manager-df-path", "children"), Output("progress", "children")],
    [Input("manager-list", "children"), Input("run-index", "children"),
     State("session_id", "children"), State("manager-df-path", "children")]
)
def run(list_input, run_index, session_id, df_path):
    if list_input is None:
        raise PreventUpdate
    elif run_index >= len(list_input):
        raise PreventUpdate

    entry_id = list_input[run_index]
    gw_list = [1, 2, 3]

    manager_df = scrape_manager_team(entry_id, gw_list)
    manager_df['manager'] = entry_id

    if df_path is not None:
        stored_df = pd.read_feather(df_path)
        manager_df = pd.concat([stored_df, manager_df]).reset_index(drop=True)
    else:
        df_path = DATA_STORE.joinpath(session_id, 'manager_df.feather')

    manager_df.to_feather(df_path)
    progress_val = ((run_index+1)/len(list_input))*100
    progress_str = f"{run_index+1}/{len(list_input)}" if progress_val >= 5 else ""
    return progress_val, run_index, str(df_path), progress_str


@app.callback(
    [Output("progress-interval", "disabled"), Output("load-complete", "children")],
    [Input("manager-list", "children"), Input("progress", "value")]
)
def stop_interval(list_input, progress):
    if list_input is None:
        raise PreventUpdate

    if progress >= 100:
        return True, True
    else:
        return False, False
