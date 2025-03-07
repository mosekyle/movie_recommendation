from logging import config
import requests
from django.core.cache import cache
import logging
from decouple import config  

logger = logging.getLogger(__name__)

TMDB_API_KEY = config('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_trending_movies(time_window='week', page=1):
    """
    Fetch trending movies from TMDb
    time_window: 'day' or 'week'
    """
    cache_key = f'trending_movies:{time_window}:{page}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        url = f"{BASE_URL}/trending/movie/{time_window}"
        response = requests.get(
            url,
            params={
                'api_key': TMDB_API_KEY,
                'page': page
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Cache data for 6 hours
        cache.set(cache_key, data, 60 * 60 * 6)
        
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching trending movies: {e}")
        return {'results': [], 'error': str(e)}

def get_movie_recommendations(movie_id, page=1):
    """
    Get movie recommendations based on a movie ID
    """
    cache_key = f'movie_recommendations:{movie_id}:{page}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        url = f"{BASE_URL}/movie/{movie_id}/recommendations"
        response = requests.get(
            url,
            params={
                'api_key': TMDB_API_KEY,
                'page': page
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Cache data for 24 hours - recommendations change less frequently
        cache.set(cache_key, data, 60 * 60 * 24)
        
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie recommendations: {e}")
        return {'results': [], 'error': str(e)}

def search_movies(query, page=1):
    """
    Search for movies by title
    """
    cache_key = f'movie_search:{query}:{page}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        url = f"{BASE_URL}/search/movie"
        response = requests.get(
            url,
            params={
                'api_key': TMDB_API_KEY,
                'query': query,
                'page': page
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Cache search results for 6 hours
        cache.set(cache_key, data, 60 * 60 * 6)
        
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching movies: {e}")
        return {'results': [], 'error': str(e)}

def get_movie_details(movie_id):
    """
    Get detailed information about a specific movie
    """
    cache_key = f'movie_details:{movie_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        url = f"{BASE_URL}/movie/{movie_id}"
        response = requests.get(
            url,
            params={
                'api_key': TMDB_API_KEY,
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Cache movie details for 7 days
        cache.set(cache_key, data, 60 * 60 * 24 * 7)
        
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie details: {e}")
        return {'error': str(e)}