from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
 
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    vote_average = models.FloatField(default=0.0)
    genres = models.ManyToManyField(Genre, related_name="movies")  
    def __str__(self):
        return self.title

class Rating(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")  # Link to user
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")  # Link to movie
    rating = models.FloatField()
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title} - {self.rating}"

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)  # Track when the user favorited 
    def __str__(self):
        return f"{self.user.username} favorited {self.movie.title}"

class APILog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Optional (for anonymous users)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField()  # Store how long the API call took
    def __str__(self):
        return f"API call to {self.endpoint} at {self.timestamp}"

