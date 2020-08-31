import os
from flask import Flask, redirect, render_template, request, Response, stream_with_context, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp, Length
from yahoo_team_names import YAHOO_TEAMS # teams data
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


app = Flask(__name__)#, static_folder='../templates/')

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'b8EL!Dpw?@zW3U5zebye;e?(Mwn^Jn'

# Flask-Bootstrap requires this line
Bootstrap(app)

#with open('yahoo_team_names.txt') as json_file:
#    list_of_names = json.load(json_file)

class SearchNameForm(FlaskForm):
    search_name = StringField('Enter team name search term',
                       validators=[InputRequired(message='Search term required to search!'),
                                   Regexp('^[a-zA-Z]+$', message='Invalid character, only letters and numbers are allowed'),
                                   Length(min=2, max=16, message='Please enter a search term with between 2-16 characters in length')
                                   ])
    submit = SubmitField('Search')

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


def generate(search_name):
    index = 3 # avoid dividing 1 or 2 by 3 in the next steps. need remainder value to determine column text
    for name in process.extractWithoutOrder(re.escape(search_name), YAHOO_TEAMS, score_cutoff=75):
        yield (name[0].encode('utf-16', 'surrogatepass').decode('utf-16'), index % 3)
        index += 1

@app.route('/', methods=['GET', 'POST'])
def index():
    search_form = SearchNameForm()
    #message = ""
    messages=""
    search_name = ""
    if search_form.validate_on_submit(): # VALIDATE
        search_name = search_form.search_name.data
        search_form.search_name.data = "" # Clear the form field
        print("Running search...", search_name)

        #messages = generate(search_name)

    #return render_template('index.html', form=search_form, message=message)
    return Response(stream_with_context(stream_template('index.html', form=search_form, messages=generate(search_name)))) # Stream results instead of pre-loading

"""
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
"""

@app.route('/league_search')
def leaguesearchPage():

    title = "League Search"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("base.html", title=title, paragraph=paragraph, pageType=pageType)

@app.route('/top_names')
def topnamesPage():

    title = "Top Names"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("base.html", title=title, paragraph=paragraph, pageType=pageType)

@app.route('/about')
def aboutPage():

    title = "About this site"
    paragraph = ["Page under construction"]

    pageType = 'about'

    return render_template("base.html", title=title, paragraph=paragraph, pageType=pageType)

if __name__== "__main__":
    app.run()