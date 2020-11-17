import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

import pandas as pd

from app import app, DATA_STORE
from fpl_api_utils import scrape_manager_team

progress = html.Div(
    [
        dcc.Interval(id="progress-interval", interval=0.5*1000, disabled=True),
        html.Div(id="latest-processed-index", style={'display': 'none'}),
        html.Div(id="progress-output", style={'display': 'none'}),
        html.Div(0, id="run-index", style={'display': 'none'}),
        html.Div(id="load-complete", style={'display': 'none'}),
        dbc.Progress(id="progress", striped=True, className='mb-3'),
    ]
)


@app.callback(
    Output("run-index", "children"),
    [Input("progress-interval", "n_intervals"), Input("manager-list", "data"),
     State("latest-processed-index", "children"), State("run-index", "children")]
)
def iterate_index(interval_trigger, list_input, latest_processed_index, run_index):
    """
    Callback to iterate through the list indices. Steps to next index when latest_processed_index from loop_contents is
    equal to the current run index. Triggered regularly by interval component to check if loop contents has completed
    and ready to receive next run_index.
    :param interval_trigger: interval component triggering the callback at regular intervals.
    :param list_input: used to trigger when user submits new manager list. Resets run_index to zero
    :param latest_processed_index: most recent list index loop contents has successfull processed
    :param run_index: current run index
    :return:
    """
    ctx = callback_context
    if ctx.triggered[0]['prop_id'] == "manager-list.data":
        return 0
    elif run_index != latest_processed_index:
        raise PreventUpdate
    else:
        return run_index+1


@app.callback(
    [Output("progress", "value"), Output("latest-processed-index", "children"),
     Output("manager-df-path", "data"), Output("progress", "children")],
    [Input("run-index", "children"), State("manager-list", "data"), State("gw-list", "data"),
     State("session_id", "children"), State("manager-df-path", "data")]
)
def loop_contents(run_index, list_input, gw_list, session_id, df_path):
    """
    Main processing contents of loop.
    Given an index 'run_index' to the list 'list_input', extracts from list and processes.
    Scrapes manager team and saves to feather.
    Updates progress bar.
    :param run_index:
    :param list_input:
    :param gw_list:
    :param session_id:
    :param df_path:
    :return:
    """
    if list_input is None:
        raise PreventUpdate
    elif run_index >= len(list_input):
        raise PreventUpdate

    entry_id, entry_name = list_input[run_index]

    manager_df = scrape_manager_team(entry_id, gw_list)
    manager_df['manager'] = entry_id
    manager_df['team_name'] = entry_name

    if df_path is not None:
        stored_df = pd.read_feather(df_path)
        manager_df = pd.concat([stored_df, manager_df]).reset_index(drop=True)
        manager_df = manager_df.drop_duplicates()
    else:
        df_path = DATA_STORE.joinpath(session_id, 'manager_df.feather')

    manager_df.to_feather(df_path)
    progress_val = ((run_index+1)/len(list_input))*100
    progress_str = f"{run_index+1}/{len(list_input)}" if progress_val >= 5 else ""
    latest_processed_index = run_index
    return progress_val, latest_processed_index, str(df_path), progress_str


@app.callback(
    [Output("progress-interval", "disabled"), Output("load-complete", "children")],
    [Input("manager-list", "data"), Input("progress", "value")]
)
def start_stop_interval(list_input, progress):
    """
    Callback to start/stop the interval component which controls the run_index iteration.
    :param list_input: manager list
    :param progress: progress bar value
    :return:
    """
    ctx = callback_context
    if ctx.triggered[0]['prop_id'] == "manager-list.data":
        return False, False

    if list_input is None:
        raise PreventUpdate

    if progress >= 100:
        return True, True
    elif progress < 100:
        return False, False
    else:
        raise PreventUpdate