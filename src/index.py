import uuid
import time
import shutil

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc

from app import app, DATA_STORE
from layouts import control_tabs, analysis
from fpl_api_utils import get_bootstrap_static_dataframes

header = dbc.Row(
    [
        dbc.Col(
            html.H2("FPL League Dashboard", className="font-weight-bold text-center"),
            width=12,
        ),
    ],
    no_gutters=True,
    align="center",
    id="header"
)

app.layout = dbc.Container(
    [
        html.Div(str(uuid.uuid4()), id='session_id', style={'display': 'none'}),
        html.Div(id='data_store_success', style={'display': 'none'}),
        dcc.Store(id="fpl-data-paths"),
        header,
        # dbc.Row(
        #     [
        dbc.Col(
            control_tabs,
            width=12
        ),
        dbc.Col(
            analysis,
            width=12
        )
        #     ]
        # ),
    ],
    fluid=True
)


@app.callback(
    Output('data_store_success', "children"),
    [Input("session_id", "children")]
)
def create_session_store(session_id):
    def reset_datastore():
        time_stamps = DATA_STORE.glob(r'*\*.txt')
        for ts in time_stamps:
            creation_time = float(ts.stem)
            if (time.time() - creation_time) > 5 * 60:
                shutil.rmtree(ts.parent, ignore_errors=True)

    session_store = DATA_STORE.joinpath(session_id)
    if not session_store.exists():
        session_store.mkdir(parents=True, exist_ok=True)
        ts = session_store.joinpath(f'{time.time()}.txt')
        with open(ts, 'w') as fh:
            pass
    reset_datastore()
    if session_store.exists():
        return True
    else:
        return False


@app.callback(
    Output("fpl-data-paths", "data"),
    [Input('data_store_success', "children"), State("session_id", "children")],
    prevent_initial_call=True
)
def retrieve_player_data(trigger, session_id):
    if trigger is None:
        raise PreventUpdate
    paths = {
        'players': DATA_STORE.joinpath(session_id, 'players.feather'),
        'teams': DATA_STORE.joinpath(session_id, 'teams.feather'),
        'events': DATA_STORE.joinpath(session_id, 'events.feather'),
    }
    if not all([path.exists() for path in paths.values()]):
        players, teams, events = get_bootstrap_static_dataframes()

        players.to_feather(paths['players'])
        teams.to_feather(paths['teams'])
        events.to_feather(paths['events'])

    return {item[0]: str(item[1]) for item in paths.items()}



if __name__ == '__main__':
    app.run_server(debug=True)
