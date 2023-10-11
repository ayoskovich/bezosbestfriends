"""

"""
import pandas as pd
from dash import Dash, dcc, html
import figs as F
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        html.H1(children="Customer Obsession"),
        html.P(children=("This is the result of all shareholder letters from Amazon.")),
        html.Div([
            dbc.Row([
                dbc.Col([dcc.Graph(figure=F.rawtable())], width=6),
                dbc.Col([dcc.Graph(figure=F.nwordshist())], width=6)
            ]),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=F.nwordscatter())], width=6),
                dbc.Col([
                    dcc.Input(id="nmostcommon", type="text", placeholder="", style={'marginRight':'10px'}),
                    html.Button("Update", id="topnwordbutton", n_clicks=0),
                    dcc.Graph(id='mostcommonfig', figure=F.blank_fig())
                    ], width=6)
            ]),
        ]),
        html.Div([
            dcc.Input(id="concordance_input", type="text", placeholder="", style={'marginRight':'10px'}),
            html.Button("Search!", id="submit-val", n_clicks=0, ),
        ]),
        dcc.Graph(id='concordance_output', figure=F.blank_fig())
    ],
    style={'margin': 50}
)

if __name__ == "__main__":
    app.run_server(debug=True)