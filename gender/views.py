from django.shortcuts import render
from django.contrib.auth import authenticate, login as dj_login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
# We use python requests and BeautifulSoup
import requests
from bs4 import BeautifulSoup
# For url validation
import validators

# Import DB models
from .models import Noun, Marker, Request


# Views
def index(request):
    """Main index page. Displays information about the project."""
    # Home Page
    return render(request, "gender/index.html", {"isLoggedIn": request.user.is_authenticated})


def login_view(request):
    """This is our login page. Login is required to make contributions
    but not to view nouns."""

    # Send them to contribute if they are already logged in
    if request.user.is_authenticated:
        return render(request, "gender/contribute.html")

    # Check method
    if request.method == "GET":
        return render(request, "gender/login.html", {"message": ""})
    # POST
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            # Send them to the contribute page
            return render(request, "gender/contribute.html", {"message": ""})
        else:
            return render(request, "gender/login.html", {"message": "Invalid credentials"})


def logout_view(request):
    """Logout user."""
    logout(request)
    return render(request, "gender/login.html", {"message": "Logged out"})

def register(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
       return render(request, "gender/contribute.html", {"message": "You are already registered!"})

    # If they got here from a get request
    if request.method == "GET":
        return render(request, "gender/register.html")
    # Via Post
    else:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        passwordCheck = request.POST["password-check"]

        # Verify password match
        if password != passwordCheck:
            return render(request, "gender/register.html", {"message": "Password doesn't match!"})

        # Look for prexisting user
        user = User.objects.get(username=username)

        # Or register and signin
        if user is None:
            user = User.objects.create_user(username, email, password)
            dj_login(request, user)
            return render(request, "gender/contribute.html", {"message": "Sucsessfully registered!"})
        else:
            return render(request, "gender/register.html", {"message": "User already exists."})

def search(request):
    if request.method == "GET":
        return render(request, "gender/search.html", {"isLoggedIn": request.user.is_authenticated})


def contribute(request):
     # Redirect if user is not logged in
    if not request.user.is_authenticated:
        return render(request, "gender/login.html", {"message": "Login Required to Contribute!"})

    # Check Method
    if request.method == "GET":
        return render(request, "gender/contribute.html")

    if request.method == "POST":

        # get noun
        noun = request.POST["noun"]
        noun = noun.strip()

        # get website
        url = request.POST["url"]

        # check number of requests per day
        try:
            user_requests = Request.objects.get(user=request.user)
        except Request.DoesNotExist:
            user_requests = Request.objects.create(user=request.user)
        # If requests arent from today reset the number
        if user_requests.date != date.today():
            user_requests.date = date.today()
            user_requests.number = 0
            user_requests.save()
        # Add this request
        user_requests.number += 1
        user_requests.save()
        # Check max requests
        if user_requests.number > 10:
            return render(request, "gender/contribute.html", {"message": "You have sumbitted the maximum number of contributions for today"})

        # if they didn't give us a noun send them back
        if noun == "":
            return HttpResponseRedirect(reverse("gender/contribute.html", {"message": "You must enter a noun"}))

        if not validators.url(url):
            return render(request, "gender/contribute.html", {"message": "You must enter the URL on which you found an instance of the Hindi Word"})

        # Test for Hindi Unicode Range
        # https://stackoverflow.com/questions/19704317/how-to-detect-unicode-character-range-in-python
        # by Martijn Pieters
        maxchar = max(noun)
        if u'\u0900' <= maxchar <= u'\u097f':
            pass
        else:
            return render(request, "gender/contribute.html", {"message": "You must enter a Hindi word in Unicode (Read our info page)"})

        # check for only one word
        # https://stackoverflow.com/questions/2311044/determine-if-string-in-input-is-a-single-word-in-python
        # by ghostdog74
        r = noun.split()
        if len(r) != 1:
            return render(request, "gender/contribute.html", {"message": "You can only enter one word at a time"})

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
                    if i > 0:
                        # remove trailing punctuation
                        markers.append(list_of_words[i-1].strip('!,.?'))

        # Word doesn't exist on page
        else:
            return render(request, "gender/contribute.html", {"message": "Could not find that word in the webpage"})

        # How many times was marker repeated?
        # markers_totaled = {}
        # for marker in markers:
        #     if marker in markers_totaled:
        #         markers_totaled[marker] += 1
        #     else:
        #         markers_totaled[marker] = 1

        # Setup Gender Count
        # markers_gender = []
        male_up = 0
        female_up = 0

        # Make an array that has a gender value for each object key
        # for marker in markers_totaled:
        #     try:
        #         mark = Marker.objects.get(word=marker)
        #         if mark.gender == "Masculine":
        #             markers_gender.append("Masculine")
        #         else:
        #             markers_gender.append("Feminine")
        #     except Marker.DoesNotExist:
        #         markers_gender.append("Not a registered marker")


        # check if marker is in gender markers and tally
        for marker in markers:
            try:
                mark = Marker.objects.get(word=marker)
                if f"{mark.gender}" == "M":
                    male_up += 1
                else:
                    female_up += 1
            except Marker.DoesNotExist:
                pass
                # Still need to add to DB

        # create the list of markers with gender
        markers_gender = []
        for marker in markers:
            try:
                mark = Marker.objects.get(word=marker)
                markers_gender.append(mark)
            except Marker.DoesNotExist:
                markers_gender.append({"marker": marker, "gender": "unc"})

        # Return our context to the contribution (result) page
        context = {
            "markers": markers,
            "noun": noun,
            "url": url,
            "number": len(markers),
            "male_up": male_up,
            "female_up": female_up,
            "markers_gender": markers_gender,
        }

        return render(request, "gender/contribution.html", context)



        # for i in range(len(markers)):
        #     rows_markers = db.execute("SELECT * FROM markers WHERE masculine = :marker OR feminine = :marker OR masculine_plural = :marker", marker=markers[i])

            # check to make sure marker exists
            # markerrow = 0
            # for row in rows_markers:
            #     markerrow += 1

        #     # append markers gender
        #     if markerrow > 0:
        #         if rows_markers[0]["masculine"] == markers[i] or rows_markers[0]["masculine_plural"] == markers[i]:
        #             markers_gender.append("masculine")
        #             male_up += 1
        #         elif rows_markers[0]["feminine"] == markers[i]:
        #             markers_gender.append("feminine")
        #             female_up += 1
        #     else:
        #         markers_gender.append("marker not in database or not valid")
        #
        # # combine markers and markers gender into marker_dict to easily display in a table
        # marker_dict = list( {} for i in range(len(markers)))
        # for i in range(len(markers)):
        #     marker_dict[i]["marker"] = markers[i]
        #     marker_dict[i]["gender"] = markers_gender[i]
        #
        # # check if noun is in dictionary
        # rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)
        #
        # # check to make sure word exists
        # nounrow = 0
        # for row in rows:
        #     nounrow += 1
        #
        # # if word exists in db
        # noun_status =""
        # if nounrow > 0:
        #     noun_status ="Word Exists in Database...updating."
        #
        # # insert new word into db
        # if nounrow == 0:
        #     db.execute("INSERT INTO nouns(word) VALUES(:word)", word=noun)
        #     noun_status ="Word Does Not Exist in Database...adding."
        #     # reget database with addition
        #     rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)
        #
        # # increment male votes
        # male_up = male_up + rows[0]["male_vote"]
        # db.execute("UPDATE nouns SET male_vote = :male_vote WHERE word = :word", male_vote=male_up, word=noun)
        #
        # # increment female votes
        # female_up = female_up + rows[0]["female_vote"]
        # db.execute("UPDATE nouns SET female_vote = :female_vote WHERE word = :word", female_vote=female_up, word=noun)
        #
        # # set gender in db
        # # set male
        # if male_up > female_up:
        #     db.execute("UPDATE nouns SET gender_id = 0 WHERE word = :word", word=noun)
        # # set female
        # if female_up > male_up:
        #     db.execute("UPDATE nouns SET gender_id = 1 WHERE word = :word", word=noun)
        # # set contested
        # else:
        #     db.execute("UPDATE nouns SET gender_id = 2 WHERE word = :word", word=noun)
        #
        # # get updated word row after new votes and updated gender
        # rows = db.execute("SELECT * FROM nouns WHERE word = :word", word=noun)
        #
        # # display listed gender
        # gender = ""
        # g_id = rows[0]["gender_id"]
        # if g_id == 0:
        #     gender = "masculine"
        # elif g_id == 1:
        #     gender = "feminine"
        # elif g_id == 2:
        #     gender = "contested"
        # else:
        #     gender = "no data"
        #
        # # get male_vote
        # male_vote = rows[0]["male_vote"]
        #
        # # get female_vote
        # female_vote = rows[0]["female_vote"]
        #
        # # render results
        # return render_template("result.html", noun=noun, noun_status=noun_status, marker_dict=marker_dict, gender=gender, male_vote=male_vote, female_vote=female_vote)
