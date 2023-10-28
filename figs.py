import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import glob

import nltk
nltk.download('vader_lexicon')

from datapipeline import alldata, wholetext, sentiment_frame
from dash import Input, callback, Output, State

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
import itertools

def clean_letter_name(lname) -> int:
    """Returns the number for a letters pathname."""
    clean_year = lname.replace("assets/Letter_", "")
    clean_year = int(clean_year.replace(".pdf", ""))
    return clean_year


ALL_PDFS = [
    {"label": f"{clean_letter_name(x)} Letter", "value": clean_letter_name(x)}
    for x in sorted(glob.glob("assets/*.pdf"))
]
DEFAULT_MARGINS = dict(l=0, r=0, t=40, b=40)
pio.templates.default = "simple_white"


def FIGBUILDER(*args, **kwargs):
    """Contains defaults for creating figures."""
    fig = go.Figure(*args, **kwargs)
    # fig.update_layout(margin=dict(DEFAULT_MARGINS))
    return fig


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def wordtimeseries():
    colnames = []

    most_commons = [
        # I came up with these in a notebook,
        # no point in running this over and over again.
        ("customer", 1231),
        ("amazon", 569),
        ("year", 471),
        ("term", 394),
        ("investment", 391),
    ]
    for word, count in most_commons:
        print(f"Creating word for {word}")
        _tempname = f"count_{word}"
        colnames.append(_tempname)
        alldata[_tempname] = alldata["text_object"].apply(lambda x: x.count(word))

    fig = (
        alldata.melt(id_vars=["pagenumber", "fname", "year"], value_vars=colnames)
        .groupby(["year", "variable"])["value"]
        .sum()
        .reset_index()
        .assign(variable=lambda x: x["variable"].str.replace("count_", ""))
        .pipe(
            lambda x: px.line(
                data_frame=x,
                x="year",
                y="value",
                color="variable",
                labels=dict(year="Year", value="# of Uses"),
                custom_data=["variable"],
            )
        )
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text="Word")
    fig.update_traces(
        hovertemplate='In %{x}, the word "%{customdata[0]}" was used %{y} times.<extra></extra>',
    )
    return fig


def rawtable() -> go.Figure:
    """The sample table."""
    df = alldata.head(40)
    df["text"] = df["text"].apply(lambda x: f"{x[:100]}...")
    headers = df.columns
    fig = FIGBUILDER(
        data=[
            go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[df[col] for col in headers],
                    fill_color="lavender",
                    align="left",
                ),
            )
        ],
        # TypeError: invalid Figure property: margin
        # margin=go.layout.Margin(l=0, r=0, t=0, b=0)
    )
    return fig



def timetoread() -> go.Figure:
    fig = (
        alldata.loc[lambda x: ~x["is1997letter"]]
        .assign(
            nwords=lambda x: x["text"].apply(
                lambda x: len(x.replace("\n", " ").split(" "))
            )
        )
        .assign(minutes=lambda x: x["nwords"].apply(lambda x: x / 200))
        .groupby(["year", "author"])
        .agg({"minutes": "sum", "nwords": "sum"})
        .reset_index()
        .pipe(
            lambda x: px.line(
                data_frame=x,
                x="year",
                y="minutes",
                color="author",
                labels=dict(year="Year Released", minutes="Minutes to Read"),
            )
        )
    )
    fig.update_layout(yaxis_range=[0, 60], legend_title_text="Author")
    fig.update_traces(
        hovertemplate="The %{x} letter would take ~%{y:.0f} minutes to read.<extra></extra>"
    )
    return fig


@callback(Output("embedded-pdf", "src"), Input("dropdown-pdf", "value"))
def pdfdropdown(value) -> str:
    return f"assets/Letter_{value}.pdf"


COLORMAP = {"negative": "#D81B60", "neutral": "#D3D3D3", "positive": "#1E88E5"}


@callback(Output("sentiment-graph", "figure"), Input("dropdown-pdf", "value"))
def individual_sentiment(year):
    fig = px.scatter(
        data_frame=sentiment_frame.loc[lambda x: x["year"] == year],
        x="index",
        y="score",
        color="color",
        color_discrete_map=COLORMAP,
        hover_data="chunk",
        custom_data=["color", "wrapped"],
        range_y=(-1, 1),
        height=300,
        opacity=0.5,
        labels={
            "index": "",
            "score": "Sentiment",
        },
        title="",
    )
    fig.update_traces(
        hovertemplate='The passage below has %{customdata[0]} sentiment (%{y}).<br><br>"%{customdata[1]}"<extra></extra>',
    )
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
    )

    def traceconfig(trace):
        if trace.name in ("negative", "positive"):
            trace.update(marker_size=10)

    fig.for_each_trace(traceconfig)
    fig.for_each_yaxis(
        lambda yaxis: yaxis.update(
            tickmode="array",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["Negative", "", "Neutral", "", "Positive"],
        )
    )
    # This doesnt seem to work for negative values?
    # fig.update_yaxes(labelalias={-1: 'Negative', -.5: '', 0: 'Neutral', .5: 'lil positive', 1: 'Positive'})
    fig.for_each_xaxis(
        lambda xaxis: xaxis.update(matches=None, showticklabels=False, ticks=None)
    )
    return fig


@callback(Output("sentiment-summary", "figure"), Input("dropdown-pdf", "value"))
def breakdownviz(year):
    """Sentiment overview of an indivudal letter."""
    breakdown = (
        sentiment_frame.loc[lambda x: x["year"] == year]["color"]
        .value_counts(normalize=True)
        .reset_index()
    )
    nvals = breakdown.shape[0]
    fig = px.bar(
        y=[1] * nvals,
        x="proportion",
        color="color",
        data_frame=breakdown,
        color_discrete_map=COLORMAP,
        orientation="h",
        height=150,
        template="none",
        labels=dict(proportion="", y=""),
        custom_data=["color"],
    )
    fig.update_layout(
        barmode="stack",
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
        showlegend=False,
        hovermode=False,
    )
    fig.update_traces(
        texttemplate="%{x:.0%} %{customdata[0]}",
        textposition="inside",
        insidetextanchor="middle",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=40))
    return fig


def alllettersfig():
    """Shows sentiment breakdown (stacked bars) for all years."""
    breakdown = (
        sentiment_frame.groupby("year")["color"]
        .value_counts(normalize=True)
        .reset_index()
        .sort_values(by="color")
    )
    ns = (
        sentiment_frame.groupby("year")["color"]
        .value_counts()
        .reset_index(name="n")
        .sort_values(by="color")["n"]
    )
    breakdown["n"] = ns
    breakdown["color"] = pd.Categorical(
        breakdown["color"], ["negative", "neutral", "positive"]
    )
    fig = px.bar(
        y="year",
        x="proportion",
        color="color",
        data_frame=breakdown,
        color_discrete_map=COLORMAP,
        orientation="h",
        labels=dict(year="", proportion=""),
        height=700,
        custom_data=["year", "color", "n"],
    )
    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
        yaxis=dict(tickvals=breakdown["year"].unique()),
        legend_title_text="Sentiment",
    )
    fig.update_traces(
        hovertemplate="%{x:.0%} (%{customdata[2]}) of the sentences in %{y} were %{customdata[1]}<extra></extra>",
    )
    return fig


@callback(Output("sentiment-top-chunks", "figure"), Input("dropdown-pdf", "value"))
def top_bottom_chunks(year) -> go.Figure:
    """Shows the top / bottom passages by sentiment."""
    TOP_N = 3
    _df = (
        sentiment_frame.loc[lambda x: x["year"] == year]
        .sort_values(by="score", ascending=False)
        .pipe(lambda x: pd.concat([x.head(TOP_N), x.tail(TOP_N)]))
    )

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Passage", "Score (between -1 to +1)"],
                    line_color="white",
                    fill_color="white",
                    align="left",
                    font=dict(color="black", size=12),
                ),
                cells=dict(
                    values=[_df.chunk, _df.score],
                    fill_color=[_df.color.apply(lambda x: COLORMAP[x])],
                    align="left",
                    font=dict(color="black", size=11),
                ),
            )
        ]
    )
    fig.update_layout(margin=DEFAULT_MARGINS)
    return fig


@callback(
    Output("concordance_output", "figure"),
    Input("submit-val", "n_clicks"),
    State("concordance_input", "value"),
)
def word_concordance_plot(concordance_input, value):
    """ Shows the frequency of a particular word. """
    SEARCH_TERM = value
    base_data = (
        alldata
        .assign(split = lambda x: x['text_object'].apply(lambda x: x.tokens))
        .explode('split')
        .reset_index(drop=True)
        .reset_index()
    )
    summary_data = ( 
        base_data
        .loc[lambda x: x['split'] == SEARCH_TERM]
    )
    refline_data = base_data.groupby('year')['index'].min().reset_index()
    fig = (
        summary_data
        .assign(static_value = 1)
        .assign(static_x = lambda x: x.apply(lambda x: [x['index'], x['year']], axis=1))
        .pipe(lambda x: px.scatter(
            data_frame=x, x='index', y='static_value', title='', labels={'static_value': '', 'index': ''}
        ))
    )
    for row in refline_data.to_dict(orient='records'):
        # This is taking a long time
        fig.add_vline(
            x=row['index'], 
            line_width=3, 
            line_dash="dash", 
            line_color="grey",
            annotation_text=row['year'],
            annotation_position='bottom right',
            annotation_textangle=45
        )
    fig.update_traces(
        # use rbga so I can make the center opacity
        marker = {
            'size': 20,
            'color': 'rgba(30,136,229,.25)',
            'line': {
                'color': 'rgba(0,0,0,1)',
                'width': 1
            }
        })
    fig.update_layout(
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickvals=[],
            ticktext=[],
        ),
        hovermode=False,
    )
    return fig


@callback(
    Output("word_search_title", "children"),
    Input("submit-val", "n_clicks"),
    State("concordance_input", "value"),
)
def update_concordance_title(concordance_input, value):
    return f"Showing occurences of \"{value}\""

@callback(
    Output("individual_page_title", "children"),
    Input("dropdown-pdf", "value"),
)
def update_document_details_title(value):
    return f"Summarizing sentiment for {value}"


@callback(
    Output("concordance_table", "figure"),
    Input("submit-val", "n_clicks"),
    State("concordance_input", "value"),
)
def search_word_table(concordance_input, value):
    """ This renders pretty quickly """
    _df = (
        alldata
        .assign(concordances = lambda x: x['text_object'].apply(lambda x: x.concordance_list(value)))
        .loc[lambda x: ~x['concordances'].isna()]
        [['pagenumber', 'year', 'author', 'concordances']]
        .explode('concordances')
        .loc[lambda x: ~x['concordances'].isna()]
        .assign(left_text = lambda x: x['concordances'].apply(lambda x: ' '.join(x.left)))
        .assign(right_text = lambda x: x['concordances'].apply(lambda x: ' '.join(x.right)))
        .assign(search_term = value)
        [['year', 'left_text', 'search_term', 'right_text']]
    )
    headers = _df.columns
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=['Year', '', '', ''],
                    fill_color="rgba(30,136,229,.25)",
                    align="left",
                ),
                cells=dict(
                    values=[_df[col] for col in headers],
                    # fill_color="rgba(30,136,229,.25)",
                    align=["left", 'right', 'center', 'left'],
                ),
                columnwidth=[50, 420, 40, 420],
            )
        ],
    )
    return fig



if __name__ == "__main__":
    """You can use this to product the figures locally."""
    fig = alllettersfig()
    fig.write_html("_testfigs/test.html")
