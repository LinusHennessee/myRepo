from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp
from flask.json import jsonify
import re
import json

class WordForm(FlaskForm):
    avail_letters = StringField("Letters", validators= [
        Regexp(r'^[a-z]*$', message="must contain letters only")
    ])

    word_length = SelectField("Word Length", choices = [('0','Any Length'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')])

    pattern = StringField("Pattern", validators= [
        Regexp(r'^([a-z]|\.)*$', message="must contain only letters and .")
    ])

    submit = SubmitField("Go")

    def validate(self):
        origVal = FlaskForm.validate(self)
        if not origVal:
            return False

        if len(self.avail_letters.data) == 0 and len(self.pattern.data) == 0:
            self.pattern.errors.append('If no pattern provided then letters must be provided')
            return False

        if int(self.word_length.data) != 0 and len(self.pattern.data) != 0 and int(self.word_length.data) != len(self.pattern.data):
            self.pattern.errors.append('Pattern length and Word Length must be equal if both entered')
            return False

        return True


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    if form.validate_on_submit():
        letters = form.avail_letters.data
        length = int(form.word_length.data)
        thePattern = form.pattern.data
    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if length == 0 and not thePattern:
        for l in range(3,len(letters)+1):
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    word_set.add(w)
    elif letters and length != 0:
        for word in itertools.permutations(letters,length):
            w = "".join(word)
            if w in good_words and len(w) == length:
                word_set.add(w)
    elif not letters:
        for w in good_words:
            if len(w) == len(thePattern):
                word_set.add(w)
    else:
        for word in itertools.permutations(letters, len(thePattern)):
            w = "".join(word)
            if w in good_words and len(w) == len(thePattern):
                word_set.add(w)

    if thePattern:
        removeThese = []
        for word in word_set:
            for i in range(0, len(word)):
                if thePattern[i] != '.' and thePattern[i] != word[i]:
                    removeThese.append(word)
                    break

        for werd in removeThese:
            word_set.remove(werd)

    sortedWords = sorted(word_set)
    return render_template('wordlist.html',
        wordlist=sorted(sortedWords, key=len),
        name="CS4131")

@app.route('/words/<word>')
def defproxy(word):
    x = requests.get('https://www.dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=1c1b1b8b-7cba-4e59-8ab2-e2e23ab0e816')
    t = x.text
    j = json.loads(t)
    try:
        definition = j[0]['shortdef'][0]
    except:
        return "No definition available"

    return definition


@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp
