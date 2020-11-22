import dash
import dash_bootstrap_components as dbc
from pathlib import Path

app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])
server = app.server

DATA_STORE = Path().resolve().joinpath('data')