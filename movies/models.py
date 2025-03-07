from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    vote_average = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_movies = models.ManyToManyField(Movie, related_name='favorited_by', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"