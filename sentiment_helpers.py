import wordninja
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from nltk.tokenize import sent_tokenize

sia = SentimentIntensityAnalyzer()
def remove_puncuation(word: str) -> str:
    PUNCTUATION = (
        ',', '.', '`', '$', '%', 
        ':', '-', '(', ')', '’',
        '•', '–', '“', '”', "'",
        '-'
    )
    return ''.join([letter for letter in word if letter not in PUNCTUATION])

def cleanup_words(text: str) -> str:
    """ Cleans up the words. """

    cleanedwords = []
    for word in text.split(' '):
        word = remove_puncuation(word)
        if not word:
            continue

        if len(splitword := wordninja.split(word)) > 1:
            # if its an acronym, thats fine too:
            if word.isupper():
                cleanedwords.append(word)
                continue

            # ['That', 's'] is fine, "s" at the end it OK
            if splitword[-1].lower() == 's':
                continue

            # check if its "amazon.com"
            if splitword == ['Amazon', 'com']:
                cleanedwords.extend(['Amazon.com'])
                continue

            cleanedwords.extend(splitword)
        else:
            cleanedwords.append(word)
    return ' '.join(cleanedwords)

def createchunkscores(_df):
    """ This is expecting to be used with a groupby('year') """
    singledocument = ' '.join(_df['text'].values)

    nums = []

    # I tried a few approaches here, splitting on spaces, splitting on a certain
    # # of characters, I think the sentence breakup makes the most sense
    for group in sent_tokenize(singledocument):
        cleangroup = cleanup_words(group)
        scores = sia.polarity_scores(cleangroup)
        nums.append({'chunk': cleangroup, 'score': scores['compound']})

    return pd.DataFrame(nums).reset_index()