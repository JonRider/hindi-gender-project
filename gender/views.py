from django.shortcuts import render
from django.contrib.auth import authenticate, login as dj_login, logout
from django.contrib.auth.models import User

# Import DB models
from .models import Noun, Marker

# Views
def index(request):

    # Access our nouns model
    nouns = Noun.objects.all()

    context = {
        "message": "Hello Everyone!!!!",
        "nouns": nouns
    }

    return render(request, "gender/index.html", context)

def login(request):
    if request.method == "GET":
        return render(request, "gender/login.html", {"message": ""})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            # Eventually this will redirect to a new page
            return render(request, "gender/login.html", {"message": "Logged in Successfully"})
        else:
            return render(request, "gender/login.html", {"message": "Invalid credentials."})
