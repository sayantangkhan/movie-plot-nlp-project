import pandas as pd
from cleaning import *
import pytest
from pandas.testing import assert_frame_equal
"""
A module for testing the cleaning module.

To run this module, navigate to this directory & enter
    pytest test_cleaning.py
in the command line. To run ALL test modules (i.e., any module starting with
the word test) just enter
    pytest
on the command line.
"""

def test_cit_indiv():
    df = pd.DataFrame({"Sample": ["An uncited fact[citation needed].",
            "An ambiguous statement[clarification needed].",
            "A badly cited fact[not in citation given].",
            "Another ambiguous stmt[disambiguation needed].",
            "New work[original research?]",
            "See the Note[N 1]",
            "See the other note[N 23]",
            "See another [Note 5]",
            "A last note[Note 49]",
            "Numeric[4], blah blah",
            "Higher numeric[11], blah blah",
            "A person[who?]",
            "An event[what?]",
            "It once happened[when?] that...",
            "In another country[where?],",
            "He did that[why?]"]})
    remove_citations(df)
    count1 = [p.count("[") for p in df["Sample"] ]
    assert count1 == [0]*len(count1)
    count2 = [p.count("]") for p in df["Sample"] ]
    assert count2 == [0]*len(count2)
    corr_df = pd.DataFrame({"Sample": ["An uncited fact.",
            "An ambiguous statement.",
            "A badly cited fact.",
            "Another ambiguous stmt.",
            "New work",
            "See the Note",
            "See the other note",
            "See another ",
            "A last note",
            "Numeric, blah blah",
            "Higher numeric, blah blah",
            "A person",
            "An event",
            "It once happened that...",
            "In another country,",
            "He did that"]})
    assert_frame_equal(df, corr_df, check_dtype=False)

def test_cit_many():
    df = pd.DataFrame({"Sample": ["An uncited fact[citation needed]. An ambiguous statement[clarification needed].",
            "A badly cited fact[not in citation given]. Another ambiguous stmt[disambiguation needed].",
            "New work[original research?] See the Note[N 1] See the other note[N 23]",
            "See another [Note 5]. A last note[Note 49] Numeric[4], blah blahHigher numeric[11], blah blah A person[who?]",
            "An event[what?] It once happened[when?] that...",
            "In another country[where?], He did that[why?]"]})
    remove_citations(df)
    count1 = [p.count("[") for p in df["Sample"] ]
    assert count1 == [0]*len(count1)
    count2 = [p.count("]") for p in df["Sample"] ]
    assert count2 == [0]*len(count2)
    corr_df = pd.DataFrame({"Sample": ["An uncited fact. An ambiguous statement.",
            "A badly cited fact. Another ambiguous stmt.",
            "New work See the Note See the other note",
            "See another . A last note Numeric, blah blahHigher numeric, blah blah A person",
            "An event It once happened that...",
            "In another country, He did that"]})
    assert_frame_equal(df, corr_df, check_dtype=False)

def test_cite_more_cols():
    df = pd.DataFrame({"Col1": ["An uncited fact[citation needed].",
            "An ambiguous statement[clarification needed].",
            "A badly cited fact[not in citation given].",
            "Another ambiguous stmt[disambiguation needed].",
            "New work[original research?]",
            "See the Note[N 1]"],
    "Col2": ["See the other note[N 23]",
            "See another [Note 5]",
            "A last note[Note 49]",
            "Numeric[4], blah blah",
            "Perfectly good sentence!",
            "Higher numeric[11], blah blah"],
    "Col3": ["Another normal sentence!",
             "A person[who?]",
            "An event[what?]",
            "It once happened[when?] that...",
            "In another country[where?],",
            "He did that[why?]"]})
    remove_citations(df)
    for i in range(1,4):
        count1 = [p.count("[") for p in df["Col"+str(i)] ]
        assert count1 == [0]*len(count1)
        count2 = [p.count("]") for p in df["Col"+str(i)] ]
        assert count2 == [0]*len(count2)
    corr_df = pd.DataFrame({"Col1": ["An uncited fact.",
            "An ambiguous statement.",
            "A badly cited fact.",
            "Another ambiguous stmt.",
            "New work",
            "See the Note"],
    "Col2": ["See the other note",
            "See another ",
            "A last note",
            "Numeric, blah blah",
            "Perfectly good sentence!",
            "Higher numeric, blah blah"],
    "Col3": ["Another normal sentence!",
            "A person",
            "An event",
            "It once happened that...",
            "In another country,",
            "He did that"]})
    assert_frame_equal(df, corr_df, check_dtype=False)
