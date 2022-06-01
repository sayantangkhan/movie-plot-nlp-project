# Semantic search engine for movie plots

This is a search engine that lets you find movies based on a sentence or two describing the plot.
This was made as a part of the Erdös data science bootcamp.

In the README, we describe the data gathering process, the preprocessing and cleanup, the architecture (with its flaws) of the classifier, and the web-frontend ([link](http://jupyter.sayantankhan.io/search) to web-frontend). 

### Table of contents
1. [Data gathering](#data-gathering)
    1. [Scraping IMDB](#imdb-scraping)
    2. [Generating data using T5](#summary-generation)
2. [Preprocessing and cleanup](#preprocessing)
3. [Classifier models](#classifier)
4. [Web frontend](#web-frontend)

## Data gathering <a name="data-gathering"></a>

We needed two kinds of data for the semantic search engine: first we needed the plot summaries of all the movies we could get. These are the movies that are actually searchable by the search engine.
This dataset was a combination of the [Kaggle Wikipedia Movie Plots](https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots) dataset and the [CMU Movie Summary Corpus](http://www.cs.cmu.edu/~ark/personas/).

The second kind of dataset we needed was a collection of example queries users would query the search engine for; we planned to train and test the performance on such a dataset.
For the search engine to be a good search engine, we wanted it to be able to identify the movie based on very little detail, i.e. search queries needn't have names of characters involved (or actors), and just describe part of the plot in broad strokes.
If the searches were more detailed, traditional search engine methods would suffice, just using keyword based searches.

However, we did not have such an collection of user searches along with movies they were searching for.
To get this data, we tried two different approaches. 

### Scraping IMDB <a name="imdb-scraping"></a>

The first approach was to scrape IMDB user submitted summaries for short (and hopefully vague) summaries that could serve as a proxy for search queries users would make when searching for the corresponding movie. Our process was as follows:

First, any movie on IMDB is given a distinct IMDB ID that serves as an identifier. Conveniently, any link pertaining to a particular movie is in one-to-one correspondence with its unique IMDB identifier. So, user generated summaries were always on the same URL---the only change was the IMDB ID. 

Then, we utilized the requests module in concert with BeautifulSoup in order to scrape the user generated data from IMDB. We implemented the time module to add delay in each iteration of the for-loop so we would not overburden IMDB's servers. 

Due to the lengthy run time and other unknowns (internet cutting off, laptop rebooting, etc.), we had the scraper save its output periodically to Google Drive. When a crash occured, we rebooted the program at the last iteration and continued from there. Once all data had been scraped, we concatenated the CSV files and added them to the existing data as a new column. This whole process was for the first user generated summary; later on, we repeated this process for the second user generated summary (when available) as well.

### Generating data using T5 <a name="summary-generation"></a>

The other approach we tried in parallel with the scraping was to generate reasonably vague queries from the plot summary using a pre-trained text summarizer.
The hope was that the text summarizer would leave out a lot of details, and get rid of most identifying keywords, leaving only broad outlines.

[This notebook](notebooks/exploratory/plot-summarizer.ipynb) displays what the summary looks like for different pre-trained text summarizer.
Based on the output, we decided that the T5 summarizer generated the summary that left out the most keywords, making it the most suitable for our purposes.

## Preprocessing and cleanup <a name="preprocessing"></a>

The Kaggle dataset contained various wikipedia-style citation artifacts (such as \[1\] or \[citation needed\]), which we cleaned from the dataset. Using the module NLTK, we built a tool to split longer plot descriptions into pieces (halves and thirds, based on the number of sentences) for use on the wikipedia plot summaries, to build our vector embedding.

Every movie initially had string representing a list of genres associated to it from both the Kaggle & CMU datasets. We wanted standard, high-level genres for use in the genre selector on the interface. To do this, we did the following.
+ Standardized spellings for genres (e.g., "sci-fi" and "science fiction" both appeared, so we standardized to "science-fiction").
+ Standardized separators, since sometimes genres could be separated with "/", ",", " - ", or just a space " ".
+ Added some additional broader genres for smaller subgenres (e.g., movies with the genres "slasher" or "zombie" got the genre "horror" added to the list).
+ Broke intersectional genres into broader genres (e.g., "romantic comedy" split into the two genres "romance" and "comedy"). 
We did this to both lists of associated genres, and merged them together.

We eventually plan to improve the web interface and allow for filtering by cast members. To prepare for this, we also cleaned the cast & director info. Originally, the lists of directors and of cast members were linked in multiple ways (sometime with "and", "/", or ","). We standardized them to all be separated by commas. And sometimes, the lists would start with the word "Director: " or "Cast: ", which we removed.

We also had to deal with some duplicated data. For Kaggle datasets, some movies had duplicated URLs, usually due to several different releases (e.g., in different languages) with different titles sharing the same wikipedia page. For those, we dropped all but the first entry with that URL. We were then still left with some Kaggle and CMU entries which shared a title and release year; for scraped IMDB data, a few movies had duplicated IMDB ids. This was a small percentage of the original data, so we deleted all copies of these remaining duplicates.

At the end, we merged the Kaggle, CMU, and scraped IMDB data based on movies that had the same title & release year. 

## Classifier models <a name="classifier"></a>

We tried out two different approaches to classifying queries: one of them is based on [Sentence Embeddings](https://www.sbert.net/index.html): this method is called _Embed-and-Rerank_ and the other is the more classical [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25).

### Embed-and-Rerank

Embed-and-Rerank is a 3-step process.

1. Take the corpus of all wikipedia plots, and break them up into chunks of 256 tokens, since that's the most the neural network can handle. This results in a large collection of plot summary fragments, labelled by the movie they are from.
2. The corpus of summary fragments is then embedded in
using a context sensitive sentence embedder. We use a BERT derived model trained on the MS-MARCO dataset. Using the same embedder, we also embed the search query string into the vector space, and then pick out the closest 100 corpus entries using a cosine-similarity metric. These 100 points are an initial guess for the movie the query string is referencing.
3. Finally, we run the query string and each of the 100 guesses through a cross-encoder, a different neural network that outputs a similarity score based on semantics between two input sentences. We pick the top 10 scoring movies as search results for the input query.

With this approach, we achieved 84% accuracy on the IMDB query dataset, which is much higher than the baseline 21% obtained with a naïve substring similarity search.
We also looked at some examples of misclassifications (see the [notebook](notebooks/testing/embed_and_rerank.ipynb) for examples) and observed that the classifier misclassified on queries that referred to the global structure of the plot, i.e. referring to events that happen at the beginning and the end of the movie.
However, we break up the plot into chunks of 256 words, which means for long plots, the beginning and end are in different chunks.

This can be gotten around by increasing the max tokens the sentence embedder can consume, but this slows down inference considerably which is why we chose not to.

### Okapi BM25
We implemented this model to compare it to Embed-and-Rerank. This is based on TF-IDF approach, and does not use neural networks.
Despite this, this model also achieves 84% accuracy on the IMDB dataset, although its misclassifications are of a different nature.

Since this model just uses term-frequency, it does not understand synonyms, and fails to classify correctly when synonymous terms are present in the query and the plot summary.
Thus despite doing well on the test set, it's still not suitable for the search engine, and the fact it does so well on the test set is an artifact of the test set rather than a quality of the model.

## Web frontend <a name="web-frontend"></a>

The front-end is built in [Flask](https://flask.palletsprojects.com/en/2.1.x/).
To build and run the web-server, navigate to [web_interface](web_interface), and run the following commands.
```
poetry env use python3.8
poetry install
poetry shell
flask run
```
Click on [this link](http://jupyter.sayantankhan.io/search) to go to the hosted version of the web-interface.
