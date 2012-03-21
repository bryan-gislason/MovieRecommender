from django.contrib.auth.models import User
from django.db import models


class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    video_release_date = models.DateField()
    imbd_url = models.CharField(max_length=255)
    similarity = models.ManyToManyField('Similarity')
    unknown = models.BooleanField()
    action = models.BooleanField()
    adventure = models.BooleanField()
    animation = models.BooleanField()
    childrens = models.BooleanField()
    comedy = models.BooleanField()
    crime = models.BooleanField()
    documentary = models.BooleanField()
    drama = models.BooleanField()
    fantasy = models.BooleanField()
    film_noir = models.BooleanField()
    horror = models.BooleanField()
    musical = models.BooleanField()
    mystery = models.BooleanField()
    romance = models.BooleanField()
    sci_fi = models.BooleanField()
    thriller = models.BooleanField()
    war = models.BooleanField()
    western = models.BooleanField()


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    rating = models.ForeignKey('Rating')


class Similarity(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    value = models.FloatField()


class Rating(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    value = models.FloatField()
