from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for
import re
import os
import numpy as np
from flask import Flask, render_template, request, Response, stream_with_context
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
# from yahoo_team_names import YAHOO_TEAMS # teams data
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp, Length
from rapidfuzz import fuzz as rapid_fuzz
from rapidfuzz import process as rapid_process

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config.update(

    #Set the secret key to a sufficiently random value
    SECRET_KEY=os.urandom(24),

    #Set the session cookie to be secure
    SESSION_COOKIE_SECURE=True,

    #Set the session cookie for our app to a unique name
    SESSION_COOKIE_NAME='YourAppName-WebSession',
)

# Flask-Bootstrap requires this line
Bootstrap(app)

YAHOO_TEAMS = np.load("yahoo_team_names.npy").tolist()

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

def bad_char_search(strg, search=re.compile(r'[^A-Za-z0-9 ]{3,20}').search):
    return not bool(search(strg))

def generate(search_name):
    index = 3 # avoid dividing 1 or 2 by 3 in the next steps. need remainder value to determine column text
    for name in rapid_process.iterExtract(re.escape(search_name), YAHOO_TEAMS, score_cutoff=75):

        yield (name[0].encode('utf-16', 'surrogatepass').decode('utf-16'), index % 3)
        index += 1

@app.route('/')
def home():
    return render_template('search.html')


@app.route('/search/results', methods=['GET', 'POST'])
def search_results():
    search_name = ""
    if request.method == 'GET':
        return redirect("/")
    else:
        search_name = request.form["input"]
    device_width = request.form["device_width"] # String 'true' = 'Desktop Mode' or 'false' = 'Mobile mode'
    messages = ""
    messages = generate(search_name)

    return Response(stream_with_context(stream_template('results.html', messages=messages, device_width=device_width))) # Stream results instead of pre-loading

"""@app.route('/league_search')
def leaguesearchPage():

    title = "League Search"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("league_search.html", title=title, paragraph=paragraph, pageType=pageType)
"""

@app.route('/top_names')
def topnamesPage():
    return render_template("top_names.html")

@app.route('/about')
def aboutPage():
    return render_template("about.html")

if __name__== "__main__":
    app.run()
