import uuid
import time
import shutil

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app, DATA_STORE
from layouts import control, analysis
from loading_loop import progress

header = dbc.Row(
    dbc.Col(
        html.H1("FPL League Dashboard", className="bg-primary text-center text-white font-weight-bold"),
    )
)

app.layout = dbc.Container(
    [
        html.Div(str(uuid.uuid4()), id='session_id', style={'display': 'none'}),
        html.Div(id='data_store_success', style={'display': 'none'}),
        header,
        control,
        progress,
        analysis,
    ]
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


if __name__ == '__main__':
    app.run_server(debug=True)
