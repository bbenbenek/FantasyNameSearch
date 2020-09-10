from flask import Flask, render_template, request, Response, stream_with_context
import re

import numpy as np
from flask import Flask, render_template, request, Response, stream_with_context
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
# from yahoo_team_names import YAHOO_TEAMS # teams data
from fuzzywuzzy import process
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp, Length

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'b8EL!Dpw?@zW3U5zebye;e?(Mwn^Jn'

# Flask-Bootstrap requires this line
Bootstrap(app)

YAHOO_TEAMS = np.load("yahoo_team_names.npy").tolist()

class SearchNameForm(FlaskForm):
    search_name = StringField('Enter team name search term',
                       validators=[InputRequired(message='Search term required to search!'),
                                   Regexp('^[a-zA-Z ]+$', message='Invalid character, only letters and numbers are allowed'),
                                   Length(min=2, max=16, message='Please enter a search term with between 2-16 characters in length')
                                   ])
    submit = SubmitField('Search')

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

def bad_char_search(strg, search=re.compile(r'[^A-Za-z0-9]').search):
    return not bool(search(strg))

def generate(search_name):
    index = 3 # avoid dividing 1 or 2 by 3 in the next steps. need remainder value to determine column text
    for name in process.extractWithoutOrder(re.escape(search_name), YAHOO_TEAMS, score_cutoff=75):
        yield (name[0].encode('utf-16', 'surrogatepass').decode('utf-16'), index % 3)
        index += 1

@app.route('/')
def home():
    return render_template('search.html')


@app.route('/search/results', methods=['GET', 'POST'])
def search_results():
    search_name = ""
    search_name = request.form["input"]
    device_width = request.form["device_width"] # Sting 'true' = 'Desktop Mode' or 'false' = 'Mobile mode'
    print(device_width)
    print(search_name)
    messages = ""
    messages = generate(search_name)

    return Response(stream_with_context(stream_template('results.html', messages=messages, device_width=device_width))) # Stream results instead of pre-loading



"""
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
"""

"""@app.route('/league_search')
def leaguesearchPage():

    title = "League Search"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("league_search.html", title=title, paragraph=paragraph, pageType=pageType)
"""
@app.route('/top_names')
def topnamesPage():

    title = "Top Names"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("top_names.html", title=title, paragraph=paragraph, pageType=pageType)

@app.route('/about')
def aboutPage():

    title = "About this site"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("about.html", title=title, paragraph=paragraph, pageType=pageType)

if __name__== "__main__":
    app.run()
