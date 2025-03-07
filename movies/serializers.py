from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, UserProfile

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
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    favorite_movies = MovieSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'favorite_movies']