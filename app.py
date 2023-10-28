"""

"""
import pandas as pd
from dash import Dash, dcc, html, callback, Output, Input
import figs as F
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

tabheight = 50
tabstyle = {
    # "padding": "0",
    # "line-height": tabheight,
    # "height": 25
}

app.layout = html.Div(
    [
        html.H1("Customer Obsession"),
        dcc.Tabs(
            id="tabs-example-graph",
            value="tab-summary",
            children=[
                dcc.Tab(label="Executive Summary", value="tab-summary", style=tabstyle),
                dcc.Tab(
                    label="Explore an Individual Letter", value="tab-single-page", style=tabstyle
                ),
                dcc.Tab(label="Search for a Term", value="tab-explore", style=tabstyle),
            ],
            # style={"height": tabheight},
        ),
        html.Div(id="tabs-content-example-graph"),
    ]
)


@callback(
    Output("tabs-content-example-graph", "children"),
    Input("tabs-example-graph", "value"),
)
def render_content(tab):
    return {
        "tab-summary": mainpage(),
        "tab-explore": explorepage(),
        "tab-single-page": singlepage(),
    }[tab]


def singlepage():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    html.H3("Sentiment over the document", id="individual_page_title"),
                                    html.Span(
                                        "View the source file by selecting from the dropdown below:"
                                    ),
                                    dcc.Dropdown(
                                        F.ALL_PDFS, F.ALL_PDFS[0]['value'], id="dropdown-pdf"
                                    ),
                                    dcc.Graph("sentiment-summary"),
                                    dcc.Graph("sentiment-graph"),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.H3("Top and Bottom 3 Passages"),
                                    dcc.Graph("sentiment-top-chunks"),
                                ]
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Iframe(
                                id="embedded-pdf",
                                style={"width": "100%", "height": 1000},
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
        ]
    )


def mainpage():
    return html.Div(
        children=[
            html.H3(
                ["I downloaded and analyzed all of Amazon's customer shareholder letters and this site is the result of my analysis.", html.Br(), "My key finding? Jeff Bezos' best friend is the customer."],
                className='key-finding'
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P(
                                        "The letters take around 20 minutes to read, a bit quicker from 2006 to 2013. Interestingly, the 2 most recent letters that are also the longest have been authored by the new CEO, Andy Jassy.",
                                        className="side-note",
                                    )
                                ],
                                width=2,
                            ),
                            dbc.Col([dcc.Graph(figure=F.timetoread())], width=10),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [html.P(
                                    "They are mostly filled with neutral statements, and 2005 and 2009 had the highest percent of statements with positive sentiment.", 
                                    className='side-note'
                                    )],
                                width=2,
                            ),
                            dbc.Col([dcc.Graph(figure=F.alllettersfig())], width=10),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P(
                                        'Jeff B. is not kidding when he says customers are key, the data shows that the word "Customer" is consistently the most common word used in the letters.',
                                        className='side-note'
                                    )
                                ],
                                width=2,
                            ),
                            dbc.Col([dcc.Graph(figure=F.wordtimeseries())], width=10),
                        ]
                    ),
                ]
            ),
        ],
        style={"margin": 50},
    )


def explorepage():
    return (
        html.Div(
            [
                html.H3(
                    "You can use this page to search for particular words, or view the most common words.",
                    id='word_search_title'
                ),
                html.Div(
                    [
                        html.Span("Enter a search term here: "),
                        dcc.Input(
                            id="concordance_input",
                            type="text",
                            placeholder="",
                            value="customer",
                            style={"marginRight": "10px"},
                        ),
                        html.Button(
                            "Search",
                            id="submit-val",
                            n_clicks=0,
                        ),
                    ]
                ),
                dcc.Graph(id="concordance_output"),
                dcc.Graph(id="concordance_table"),
            ]
        ),
    )



if __name__ == "__main__":
    app.run_server(dev_tools_hot_reload=False)
