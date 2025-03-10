from rest_framework import serializers
from django.contrib.auth.models import User
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

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


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
        
        validated_data['user'] = request.user
        return super().create(validated_data)
