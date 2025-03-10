from logging import config
import requests

TMDB_API_KEY = config('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def fetch_trending_movies():
    url = f'{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()

def fetch_recommended_movies(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()
