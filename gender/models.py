from django.db import models
from django.conf import settings

# Options
GENDER = [
    ('M', 'Masculine'),
    ('F', 'Feminine'),
]

# Models
class Noun(models.Model):
    word = models.CharField(max_length=64)
    female_up = models.PositiveIntegerField(default=0)
    male_up = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word


class Marker(models.Model):
    word = models.CharField(max_length=64)
    gender = models.CharField(max_length=2, choices=GENDER)

    def __str__(self):
        return self.word
