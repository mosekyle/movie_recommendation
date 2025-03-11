from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Movie, FavoriteMovie

class MovieSerializer(serializers.ModelSerializer):
    """Serializer for movies"""
    
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'overview', 'poster_path', 'release_date', 'vote_average']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation"""
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def validate_password(self, value):
        """Ensure password meets security standards"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def create(self, validated_data):
        """Create a new user with hashed password"""
        return User.objects.create_user(**validated_data)


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """Serializer for user's favorite movies"""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # User as ID
    movie = MovieSerializer(read_only=True)  # Nested movie details

    class Meta:
        model = FavoriteMovie
        fields = ['id', 'user', 'movie', 'added_at']

    def create(self, validated_data):
        """Ensure a user can favorite a movie"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        # Associate the movie with the authenticated user
        validated_data['user'] = request.user
        return super().create(validated_data)
