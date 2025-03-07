from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Movie, UserProfile

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)

class MovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test movie
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title='Fight Club',
            overview='An insomniac office worker...',
            release_date='1999-10-15',
            vote_average=8.4
        )

    @patch('api.tmdb_api.get_trending_movies')
    def test_trending_movies_endpoint(self, mock_get_trending):
        # Mock the API response
        mock_get_trending.return_value = {
            'results': [
                {'id': 550, 'title': 'Fight Club'}
            ]
        }
        
        url = reverse('trending-movies')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        mock_get_trending.assert_called_once()

    @patch('api.tmdb_api.search_movies')
    def test_search_movies_endpoint(self, mock_search):
        # Mock the API response
        mock_search.return_value = {
            'results': [
                {'id': 550, 'title': 'Fight Club'}
            ]
        }
        
        url = f"{reverse('search-movies')}?query=fight"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        mock_search.assert_called_once_with('fight', 1)

class FavoriteMovieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test movie
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title='Fight Club',
            overview='An insomniac office worker...',
            release_date='1999-10-15',
            vote_average=8.4
        )
        
        self.profile = UserProfile.objects.get(user=self.user)

    @patch('api.tmdb_api.get_movie_details')
    def test_add_favorite_movie(self, mock_get_details):
        # Mock the API response
        mock_get_details.return_value = {
            'id': 550,
            'title': 'Fight Club',
            'overview': 'An insomniac office worker...',
            'release_date': '1999-10-15',
            'vote_average': 8.4
        }
        
        url = reverse('favorite-movie', kwargs={'movie_id': 550})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.favorite_movies.count(), 1)
        self.assertEqual(self.profile.favorite_movies.first(), self.movie)

    def test_remove_favorite_movie(self):
        # Add movie to favorites first
        self.profile.favorite_movies.add(self.movie)
        self.assertEqual(self.profile.favorite_movies.count(), 1)
        
        url = reverse('favorite-movie', kwargs={'movie_id': 550})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.favorite_movies.count(), 0)