import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app
from layouts import control, analysis
from loading_loop import progress

header = dbc.Row(
    dbc.Col(
        html.H1("FPL League Dashboard", className="bg-primary text-center text-white font-weight-bold"),
    )
)

app.layout = dbc.Container(
    [
        header,
        control,
        progress,
        analysis,
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
