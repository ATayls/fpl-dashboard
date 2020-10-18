import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app


control = dbc.Row(
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Input(id="input", placeholder="Input League Id...", type="number"),
                dbc.Button(
                    "Generate for League Id",
                    color="primary",
                    block=True,
                    id="button1",
                ),
            ]
        ),
        outline=False,
        color='light',
        className="w-100 mb-3",
    ),
)


analysis = html.Div([
    dbc.Row(
        [
            dbc.Tabs(
                [
                    dbc.Tab(label="League Rankings", tab_id="rank"),
                    dbc.Tab(label="Percentage Ownership", tab_id="prc_own"),
                    dbc.Tab(label="Transfers In", tab_id="trans_in"),
                    dbc.Tab(label="Transfers Out", tab_id="trans_out"),
                    dbc.Tab(label="Captains", tab_id="captains"),
                    dbc.Tab(label="Manager Correlation", tab_id="man_corr"),
                    dbc.Tab(label="Manager Points", tab_id="man_box"),

                ],
                id="tabs",
                active_tab="prc_own",
            ),
            html.Div(id="tab-content"),
        ]
    )
])