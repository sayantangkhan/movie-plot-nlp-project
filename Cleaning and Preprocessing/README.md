These are all of the notebooks used for data gathering, data cleaning, data exploration, and preprocessing.

### Table of contents
1. [Data gathering](#data-gathering)
2. [Data cleaning](#data-cleaning)
   1. [Removing citations](#citation-clean)
   2. [Genre cleaning](#genre-clean)
   3. [Prep for future](#prep-clean)
3. [Preprocessing](#preprocessing)
   1. [Generating Wikipedia summary fragments](#wiki-summary)
   2. [Generating cross-encoder training data](#encoder-train-data)
   3. [Splitting plot](#plot-split)

# Data gathering <a name="data-gathering"></a>

## Kaggle & CMU

Our two main datasets are the [Kaggle Wikipedia Movie Plots](https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots) and the [CMU Movie Summary Corpus](http://www.cs.cmu.edu/~ark/personas/) dataset.

## Scraping IMDB summaries
We supplemented the above datasets with data scraped from IMDB.
The notebook [IMDB_Web_Scraping](IMDB_Web_Scraping.ipynb) uses BeautifulSoup to get the first user summary for each movie in our dataset, using the IMDB id's coming from the CMU dataset.
Modifying some indices then allows one to scrape the second user summary instead.

This data is then used in the  notebook [Combined_Yili_and_Ethan_Scrape](Combined_Yili_and_Ethan_Scrape.ipynb), which combines the scraped data for getting the 1st summary and the 2nd summary into one csv file.

INPUTS: 
+ (paths not all in this github)

OUTPUT: 
+ (path not in this github)

# Data cleaning <a name="data-cleaning"></a>

## Removing citations <a name="citation-clean"></a>
The python script [cleaning](cleaning.py) removes wikipedia-style citation artifacts (such as \[1\] or \[citation needed\]) from all entries in the Kaggle dataset.
There are corresponding test cases in [test_cleaning](test_cleaning.py).

## Genre cleaning <a name="genre-clean"></a>
We need to have 15 or so high-level genres for use in the web interface. The CMU dataset is reasonably well formatted, but sometimes describes genres in ways that are unhelpful (e.g., subgenres, or combining genres like "romantic comedy" when we would prefer separate genres "romance" and "comedy"). 
The Kaggle dataset is fairly messy, and we have to deal with inconsistent separators ("/" vs "," vs " - " vs " ") in addition to the issues from the CMU dataset. 
The notebook [genre-clean](genre-clean.ipynb) has functions that turn a given genre string into a set of genres to fix these issues.

The notebook also merges these datasets together and combines the genre info. It matches movies based on title & release year (since with remakes, there can be multiple movies with the same title released in different years). We do some further cleaning and drop extraneous copies of movies with the same wikipedia URL, and we alltogether delete any remaining movies which have the same title & release year, as this was a very small fraction of the dataset.

INPUTS: 
+ Data/wiki_movie_plots_deduped.csv.zip
+ Data/cmu_movie_boxoffice.tsv

OUTPUT: 
+ Data/wiki_plots_with_genres.csv.zip 

## Cleaning to prep for future work <a name="prep-clean"></a>

### Cast and director cleaning

The notebook [CastAndDirectorClean](CastAndDirectorClean.ipynb) renames the column "Origin/Ethnicity" to the easier-to-access "Origin" (though some are actually languages!).

It then works on cleaning the cast & director info, for future usage in the web interface. The data is messy in several ways: it can have different separators ("and", "&", "/", "\r\n", and ",") and it can have various parentheticals with "[...]" or "(...)". Sometimes, entries also include header words like "Director:" or "Cast:", and these are removed as well. Several special cases are also manually dealt with.

The output is written to file, with all "unknown" cast/directors removed.

INPUT: 
+ Data/wiki_plots_with_genres.csv

OUTPUT: 
+ Data/wiki_plots_with_genres_c2.csv

### Revenue and summary
We originally considered using revenue (as a proxy for popularity) to help weight the search results. In preparation for this, 

The notebook [MergeTwoDataset](MergeTwoDataset.ipynb) takes the original CMU dataset and merges its revenue column into the Kaggle dataset (with cleaned cast & director info).
The merge is done based on shared title & release year.

Then the notebook [combining-revenue-and-summary-fragments](combining-revenue-and-summary-fragments.ipynb) merges the revenue and summary csv files into a single csv file.

However, even without this the model seemed to do a good job when manually testing on popular movies, and we worried this would make it too difficult to find obscure films, so we never ended up using this data. 
We may in future run a comparison to see how the results actually compare.

INPUTS: 
+ Data/cmu_movie_boxoffice.tsv
+ Data/wiki_plots_with_genres_c2.csv
+ Data/wiki_movies_no_cites.zip
+ Data/wiki_movie_plots_deduped_c2.csv

OUTPUT: 
+ Data/wiki_with_revenue.csv (actually a zip file)

### More revenues

The notebook [ttlDmerging](ttlDmerging.ipynb) takes the revenue, overview, and popularity from the metadata dataset and merges them into the Kaggle dataset.

INPUTS:
+ Data/movies_metadata.csv
+ Data/wiki_plots_with_genres_c2.csv
OUTPUT:
+ Data/wiki_plots_with_genres_c3.csv

# Preprocessing <a name="preprocessing"></a>

## Generating Wikipedia summary fragments <a name="wiki-summary"></a>

The notebook [summary_generator](summary_generator.ipynb) takes the Kaggle dataset (with citations removed) and creates a new dataset which contains fragments of the plots and a corresponding sentence randomly chosen from a summary of that chunk.
The fragments of the plots can be the 1st, 2nd, or 3rd third of the plot, or the 1st or 2nd half of the plot (stored in column PlotFragments). Then T5 is used to summarize this fragment, and a sentence is randomly chosen from this summary (which is then stored in column SummaryFragment). 
A MovieID column is used to link the rows back to the corresponding row in the original dataset.
To keep the datasize managable, instead of adding all 5 options for every movie, there is a 62.5% chance of adding any given fragment to the new dataset.

INPUT:
+ Data/wiki_movies_no_cites.csv

OUTPUT:
+ Data/summaries.csv

## Generating cross-encoder training data <a name="encoder-train-data"></a>

The cross-encoder needs pairs of text with similarity scores for training purposes.
The notebook [pruning-summaries](pruning-summaries.ipynb) uses the plot fragments & corresponding random sentences from summaries already generated and uses this to get the similarity data.
Here's how the scores are assigned:
+ a fragment & corresponding summarized sentence get a high similarity score;
+ a fragment from one movie & summarized sentence from a totally different movie get a low similarity score;
+ a fragment & summarized sentence from the same movie, but different chunks (e.g., fragment from middle third, summarized sentence from first half) get a medium similarity score.
The pairs are randomly chosen so that about 40% get a high score and about 60% get a low score (with a negligible amount getting a medium score).

INPUT/OUTPUT:
+ Data/summaries.csv


## Splitting plot<a name="plot-split"></a>

The notebook [imdb_summaries](imdb_summaries.ipynb) takes the long plot descriptions from wikipedia and breaks long paragraphs into chunks with at most 256 tokens (words) each.

