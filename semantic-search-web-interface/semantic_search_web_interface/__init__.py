from flask import Flask, render_template, redirect, request, url_for
from wtforms import Form, SelectField, StringField, validators
from .inference import semantic_query

GENRE_CHOICES = ['Any', 'Horror', 'SciFi']

SEARCH_RESULTS = []


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
            genre = request.form['genre']
            print(query, genre)
            global SEARCH_RESULTS
            SEARCH_RESULTS = semantic_query(query, [])
            print(SEARCH_RESULTS)
            return redirect('/result')
        return render_template('search.html', genre_choices=GENRE_CHOICES)

    @app.route('/result')
    def result_page():
        print(SEARCH_RESULTS)
        return render_template('result.html', search_results=SEARCH_RESULTS)

    return app
