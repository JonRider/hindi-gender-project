from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import datetime

# Options
GENDER = [
    ('M', 'Masculine'),
    ('F', 'Feminine'),
]

# Models
class Noun(models.Model):
    word = models.CharField(max_length=64, unique=True)
    female_up = models.PositiveIntegerField(default=0)
    male_up = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word


class Marker(models.Model):
    word = models.CharField(max_length=64, unique=True)
    gender = models.CharField(max_length=2, choices=GENDER)

    def __str__(self):
        return self.word

# Number of requests per day
class Request(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user}'s current # of requests: {self.number}"

# Suggested Marker to add
class Suggestion(models.Model):
    word = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} suggested {self.word}"
