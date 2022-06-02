## Removing citation artifacts
The python script [cleaning.py](cleaning.py) removes wikipedia-style citation artifacts (such as \[1\] or \[citation needed\]) from all entries in the Kaggle dataset.
There are corresponding test cases in [test_cleaning.py](test_cleaning.py).


## Cast and director cleaning

The notebook [CastAndDirectorClean.ipnyb](CastAndDirectorClean.ipnyb) renames the column "Origin/Ethnicity" to the easier-to-access "Origin" (though some are actually languages!).

It then works on cleaning the cast & director info, for future usage in the web interface. The data is messy in several ways: it can have different separators ("and", "&", "/", "\r\n", and ",") and it can have various parentheticals with "[...]" or "(...)". Sometimes, entries also include header words like "Director:" or "Cast:", and these are removed as well. Several special cases are also manually dealt with.

The output is written to file, with all "unknown" cast/directors removed.

INPUT: 
+ Data/wiki_plots_with_genres.csv
OUTPUT: 
+ Data/wiki_plots_with_genres_c2.csv


## Splitting Plot

The notebook [imdb_summaries.ipnyb](imdb_summaries.ipnyb) takes the long plot descriptions from wikipedia and breaks long paragraphs into chunks with at most 256 tokens (words) each.


## Scraping IMDB Summaries

The notebook [IMDB_Web_Scraping.ipynb](IMDB_Web_Scraping.ipynb) uses BeautifulSoup to get the first user summary for each movie in our dataset, using the IMDB id's coming from the CMU dataset.
Modifying some indices then allows one to scrape the second user summary instead.

This data is then used in the  notebook [Combined_Yili_and_Ethan_Scrape.ipnyb](Combined_Yili_and_Ethan_Scrape.ipnyb), which combines the scraped data for getting the 1st summary and the 2nd summary into one csv file.

INPUTS: 
+ (paths not all in this github)
OUTPUT: 
+ (path not in this github)

## Revenue and Summary
The notebook [MergeTwoDataset.ipynb](MergeTwoDataset.ipynb) takes the original CMU dataset and merges its revenue column into the Kaggle dataset (with cleaned cast & director info).
The merge is done based on shared title & release year.

Then the notebook [combining-revenue-and-summary-fragments.ipynb](combining-revenue-and-summary-fragments.ipynb) merges the revenue and summary csv files into a single csv file.

INPUTS: 
+ Data/cmu_movie_boxoffice.tsv
+ Data/wiki_plots_with_genres_c2.csv
+ Data/wiki_movies_no_cites.zip
+ Data/wiki_movie_plots_deduped_c2.csv
OUTPUT: 
+ Data/wiki_with_revenue.csv (actually a zip file)

## Genre cleaning
We need to have 15 or so high-level genres for use in the web interface. The CMU dataset is reasonably well formatted, but sometimes describes genres in ways that are unhelpful (e.g., subgenres, or combining genres like "romantic comedy" when we would prefer separate genres "romance" and "comedy"). 
The Kaggle dataset is fairly messy, and we have to deal with inconsistent separators ("/" vs "," vs " - " vs " ") in addition to the issues from the CMU dataset. 
The notebook [genre-clean.ipynb](genre-clean.ipynb) has functions that turn a given genre string into a set of genres to fix these issues.

The notebook also merges these datasets together and combines the genre info. It matches movies based on title & release year (since with remakes, there can be multiple movies with the same title released in different years). We do some further cleaning and drop extraneous copies of movies with the same wikipedia URL, and we alltogether delete any remaining movies which have the same title & release year, as this was a very small fraction of the dataset.

INPUTS: 
+ Data/wiki_movie_plots_deduped.csv.zip
+ Data/cmu_movie_boxoffice.tsv
OUTPUT: 
+ Data/wiki_plots_with_genres.csv.zip 
