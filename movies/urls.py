from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'movies', views.MovieViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Movie API endpoints
    path('trending/', views.get_trending_movies, name='trending-movies'),
    path('recommendations/<int:movie_id>/', views.get_movie_recommendations, name='movie-recommendations'),
    path('search/', views.search_movies, name='search-movies'),
    path('details/<int:movie_id>/', views.get_movie_details, name='movie-details'),
    
    # User profile and favorites
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('favorites/<int:movie_id>/', views.FavoriteMovieView.as_view(), name='favorite-movie'),
]