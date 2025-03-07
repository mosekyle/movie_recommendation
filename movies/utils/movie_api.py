import requests

TMDB_API_KEY = '6ed67245ffacbb8bddd71ffdaffe482d'
BASE_URL = 'https://api.themoviedb.org/3'

def fetch_trending_movies():
    url = f'{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()

def fetch_recommended_movies(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()
