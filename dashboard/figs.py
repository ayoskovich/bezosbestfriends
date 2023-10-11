import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from datapipeline import alldata, wholetext
from dash import Input, callback, Output, State

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist

def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig

@callback(
    Output('mostcommonfig', 'figure'),
    Input("topnwordbutton", 'n_clicks'),
    State("nmostcommon", "value"),
    prevent_initial_call=True
)
def mostcommon(nclicks, nmostcommon):
    """ Returns the n most common words. """
    stop_words = set(stopwords.words("english"))
    PUNCTUATION = (
        ',', '.', '`', '$', '%', 
        ':', '-', '(', ')', '’',
        '•', '–', '“', '”'
    )
    
    stemmer = PorterStemmer()
    lemmer = WordNetLemmatizer()

    subset_of_words = [x for x in wholetext if (x.casefold() not in stop_words) and (x not in PUNCTUATION)]
    stemmed_words = [stemmer.stem(x) for x in subset_of_words]
    lemmatized_words = [lemmer.lemmatize(x) for x in subset_of_words]

    dist = FreqDist(
        # stemmed_words  # this doesn't give you whole words
        lemmatized_words
    )

    return (
        pd.DataFrame.from_records(dist.most_common(int(nmostcommon)), columns=['word', 'amount'])
        .pipe(lambda x: px.bar(data_frame=x, x='word', y='amount', title=f'{nmostcommon} most common words'))
    )
    
def rawtable():
    """The sample table."""
    df = alldata.head(40)
    df["text"] = df["text"].apply(lambda x: f"{x[:100]}...")
    headers = df.columns
    return go.Figure(
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
        ]
    )

def nwordscatter():
    fig = px.scatter(
        x='year', 
        y='ncharacters', 
        data_frame=alldata,
        labels=dict(year='Year', ncharacters='# of Characters'),
        title=f'Interestingly, starting in 2001 the 1997 letter was attached to all letters.'
    );
    fig.add_hline(y=3250);
    return fig

def nwordshist():
    """ The word histogram """
    df = alldata

    return px.histogram(
        df.groupby('fname').agg({
            'ncharacters': 'sum'
        }),
        x="ncharacters", 
        title='Number of characters per letter'
    )


@callback(
    Output('concordance_output', 'figure'),
    Input("submit-val", 'n_clicks'),
    State("concordance_input", "value"),
    prevent_initial_call=True
)
def concordances(concordance_input, value):
    search_term = value
    vals = wholetext.concordance_list(search_term)

    fullsentences = []
    for val in vals:
        fullsentences.append(f"{' '.join(val.left)} {search_term} {' '.join(val.right)}")
    return go.Figure(
        data=[
            go.Table(
                header=dict(values=["Snippet"], align='left'),
                cells = dict(values=[fullsentences], align='left')
            )
        ]
    )
