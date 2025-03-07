from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .recommendation import MovieRecommender
from .serializers import MovieSerializer
from .models import Movie, UserProfile
from .serializers import MovieSerializer, UserSerializer, UserProfileSerializer
from . import tmdb_api

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_trending_movies(request):
    time_window = request.query_params.get('time_window', 'week')
    page = request.query_params.get('page', 1)
    
    data = tmdb_api.get_trending_movies(time_window, page)
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_movie_recommendations(request, movie_id):
    page = request.query_params.get('page', 1)
    
    data = tmdb_api.get_movie_recommendations(movie_id, page)
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_movies(request):
    query = request.query_params.get('query', '')
    page = request.query_params.get('page', 1)
    
    if not query:
        return Response(
            {"error": "Query parameter is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = tmdb_api.search_movies(query, page)
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_movie_details(request, movie_id):
    data = tmdb_api.get_movie_details(movie_id)
    
    if 'error' in data:
        return Response({"error": data['error']}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(data)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class FavoriteMovieView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, movie_id):
        profile = get_object_or_404(UserProfile, user=request.user)
        
        # Get movie details from TMDb
        movie_data = tmdb_api.get_movie_details(movie_id)
        
        if 'error' in movie_data:
            return Response({"error": movie_data['error']}, status=status.HTTP_404_NOT_FOUND)
        
        # Create or get movie instance
        movie, created = Movie.objects.get_or_create(
            tmdb_id=movie_data['id'],
            defaults={
                'title': movie_data['title'],
                'overview': movie_data['overview'],
                'poster_path': movie_data.get('poster_path'),
                'release_date': movie_data.get('release_date'),
                'vote_average': movie_data.get('vote_average', 0.0)
            }
        )
        
        # Add to favorites
        profile.favorite_movies.add(movie)
        
        return Response({"message": f"Added {movie.title} to favorites"})
    
    def delete(self, request, movie_id):
        profile = get_object_or_404(UserProfile, user=request.user)
        movie = get_object_or_404(Movie, tmdb_id=movie_id)
        
        # Remove from favorites
        if movie in profile.favorite_movies.all():
            profile.favorite_movies.remove(movie)
            return Response({"message": f"Removed {movie.title} from favorites"})
        else:
            return Response(
                {"error": "Movie not in favorites"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
class MovieRecommendationView(APIView):
    """
    API endpoint to get personalized movie recommendations.
    """
    
    def get(self, request, format=None):
        """
        Get personalized recommendations for the current user.
        """
        # Get user ID from request
        user_id = request.user.id
        
        # Get number of recommendations (default: 10)
        try:
            count = int(request.query_params.get('count', 10))
        except ValueError:
            count = 10
        
        # Initialize recommender and get recommendations
        recommender = MovieRecommender()
        recommended_movies = recommender.get_recommendations(user_id, count)
        
        # Serialize the recommendations
        serializer = MovieSerializer(recommended_movies, many=True)
        
        return Response({
            'count': len(recommended_movies),
            'recommendations': serializer.data
        })
