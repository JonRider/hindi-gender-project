from django.contrib import admin
from .models import Noun, Marker, Request, Suggestion

# Register your models here.
admin.site.register(Noun)
admin.site.register(Marker)
admin.site.register(Request)
admin.site.register(Suggestion)
