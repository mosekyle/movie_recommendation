from django.contrib import admin
from .models import Movie, UserProfile

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'tmdb_id', 'release_date', 'vote_average')
    search_fields = ('title', 'tmdb_id')
    list_filter = ('release_date',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_count')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('favorite_movies',)
    
    def get_favorite_count(self, obj):
        return obj.favorite_movies.count()
    get_favorite_count.short_description = 'Favorite Movies'