from django.contrib import admin
from .models import FavoriteMovie, Movie
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'tmdb_id', 'release_date', 'vote_average')
    search_fields = ('title', 'tmdb_id')
    list_filter = ('release_date',)

@admin.register(FavoriteMovie)  # ✅ Register FavoriteMovie instead
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('added_at',)