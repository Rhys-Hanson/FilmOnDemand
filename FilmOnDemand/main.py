import sys
import os
import json

# Add the parent directory to Python's path so we can import the sibling folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WatchmodeAPI.main import WatchmodeAPI
from TraktAPI.main import TraktAPI
from TMDbAPI.tmdb import TMDbAPI
from TasteDiveAPI.main import TasteDiveAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.trakt = TraktAPI()
        self.tmdb = TMDbAPI()
        self.tastedive = TasteDiveAPI()
        
        self.fetch_type = None
        self.sources = []
        self.genres = []
        self.actor = ""
        self.similar_movies = []
        
        self.movies_and_ids = {}
        self.movies_with_desc = {}

    def settings(self, config):
        
        """
        Accepts a JSON string as follows:
        {
            "action": "start_game",
            "filters": {
                "genres": ["Horror", "Action"],
                "services": ["Netflix"],
                "actor": None,
                "yearRange": [1990, 2024],
                "similarMovies": []
            }
        }
        """
        filters = json.loads(config).get("filters", {})

        self.sources = filters.get("services", [])
        self.genres = filters.get("genres", [])
        self.actor = filters.get("actor", "")
        self.year_range = filters.get("yearRange", None)
        self.similar_movies = filters.get("similarMovies", [])

        if self.actor:
            self.fetch_type = "actor"
        elif self.similar_movies:
            self.fetch_type = "similar_movies"
        else:
            self.fetch_type = "genre"
        

# Returns a list of the top 10 most relavent movies to the settings
    def get_movies(self):        
        # From Watchmode API
        if self.fetch_type == "actor":
            self.movies_and_ids = self.watchmode.run_for_actors(self.actor, self.sources)
            return None
        elif self.fetch_type == "genre":
            self.movies_and_ids = self.watchmode.run_for_genres(self.genres, self.sources)
            return None
        
        # From TasteDive API
        elif self.fetch_type == "similar_movies":
            movie_recs = self.tastedive.run(",".join(self.similar_movies))
            temp_dict = {}
            for movie in movie_recs:
                id_and_sources_dict = self.watchmode.get_watchmode_movie_info(movie)
                tmdb_id = id_and_sources_dict["tmdb_id"]
                if self.sources:
                    for source in id_and_sources_dict["sources"]:
                        if source in self.watchmode.get_source_ids(self.sources):
                            temp_dict[movie] = tmdb_id
                            break
                else: 
                    temp_dict[movie] = tmdb_id
            self.movies_and_ids = temp_dict
            return None

# Takes the list of movies titles
    def get_movie_info(self):
        movie_titles = list(self.movies_and_ids.keys())
        movie_info = {movie : self.tmdb.movie_info(movie) for movie in movie_titles}

        # Fetch Trakt stats for all movies in one batch
        trakt_results = self.trakt.rank_movies(movie_titles)

        # Build a lookup by title so we can match results back
        trakt_lookup = {entry["title"]: entry for entry in trakt_results}

        for movie in movie_titles:
            trakt_data = trakt_lookup.get(movie, {})
            movie_info[movie]["trending_rank"] = trakt_data.get("trending_rank", None)
            movie_info[movie]["watchers"] = trakt_data.get("watchers", 0)
            movie_info[movie]["popularity_rank"] = trakt_data.get("popularity_rank", None)
            movie_info[movie]["total_plays"] = trakt_data.get("total_plays", 0)
            movie_info[movie]["total_watchers"] = trakt_data.get("total_watchers", 0)
            movie_info[movie]["collectors"] = trakt_data.get("collectors", 0)
            movie_info[movie]["trakt_rating"] = trakt_data.get("trakt_rating", "N/A")
            movie_info[movie]["rating_votes"] = trakt_data.get("rating_votes", "N/A")
        
        self.movies_with_desc = json.dumps(movie_info, indent=4)
        return None
    
    def run_movie_pull(self, settings):
        self.settings(settings)
        self.get_movies()
        self.get_movie_info()
        return self.movies_with_desc

# Takes in a list, ex [2,1,1,1,-1,-2], which defines the points a person allocated to each movie and the index states the order of the movies it was listed in
    def movie_points(self, JSON_scores):
        movies = {}
        
        for movie in self.movie_titles:
            movies[movie] = JSON_scores


if __name__ == "__main__":
    films = FilmOnDemand()
    settings = json.dumps({
            "action": "start_game",
            "filters": {
                "genres": ["Romance", "Action"],
                "services": ["Netflix","Prime Video"],
                "actor": "",
                "yearRange": [1990, 2024],
                "similarMovies": []
            }
        })
    print(films.run_movie_pull(settings))