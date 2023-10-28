# Customer Obsession

This is a dashboard built with Dash that analyzes the last decade or so of shareholder letters from Amazon.

## This project consisted of a few main steps:

1. Download all the shareholder letters as pdfs (using `selenium`)
2. Extract the text out of the pdfs (using `pypdf`)
3. Analyze the text (using `nltk`)
4. Display the results (using `Dash`)

## Assumptions

- Starting 2001, the 1997 letter was attached to every report. For most of the analysis I did, this letter was excluded.

## Visual History:

- 10-10-2023:

    - ![Alt text](history/101023/image.png)

- 10-14-2023:

    - ![Alt text](history/101423/image.png)
    - ![Alt text](history/101423/image-1.png)
    - ![Alt text](history/101423/image-2.png)

- 10-22-2023:

    - ![Alt text](history/102223/1.png)
    - ![Alt text](history/102223/2.png)
    - ![Alt text](history/102223/3.png)
    - ![Alt text](history/102223/4.png)

## Personal Goals

I had a few goals with this project:

1. Learn more about Dash
2. Learn more about sentiment analysis
3. Finish an end-to-end analytics project, starting from data collection to a final deliverable (dashboard)

I learned quite a bit:

1. Obviously all the syntax and workings of `Dash`, `plotly`, and `nltk`
2. Natural language processing has its own set of challenges
    1. Cleaning up text to begin with
        - Identifiying "sentences"
        - Lemmatizing words vs. stemming them
        - 


## Random Notes

- My webscraping script isn't perfect, for some reason the css selector didn't download the 2007 letter.
- Stemming vs. lemmatizing
- Needed to break apart words, linebreaks end up combining words in `pypdf`
- Getting sentiment by sentences (.), vs. by number of words, vs. by a rolling score
- How you define "word" / "sentence" / "punctuation" can change your analysis quite a bit
- Running into an issue where if someone wants to search for a word, I need to search over the cleaned / lemmatized version (in order to pick up some other instances that aren't EXACTLY what the person is looking for), but then, I need to reconcile that with the actual raw text when displaying it visually. 