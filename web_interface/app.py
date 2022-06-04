from flask import Flask, render_template, redirect, request, url_for
#from wtforms import Form, SelectField, StringField, validators
from inference import semantic_query
import logging

GENRE_CHOICES = ['Any', 'drama', 'comedy', 'romance', 'action', 'thriller', 'adventure', 'crime', 'indie', 'musical', 'horror', 'documentary', 'animation', 'mystery', 'science-fiction', 'fantasy']
YEAR_CHOICES = ['Any', '2010', '2000', '1990', '1980', '1970', '1960', '1950', '1940', '1930', '1920']

SEARCH_RESULTS = []

DEBUG = False

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('access.log')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/")
def index():
    return redirect('/search')

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        query = request.form['query']
        year = request.form['year']
        genre = request.form['genre']
        logger.debug("Query: {0}".format(query))
        logger.debug("year: {0}".format(year))
        logger.debug("genre: {0}".format(genre))
        global SEARCH_RESULTS
        SEARCH_RESULTS = semantic_query(query, {'year': year, 'genre': genre})
        return redirect('/result')
    return render_template('search.html', year_choices=YEAR_CHOICES, genre_choices=GENRE_CHOICES)

@app.route('/result')
def result_page():
    if len(SEARCH_RESULTS)==0:
        message = "We couldn't find any movies matching these criteria! Try broadening your search by setting the approximate year and genre options to 'Any'. Or, try altering your search query."
    elif len(SEARCH_RESULTS)<10:
        message = "We found a few movies matching your criteria. If yours isn't in this list, try broadening your search by setting the approximate year and genre options to 'Any'. Or, try altering your search query."
    elif len(SEARCH_RESULTS)>=10:
        message = "We found a lot of movies matching your criteria! If yours isn't in this list, try narrowing your search by selecting the genre and/or approximate year of release. Or, try altering your search query."
    return render_template('result.html', search_results=SEARCH_RESULTS,
                            helpful_message = message)
