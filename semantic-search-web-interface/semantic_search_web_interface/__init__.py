from flask import Flask, render_template, redirect, request, url_for
from wtforms import Form, SelectField, StringField, validators
from .inference import semantic_query
import logging

GENRE_CHOICES = ['Any', 'Horror', 'SciFi']
YEAR_CHOICES = ['Any', '2010', '2000', '1990', '1980', '1970', '1960', '1950', '1940', '1930', '1920']

SEARCH_RESULTS = []

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('access.log')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class SearchForm(Form):
    query = StringField('Query', validators=[validators.input_required()])
    genre = SelectField('Genre', choices=GENRE_CHOICES)


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/")
    def index():
        return redirect('/search')

    @app.route('/search', methods=['GET', 'POST'])
    def search_page():
        if request.method == 'POST':
            query = request.form['query']
            year = request.form['year']
            #genre = request.form['genre']
            logger.debug("Query: {0}".format(query))
            logger.debug("Genre: {0}".format(genre))
            global SEARCH_RESULTS
            SEARCH_RESULTS = semantic_query(query, {'year': year, 'genre': "Any"})
            return redirect('/result')
        return render_template('search.html', year_choices=YEAR_CHOICES)

    @app.route('/result')
    def result_page():
        return render_template('result.html', search_results=SEARCH_RESULTS)

    return app
