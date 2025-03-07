# Movie Recommendation Backend

A robust Django REST API backend for a movie recommendation application. This backend provides APIs for retrieving trending and recommended movies, user authentication, and saving user preferences.

## Features

- **Movie API Integration**: Integration with TMDb API to fetch and serve movie data
- **User Authentication**: JWT-based authentication system
- **Personal Movie Collections**: Users can save their favorite movies
- **Performance Optimization**: Redis caching for improved API response times
- **API Documentation**: Comprehensive Swagger documentation

## Technologies Used

- **Django**: Web framework for backend development
- **Django REST Framework**: For creating RESTful APIs
- **PostgreSQL**: Relational database for data storage
- **Redis**: Caching system for performance optimization
- **JWT Authentication**: Secure authentication mechanism
- **Swagger**: API documentation

## API Endpoints

### Authentication

- `POST /api/register/`: Register a new user
- `POST /api/token/`: Obtain JWT token pair
- `POST /api/token/refresh/`: Refresh JWT token

### Movie Data

- `GET /api/trending/`: Get trending movies
- `GET /api/recommendations/{movie_id}/`: Get movie recommendations based on a movie
- `GET /api/search/`: Search for movies by title
- `GET /api/details/{movie_id}/`: Get detailed information about a specific movie

### User Preferences

- `GET /api/profile/`: Get user profile with favorite movies
- `POST /api/favorites/{movie_id}/`: Add a movie to favorites
- `DELETE /api/favorites/{movie_id}/`: Remove a movie from favorites

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mosekyle/movie-recommender.git
   cd movie_recommendation
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   DB_NAME=movie
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=your_secret_key
   TMDB_API_KEY=your_tmdb_api_key
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the API documentation at: http://localhost:8000/api/docs/

## Performance Optimization

The application uses Redis to cache:
- Trending movies (6 hours cache)
- Movie recommendations (24 hours cache)
- Search results (6 hours cache)
- Movie details (7 days cache)

This significantly reduces the number of calls to the external TMDb API and improves response times.

## Testing

Run the test suite:
```bash
python manage.py test
```