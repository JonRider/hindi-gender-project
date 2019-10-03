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
from .models import Noun, Marker, Request, Suggestion

# Functions
def isHindi(word):
    # Test for Hindi Unicode Range
    # https://stackoverflow.com/questions/19704317/how-to-detect-unicode-character-range-in-python
    # by Martijn Pieters
    maxchar = max(word)
    if u'\u0900' <= maxchar <= u'\u097f':
        return True
    else:
        return False

# Views
def index(request):
    """Main index page. Displays information about the project."""

    # Find recent words
    current_list = Noun.objects.all().order_by('-id')[:4]

    # Return context
    context = {
     "current_list": current_list,
     "isLoggedIn": request.user.is_authenticated,
    }

    return render(request, "gender/index.html", context)


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


def results(request):
    if request.method == "GET":
        return render(request, "gender/search.html", {"isLoggedIn": request.user.is_authenticated})
    else:
        noun = request.POST["noun"]
        noun = noun.strip()

        # Check for Hindi Unicode Range
        if isHindi(noun) == False:
            return render(request, "gender/search.html", {"isLoggedIn": request.user.is_authenticated, "message": "Word must be in Hindi unicode format"})

        # See if word is in DB or not
        inDataBase = True
        try:
            word = Noun.objects.get(word=noun)
            inDataBase = True
            # Tally
            if word.female_up > word.male_up:
                gender = "Feminine"
            elif word.female_up == word.male_up:
                gender = "Contested"
            else:
                gender = "Masculine"
        except Noun.DoesNotExist:
            inDataBase = False
            word = None
            gender = None

        context = {
            "noun": noun,
            "word": word,
            "isLoggedIn": request.user.is_authenticated,
            "inDataBase": inDataBase,
            "gender": gender,
        }

        return render(request, "gender/results.html", context)


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
        if isHindi(noun) == False:
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

        # Setup Gender Count
        male_up = 0
        female_up = 0

        # check if marker is in gender markers and tally
        markers_gender = []
        for marker in markers:
            try:
                # See if marker is in the DB
                mark = Marker.objects.get(word=marker)
                # Add marker to the gender list to display
                markers_gender.append(mark)
                if f"{mark.gender}" == "M":
                    male_up += 1
                else:
                    female_up += 1
            except Marker.DoesNotExist:
                # We dont have a marker for this in the DB yet
                markers_gender.append({"marker": marker, "gender": "unc"})

        inDataBase = True
        # See if word is in DB or add it
        try:
            word = Noun.objects.get(word=noun)
            inDataBase = True
        except Noun.DoesNotExist:
            word = Noun.objects.create(word=noun, submitted_by=request.user)
            inDataBase = False

        # Update votes
        word.female_up += female_up
        word.male_up += male_up
        word.save()

        # Tally
        if word.female_up > word.male_up:
            gender = "Feminine"
        elif word.female_up == word.male_up:
            gender = "Contested"
        else:
            gender = "Masculine"

        # Return our context to the contribution (result) page
        context = {
            "markers": markers,
            "noun": noun,
            "url": url,
            "number": len(markers),
            "male_up": male_up,
            "female_up": female_up,
            "markers_gender": markers_gender,
            "inDataBase": inDataBase,
            "total_female": word.female_up,
            "total_male": word.male_up,
            "gender": gender,
        }

        return render(request, "gender/contribution.html", context)


def suggest(request):

   # Don't let them GET this
   if not request.user.is_authenticated:
       return render(request, "gender/login.html", {"message": "Login required to contribute!"})
   # Don't let them GET this
   if request.method == "GET":
      return render(request, "gender/contribute.html")

   if request.method == "POST":
       # Get marker to suggest
       marker = request.POST["marker"]

       # Add to suggestion DB
       try:
           suggestion = Suggestion.objects.get(word=marker)
           # Increment the number of times this has been suggested
           suggestion.count += 1
           suggestion.save()
       except Suggestion.DoesNotExist:
           suggestion = Suggestion.objects.create(word=marker, user=request.user)

       # Context to return to display
       context = {
        "marker": marker,
       }

       return render(request, "gender/suggest.html", context)
