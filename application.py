import requests
from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
import validators

# hardcoded url for testing
#url = 'http://www.jagran.com/business/biz-gold-soars-by-990-rupee-to-31350-rupee-on-positive-global-cues-16675261.html'
# hardcoded page we are currently searching

# run our flask app
app = Flask(__name__)

# ensure responses aren't cached - from cs50 Finance
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///gender.db")

# default app route
@app.route("/")
def index():
    return render_template("index.html")

# search page
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":

        # get noun
        noun = request.form.get("noun")
        noun = noun.strip()

        # get website
        url = request.form.get("url")

        # setup blank error message
        error = ""

        # if they didn't give us a noun send them back
        if not request.form.get("noun"):
            return redirect(url_for("index"))

        if not validators.url(url):
            error = "You must enter the URL on which you found an instance of the Hindi Word"
            return render_template("search.html", error=error)

        # Test for Hindi Unicode Range
        # https://stackoverflow.com/questions/19704317/how-to-detect-unicode-character-range-in-python
        # by Martijn Pieters
        maxchar = max(noun)
        if u'\u0900' <= maxchar <= u'\u097f':
            pass
        else:
            error = "You must enter a Hindi word in Unicode (Read our info page)"
            return render_template("search.html", error=error)

        # check for only one word
        # https://stackoverflow.com/questions/2311044/determine-if-string-in-input-is-a-single-word-in-python
        # by ghostdog74
        r = noun.split()
        if len(r) != 1:
            error = "You can only enter one word"
            return render_template("search.html", error=error)

        # make this a function later
        # find gender
        resp = requests.get(url)
        bsoup = BeautifulSoup(resp.text, "lxml")
        text = bsoup.get_text()
        # find the gender marker (prev_word)
        list_of_words = text.split()

        # setup markers variable
        markers = []
        # find gender marker from stripped webpage
        if noun in list_of_words:
            # find all instances of noun and it's prev_word
            for i,w in enumerate(list_of_words):
                if w == noun:
                # previous word
                    if i>0:
                        # remove trailing punctuation
                        markers.append(list_of_words[i-1].strip('!,.?'))

        else:
            error = "Could not find that word in the webpage"
            return render_template("search.html", error=error)

        markers_gender = []
        male_up = 0
        female_up = 0
        # check if marker is in gender markers
        for i in range(len(markers)):
            rows_markers = db.execute("SELECT * FROM markers WHERE masculine = :marker OR feminine = :marker OR masculine_plural = :marker", marker=markers[i])

            # check to make sure marker exists
            markerrow = 0
            for row in rows_markers:
                markerrow += 1

            # append markers gender
            if markerrow > 0:
                if rows_markers[0]["masculine"] == markers[i] or rows_markers[0]["masculine_plural"] == markers[i]:
                    markers_gender.append("masculine")
                    male_up += 1
                elif rows_markers[0]["feminine"] == markers[i]:
                    markers_gender.append("feminine")
                    female_up += 1
            else:
                markers_gender.append("marker not in database or not valid")

        # combine markers and markers gender into marker_dict to easily display in a table
        marker_dict = list( {} for i in range(len(markers)))
        for i in range(len(markers)):
            marker_dict[i]["marker"] = markers[i]
            marker_dict[i]["gender"] = markers_gender[i]

        # check if noun is in dictionary
        rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)

        # check to make sure word exists
        nounrow = 0
        for row in rows:
            nounrow += 1

        # if word exists in db
        noun_status =""
        if nounrow > 0:
            noun_status ="Word Exists in Database...updating."

        # insert new word into db
        if nounrow == 0:
            db.execute("INSERT INTO nouns(word) VALUES(:word)", word=noun)
            noun_status ="Word Does Not Exist in Database...adding."
            # reget database with addition
            rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)

        # increment male votes
        male_up = male_up + rows[0]["male_vote"]
        db.execute("UPDATE nouns SET male_vote = :male_vote WHERE word = :word", male_vote=male_up, word=noun)

        # increment female votes
        female_up = female_up + rows[0]["female_vote"]
        db.execute("UPDATE nouns SET female_vote = :female_vote WHERE word = :word", female_vote=female_up, word=noun)

        # set gender in db
        # set male
        if male_up > female_up:
            db.execute("UPDATE nouns SET gender_id = 0 WHERE word = :word", word=noun)
        # set female
        if female_up > male_up:
            db.execute("UPDATE nouns SET gender_id = 1 WHERE word = :word", word=noun)
        # set contested
        else:
            db.execute("UPDATE nouns SET gender_id = 2 WHERE word = :word", word=noun)

        # get updated word row after new votes and updated gender
        rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)

        # display listed gender
        gender = ""
        g_id = rows[0]["gender_id"]
        if g_id == 0:
            gender = "masculine"
        elif g_id == 1:
            gender = "feminine"
        elif g_id == 2:
            gender = "contested"
        else:
            gender = "no data"

        # get male_vote
        male_vote = rows[0]["male_vote"]

        # get female_vote
        female_vote = rows[0]["female_vote"]

        # render results
        return render_template("result.html", noun=noun, noun_status=noun_status, marker_dict=marker_dict, gender=gender, male_vote=male_vote, female_vote=female_vote)

# else if user reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("search.html")

# find
@app.route("/find", methods=["GET", "POST"])
def find():
    if request.method == "POST":

        # get noun
        found = request.form.get("find")
        found = found.strip()

        # setup blank error message
        error = ""

        # Test for Hindi Unicode Range
        # https://stackoverflow.com/questions/19704317/how-to-detect-unicode-character-range-in-python
        # by Martijn Pieters
        maxchar = max(found)
        if u'\u0900' <= maxchar <= u'\u097f':
            pass
        else:
            error = "You must enter a Hindi word in Unicode (Read our info page)"
            return render_template("find.html", error=error)

        # check for only one word
        # https://stackoverflow.com/questions/2311044/determine-if-string-in-input-is-a-single-word-in-python
        # by ghostdog74
        r = found.split()
        if len(r) != 1:
            error = "You can only enter one word"
            return render_template("find.html", error=error)


        # check if noun is in dictionary
        rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=found)

        # check to make sure word exists
        nounrow = 0
        for row in rows:
            nounrow += 1

        # if word exists in db
        noun_status =""
        if nounrow > 0:
            noun_status ="Word Exists in Database."
        else:
            noun_status ="Word Does Not Exist in Database."
            return render_template("found.html", noun=found, noun_status=noun_status)

        # display listed gender
        gender = ""
        g_id = rows[0]["gender_id"]
        if g_id == 0:
            gender = "masculine"
        elif g_id == 1:
            gender = "feminine"
        elif g_id == 2:
            gender = "contested"
        else:
            gender = "no data"

        # get male_vote
        male_vote = rows[0]["male_vote"]

        # get female_vote
        female_vote = rows[0]["female_vote"]

        # render results
        return render_template("found.html", noun=found, noun_status=noun_status, gender=gender, male_vote=male_vote, female_vote=female_vote)

    # if by GET
    else:
        return render_template("find.html")

# markers page
@app.route("/markers", methods=["GET", "POST"])
def markers():
    if request.method == "GET":

        # lookup our markers
        rows = db.execute("SELECT * FROM markers")

        # render results
        return render_template("markers.html", markers=rows)

    if request.method == "POST":

        # get noun
        suggested = request.form.get("suggest")
        suggested = suggested.strip()

        # lookup our markers
        rows = db.execute("SELECT * FROM markers")


        # setup blank error message
        error = ""

        # Test for Hindi Unicode Range
        # https://stackoverflow.com/questions/19704317/how-to-detect-unicode-character-range-in-python
        # by Martijn Pieters
        maxchar = max(suggested)
        if u'\u0900' <= maxchar <= u'\u097f':
            pass
        else:
            error = "You must enter a Hindi word in Unicode (Read our info page)"
            return render_template("markers.html", error=error)

        # check for only one word
        # https://stackoverflow.com/questions/2311044/determine-if-string-in-input-is-a-single-word-in-python
        # by ghostdog74
        r = suggested.split()
        if len(r) != 1:
            error = "You can only enter one word"
            return render_template("markers.html", markers=rows, error=error)

        # add suggestion to database and thank user
        db.execute("INSERT INTO suggestions(suggestion) VALUES(:word)", word=suggested)
        return render_template("suggestions.html")