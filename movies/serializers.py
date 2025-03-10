from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, FavoriteMovie  

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'overview', 'poster_path', 'release_date', 'vote_average']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        """Create a new user"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user 
class FavoriteMovieSerializer(serializers.ModelSerializer):
    """Serializer for user's favorite movies"""
    user = serializers.StringRelatedField()
    movie = MovieSerializer()

    class Meta:
        model = FavoriteMovie
        fields = ['id', 'user', 'movie', 'added_at']
