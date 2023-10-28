import pickle
import pandas as pd
import seaborn as sns
import glob
from pypdf import PdfReader
from nltk.text import Text
import os
import wordninja
import sentiment_helpers as sh
import textwrap
from nltk.stem import WordNetLemmatizer

lemmer = WordNetLemmatizer()

letters = {
    fname: PdfReader(fname) 
    for fname in glob.glob('../data/*.pdf')
}

def process_letter(x: PdfReader) -> dict:
    return [
        {'pagenumber': i+1, 'text': page.extract_text()} 
        for i, page in enumerate(x.pages)
    ]

def newclean(text: str) -> Text:
    """ This will:
    
    1. Use word-ninja to split combined words and remove puncuation
    2. lemmatize the word (lowercase it)
    """
    return Text([lemmer.lemmatize(x.lower()) for x in sh.cleanup_words(text).split(' ')])

def createwholetext(df):
    # import nltk
    # nltk.download("stopwords")

    _wholetext = (' '.join(df['text'].tolist()))
    cleanedwords = sh.cleanup_words(_wholetext)

    return cleanedwords

if not os.path.exists('alldata.pickle'):
    print('cached part not found, creating')
    al = []
    for fname, pdf in letters.items():
        al.append(pd.DataFrame(process_letter(pdf)).assign(fname=fname))
    alldata = pd.concat(al)

    getyear = lambda x: int(x.split('_')[1].split('.')[0])
    alldata['ncharacters'] = alldata['text'].str.len()


    alldata['year'] = alldata['fname'].apply(getyear)
    alldata['author'] = alldata['year'].apply(lambda x: 'Andy Jassy' if x >= 2022 else 'Jeff Bezos')

    alldata.sort_values(by=['year', 'pagenumber'], inplace=True)
    is_letter = (
        alldata
        .assign(newis = lambda x: x['text'].apply(lambda x: True if x.strip().startswith('1997 LETTER TO SHAREHOLDERS') else None))
        .groupby('year')
        ['newis']
        # Mark all others as NOT the 1997 letter
        .ffill()
        .fillna(False)
    )
    alldata['is1997letter'] = is_letter
    alldata['text_object'] = alldata['text'].apply(newclean)
    with open('alldata.pickle', 'wb') as f:
        pickle.dump(alldata, f)

    wholetext = Text(createwholetext(alldata))
    with open('wholetext.pickle', 'wb') as f:
        pickle.dump(wholetext, f)

    sentiment_frame=(
        alldata
        .loc[lambda x: ~x['is1997letter']].groupby('year').apply(sh.createchunkscores).reset_index()
        .reset_index()
        .assign(color = lambda x: x['score'].apply(lambda x: 'negative' if x < -.5 else ('neutral' if x < .5 else 'positive')))
        .assign(wrapped = lambda x: x['chunk'].apply(lambda x: '<br>'.join(textwrap.wrap(x, width=50))))
    )
    sentiment_frame.to_parquet('sentiment_cached.parquet')

else:
    print('loading from cache')

    with open('alldata.pickle', 'rb') as f:
        alldata = pickle.load(f)

    with open('wholetext.pickle', 'rb') as f:
        wholetext = pickle.load(f)

    sentiment_frame = pd.read_parquet('sentiment_cached.parquet')