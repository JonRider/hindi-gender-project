from django.shortcuts import render

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
