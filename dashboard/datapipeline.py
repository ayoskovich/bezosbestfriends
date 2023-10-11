import pickle
import pandas as pd
import seaborn as sns
import glob
from pypdf import PdfReader
from nltk.text import Text
import os

letters = {
    fname: PdfReader(fname) 
    for fname in glob.glob('../data/*.pdf')
}

def process_letter(x: PdfReader) -> dict:
    return [
        {'pagenumber': i+1, 'text': page.extract_text()} 
        for i, page in enumerate(x.pages)
    ]

def is_1997_letter(text: str) -> bool:
    return any([
        text.startswith(snippet)
        for snippet in (
            '1997 LETTER TO SHAREHOLDERS',
            '• We will make bold rather than timid investment',
            'Infrastructure\nDuring 1997, we worked hard to'
        )
    ])


def createwholetext(df):
    import nltk
    # nltk.download("stopwords")
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.draw.dispersion import dispersion_plot
    from nltk import FreqDist

    # Filtering out the 1997 letter that is always attached
    return word_tokenize(' '.join(df.loc[lambda x: ~x['is1997letter']]['text'].values))

if not os.path.exists('cached.parquet'):
    print('cached part not found, creating')
    al = []
    for fname, pdf in letters.items():
        al.append(pd.DataFrame(process_letter(pdf)).assign(fname=fname))
    alldata = pd.concat(al)

    getyear = lambda x: int(x.split('_')[1].split('.')[0])
    alldata['ncharacters'] = alldata['text'].str.len()
    alldata['is1997letter'] = alldata['text'].apply(is_1997_letter)
    alldata['year'] = alldata['fname'].apply(getyear)

    alldata.to_parquet('cached.parquet')
    wholetext = Text(createwholetext(alldata))
    with open('wholetext.pickle', 'wb') as f:
        pickle.dump(wholetext, f)
else:
    print('loading from cache')
    alldata = pd.read_parquet('cached.parquet')
    with open('wholetext.pickle', 'rb') as f:
        wholetext = pickle.load(f)
