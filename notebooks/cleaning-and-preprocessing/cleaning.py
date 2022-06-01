import pandas as pd
import re
"""
Module for cleaning original movie data csv file.
"""

def remove_citations(df):
    """ Modifies the dataframe df to remove ALL citations from ALL entries.
    """
    # note: not EVERY set of [...] is a citation
    # sometimes it can be part of a "filled in" quote
    cit_formats = [r"\[citation needed\]", 
                   r"\[clarification needed\]",
                   r"\[not in citation given\]",
                   r"\[disambiguation needed\]",
                   r"\[original research\?\]",
                   r"\[N [0-9]+\]",
                   r"\[Note [0-9]+\]",
                   r"\[[0-9]+\]",
                   r"\[who\?\]",
                   r"\[what\?\]",
                   r"\[when\?\]",
                   r"\[where\?\]",
                   r"\[why\?\]"
                   ]
    pattern = "|".join(cit_formats)
    nrows, ncols = df.shape
    for r in range(nrows):
        for c in range(ncols):
            entry = df.iat[r,c]
            if type(entry)==str:
                df.iat[r,c]  = re.sub(pattern, "",entry)

def remove_useless(df):
    """
    Returns a (view of?) df with all "useless" data removed.

    "Useless" data includes entries such as those with missing entries, those
    with something like "unknown" or NaN as an entry, or those where the plot
    description says nothing at all about the movie (badly scraped).
    """
    # These are some "useless" plots which I manually found
    bad_plots = ["Film's introduction:",
                "Smith explains:",
                "See the Plot for the original Play.",
                "There are three film clips available:",
                "From the UK VHS slick for the movie:",
                "{{no plott}||date=January 2018}}",
                "Refer this for details.",
                ]
    # it would also not be unreasonable to remove all plots which are
    #   "too short", say, <= 40 characters
    mask = [p not in bad_plots for p in df["Plot"]]
    return df.loc[mask]

if __name__ == "__main__":
    movie_df = pd.read_csv("../Data/wiki_movie_plots_deduped.csv")
    remove_citations(movie_df)
    remove_useless(movie_df)
    movie_df.to_csv("../Data/wiki_movies_no_cites.csv")
