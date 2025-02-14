from .prompts import FIND_GENRES
import json
import requests
from requests_cache import CachedSession
from collections import Counter
import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import statistics
import datetime
import heapq
load_dotenv()

class ExplorationScore:
    def __init__(self, user):
        self.user = user 
        self.user_anime_list = [ua for ua in user.anime_list if ua.status != 'Plan to Watch'] 
        self.anime_list = [ua.anime for ua in self.user_anime_list]
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.session = CachedSession(backend='sqlite', cache_name='api_cache')

    def favorite_anime_genres(self):
        """Returns a JSON of a user's favorite genres and 3 animes for each genre"""
        genres = [genre for anime in self.anime_list for genre in anime.genres]
        genre_counts = Counter(genres)
        top_genres = genre_counts.most_common(10)
        top_anime_per_genre = {}
        for genre, _ in top_genres:
            anime_in_genre = list(islice((anime for anime in self.anime_list if genre in anime.genres), 3))
        top_anime_per_genre[genre] = anime_in_genre

        return top_anime_per_genre
        # cache_key = f"favorite_anime_genres_{self.user.id}"
        # if cache_key in self.session.cache:
        #     return json.loads(self.session.cache[cache_key])

        # completion = self.client.beta.chat.completions.parse(
        #     model="gpt-4o-2024-08-06",
        #     messages=[
        #         {"role": "system", "content": FIND_GENRES},
        #         {"role": "user", "content": ", ".join([anime.title for anime in self.anime_list])},
        #     ],
        #     response_format={"type" : "json_object"}
        # )

        # top_genres = json.loads(completion.choices[0].message.content)
        # self.session.cache[cache_key] = json.dumps(top_genres)
        # return top_genres

    def release_date_frequency(self):
        """Returns a dictionary of the year started and the number of animes released in that year"""
        year_counts = Counter()
        for anime in self.anime_list:
            date = anime.start_date
            year = datetime.datetime.strptime(date, '%Y-%m-%d').year
            year_counts[year] += 1
        return dict(year_counts)

    
    def genre_diversity_score(self):
        """
        Uses Tanimoto coefficient to gauge genre diversity. 0 indicates user has only watched one genre, 
        1 indicates user has watched all possible genres.
        """
        genre_counts = Counter()
        for anime in self.anime_list:
            genre_counts.update(anime.genres)
        genre_set = set(genre_counts.keys())
        total_genres = len(genre_set)
        if total_genres == 0:
            return 0
        genre_freq = Counter(genre_counts.values())
        total_genres_watched = sum(genre_freq.values())
        if total_genres_watched == 0:
            return 0
        return len(genre_set) / total_genres_watched

    def contrariancy_score(self):
        """
        How contrarian the user's anime taste is.
        """
        rating_diff = []
        for ua in self.user_anime_list:
            try:
                diff = ua.score - ua.anime.mean
                rating_diff.append(diff)
            except TypeError:
                print("No mean for data point")

        return {
            'average_deviation': statistics.mean(rating_diff), # typical deviation from average score -> with or against the community 
            
            'deviation_consistency': statistics.stdev(rating_diff) if len(rating_diff) > 1 else 0, # inconsistent rating patterns -> strong opinions
            
            'contrarian_percentage': (sum(1 for diff in rating_diff if diff * diff > 1) / len(rating_diff)) * 100}

    def niche_score(self):
        """How niche the user's anime taste is."""
        greater_than_260k = 0
            

    def time_spent_watching(self):
        """How much anime the user watches"""
        print(f'Animes in database {self.anime_list}')
        return len(self.user_anime_list)
    

    def favorite_anime_year(self):
        """Year the user watches the most"""
        year_counts = {}
        for anime in self.anime_list:
            updated_date = datetime.datetime.strptime(anime.updated_at, '%Y-%m-%d')
            year = updated_date.strftime('%Y')
            if year in year_counts:
                year_counts[year] += 1
            else:
                year_counts[year] = 1
        return max(year_counts, key=year_counts.get)

    def most_watched_studio(self):
        """Which studios the user watches the most"""
        studio_counts = {}
        for anime in self.anime_list:
            studio = anime.studio
            if studio in studio_counts:
                studio_counts[studio] += 1
            else:
                studio_counts[studio] = 1
        return max(studio_counts, key=studio_counts.get)

    def least_popular_anime(self):
        """Least popular anime the user has watched"""
        top_5_least_popular_anime = heapq.nsmallest(5, self.anime_list, key=lambda x: x.num_list_users)
        return top_5_least_popular_anime

  


