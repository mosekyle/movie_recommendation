# movies/recommendation.py

import numpy as np # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
from django.db.models import Avg, Count
from .models import Movie, Rating, Genre

class MovieRecommender:
    """
    Advanced movie recommendation engine combining content-based filtering
    and collaborative filtering techniques.
    """
    
    def __init__(self):
        self.content_weight = 0.4  # Weight for content-based recommendations
        self.collab_weight = 0.6   # Weight for collaborative filtering recommendations
    
    def get_recommendations(self, user_id, num_recommendations=10):
        """
        Get personalized movie recommendations for a user.
        
        Args:
            user_id: ID of the user to get recommendations for
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended Movie objects
        """
        # Get both types of recommendations
        content_based_recs = self.content_based_recommendations(user_id, num_recommendations * 2)
        collab_recs = self.collaborative_filtering_recommendations(user_id, num_recommendations * 2)
        
        # Combine and weight recommendations
        combined_recs = self._combine_recommendations(content_based_recs, collab_recs)
        
        # Return top N recommendations
        return combined_recs[:num_recommendations]
    
    def content_based_recommendations(self, user_id, num_recommendations=20):
        """
        Generate content-based recommendations based on movie genres and attributes
        that the user has highly rated.
        """
        # Get movies the user has rated highly
        user_ratings = Rating.objects.filter(user_id=user_id, rating__gte=4)
        
        if not user_ratings.exists():
            # If user has no ratings, return popular movies
            return self._get_popular_movies(num_recommendations)
        
        # Get the genres of movies the user likes
        liked_genres = {}
        for rating in user_ratings:
            for genre in rating.movie.genres.all():
                if genre.id in liked_genres:
                    liked_genres[genre.id] += rating.rating
                else:
                    liked_genres[genre.id] = rating.rating
        
        # Normalize genre preferences
        total_score = sum(liked_genres.values())
        if total_score > 0:
            for genre_id in liked_genres:
                liked_genres[genre_id] /= total_score
        
        # Get all movies the user hasn't rated yet
        rated_movie_ids = user_ratings.values_list('movie_id', flat=True)
        unwatched_movies = Movie.objects.exclude(id__in=rated_movie_ids)
        
        # Score each movie based on genre match
        movie_scores = []
        for movie in unwatched_movies:
            score = 0
            for genre in movie.genres.all():
                score += liked_genres.get(genre.id, 0)
            
            # Normalize by number of genres to prevent bias towards movies with many genres
            num_genres = movie.genres.count()
            if num_genres > 0:
                score /= num_genres
                
            movie_scores.append((movie, score))
        
        # Sort movies by score and return top recommendations
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in movie_scores[:num_recommendations]]
    
    def collaborative_filtering_recommendations(self, user_id, num_recommendations=20):
        """
        Generate collaborative filtering recommendations based on
        similar users' ratings.
        """
        # Get all users who have rated at least one movie in common with the target user
        user_ratings = Rating.objects.filter(user_id=user_id)
        
        if not user_ratings.exists():
            # If user has no ratings, return popular movies
            return self._get_popular_movies(num_recommendations)
        
        # Find movies rated by the user
        rated_movie_ids = user_ratings.values_list('movie_id', flat=True)
        
        # Find users who rated the same movies
        similar_users = Rating.objects.filter(
            movie_id__in=rated_movie_ids
        ).exclude(
            user_id=user_id
        ).values_list('user_id', flat=True).distinct()
        
        # Calculate user similarity scores
        user_similarities = self._calculate_user_similarities(user_id, similar_users)
        
        # Get movies rated highly by similar users that the target user hasn't rated
        unwatched_movies = Movie.objects.exclude(id__in=rated_movie_ids)
        
        # Score each unwatched movie based on similar users' ratings
        movie_scores = []
        for movie in unwatched_movies:
            score = self._predict_rating(movie.id, user_id, user_similarities)
            movie_scores.append((movie, score))
        
        # Sort by predicted rating and return top recommendations
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in movie_scores[:num_recommendations]]
    
    def _calculate_user_similarities(self, target_user_id, similar_users):
        """
        Calculate similarity scores between target user and other users
        based on their ratings.
        """
        similarities = {}
        target_ratings = dict(Rating.objects.filter(
            user_id=target_user_id
        ).values_list('movie_id', 'rating'))
        
        for other_user_id in similar_users:
            other_ratings = dict(Rating.objects.filter(
                user_id=other_user_id
            ).values_list('movie_id', 'rating'))
            
            # Find movies rated by both users
            common_movies = set(target_ratings.keys()) & set(other_ratings.keys())
            
            if len(common_movies) < 2:
                continue  # Need at least 2 movies in common
            
            # Get ratings vectors for common movies
            target_vector = [target_ratings[movie_id] for movie_id in common_movies]
            other_vector = [other_ratings[movie_id] for movie_id in common_movies]
            
            # Calculate Pearson correlation coefficient
            similarity = self._pearson_correlation(target_vector, other_vector)
            
            # Only consider positively correlated users
            if similarity > 0:
                similarities[other_user_id] = similarity
        
        return similarities
    
    def _pearson_correlation(self, x, y):
        """
        Calculate Pearson correlation coefficient between two vectors.
        """
        x = np.array(x)
        y = np.array(y)
        
        # Handle edge cases
        if len(x) < 2:
            return 0
            
        # Calculate Pearson correlation
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sqrt(np.sum((x - x_mean)**2) * np.sum((y - y_mean)**2))
        
        if denominator == 0:
            return 0
            
        return numerator / denominator
    
    def _predict_rating(self, movie_id, user_id, user_similarities):
        """
        Predict a user's rating for a movie based on similar users' ratings.
        """
        if not user_similarities:
            return 0
            
        # Get all ratings for this movie from similar users
        similar_user_ids = list(user_similarities.keys())
        similar_ratings = Rating.objects.filter(
            movie_id=movie_id,
            user_id__in=similar_user_ids
        )
        
        if not similar_ratings.exists():
            return 0
            
        # Calculate weighted average of ratings
        weighted_sum = 0
        similarity_sum = 0
        
        for rating in similar_ratings:
            similarity = user_similarities[rating.user_id]
            weighted_sum += rating.rating * similarity
            similarity_sum += similarity
            
        if similarity_sum == 0:
            return 0
            
        return weighted_sum / similarity_sum
    
    def _combine_recommendations(self, content_recs, collab_recs):
        """
        Combine content-based and collaborative filtering recommendations
        with appropriate weighting.
        """
        combined = {}
        
        # Add content-based recommendations with weighting
        for i, movie in enumerate(content_recs):
            # Score inversely proportional to position
            score = (len(content_recs) - i) / len(content_recs) * self.content_weight
            combined[movie.id] = {'movie': movie, 'score': score}
        
        # Add collaborative filtering recommendations with weighting
        for i, movie in enumerate(collab_recs):
            # Score inversely proportional to position
            score = (len(collab_recs) - i) / len(collab_recs) * self.collab_weight
            if movie.id in combined:
                combined[movie.id]['score'] += score
            else:
                combined[movie.id] = {'movie': movie, 'score': score}
        
        # Sort results by total score
        result = [info['movie'] for info in 
                  sorted(combined.values(), key=lambda x: x['score'], reverse=True)]
        
        return result
    
    def _get_popular_movies(self, num_movies=10):
        """
        Get popular movies based on average rating and number of ratings.
        Used as fallback when user has no ratings.
        """
        return list(Movie.objects.annotate(
            avg_rating=Avg('rating__rating'),
            num_ratings=Count('rating')
        ).filter(
            num_ratings__gte=5  # At least 5 ratings
        ).order_by('-avg_rating')[:num_movies])
