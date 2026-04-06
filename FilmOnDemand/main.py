import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to Python's path so we can import the sibling folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WatchmodeAPI.main import WatchmodeAPI
from TraktAPI.main import TraktAPI
from TMDbAPI.tmdb import TMDbAPI
from TasteDiveAPI.main import TasteDiveAPI
from OMDbAPI.main import OMDbAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.trakt = TraktAPI()
        self.tmdb = TMDbAPI()
        self.tastedive = TasteDiveAPI()
        self.omdb = OMDbAPI()
        
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
                "similarMovies": []
            }
        }
        """
        filters = json.loads(config).get("filters", {})

        self.sources = filters.get("services", [])
        self.genres = filters.get("genres", [])
        # Frontend sends `actors` as an array (max 1 item); fall back to legacy `actor` string
        actors_list = filters.get("actors", [])
        self.actor = actors_list[0] if actors_list else filters.get("actor", "")
        self.similar_movies = filters.get("movies", filters.get("similarMovies", []))
        self.offset = filters.get("offset", 0)

        if self.similar_movies:
            self.fetch_type = "similar_movies"
        else:
            self.fetch_type = "watchmode"
        

# Returns a list of the top 10 most relavent movies to the settings
    def get_movies(self):        
        # From Watchmode API
        if self.fetch_type == "watchmode":
            source_ids = self.watchmode.get_source_ids(self.sources) if self.sources else None
            genre_ids = self.watchmode.get_genre_ids(self.genres) if self.genres else None
            actor_id = self.watchmode.get_actor_id(self.actor) if self.actor else None

            # If actor is restricted but they requested a bogus actor name, Watchmode will return everything.
            # We catch it gracefully here by assuming there's no matches as per legacy setup.
            if self.actor and actor_id is None:
                self.movies_and_ids = {}
                return None
                
            data = self.watchmode.fetch_movies(genre_ids, actor_id, source_ids)
            self.movies_and_ids = self.watchmode.parse_results(data)
            return None
        
        # From TasteDive API
        elif self.fetch_type == "similar_movies":
            movie_recs = self.tastedive.run(",".join(self.similar_movies))
            temp_dict = {}
            selected_source_ids = set(self.watchmode.get_source_ids(self.sources)) if self.sources else None
            for movie in movie_recs:
                id_and_sources_dict = self.watchmode.get_watchmode_movie_info(movie)
                if not id_and_sources_dict:
                    continue
                tmdb_id = id_and_sources_dict["tmdb_id"]
                if selected_source_ids is not None:
                    for source in id_and_sources_dict["sources"]:
                        if source in selected_source_ids:
                            temp_dict[movie] = tmdb_id
                            break
                else: 
                    temp_dict[movie] = tmdb_id
            self.movies_and_ids = temp_dict
            return None

# Takes the list of movies titles
    def get_movie_info(self):
        print("\n--- Fetching TMDb Details ---")
        movie_titles = list(self.movies_and_ids.keys())[self.offset : self.offset + 10]

        def fetch_tmdb_info(movie):
            info = self.tmdb.movie_info(movie)
            info["id"] = str(self.movies_and_ids.get(movie) or movie)
            info["title"] = movie # Ensure title is always present
            return info

        if movie_titles:
            with ThreadPoolExecutor(max_workers=min(8, len(movie_titles))) as executor:
                movie_info_list = list(executor.map(fetch_tmdb_info, movie_titles))
        else:
            movie_info_list = []

        # Fetch Trakt stats for all movies in one batch
        print("\n--- Fetching Trakt Details ---")
        filtered_titles = [movie["title"] for movie in movie_info_list]
        trakt_results = self.trakt.rank_movies(filtered_titles) if filtered_titles else []

        # Build a lookup by title so we can match results back
        trakt_lookup = {entry["title"]: entry for entry in trakt_results}

        # Fetch OMDb enrichment in parallel with post-Trakt processing
        print("\n--- Fetching OMDb Details ---")
        def fetch_omdb(movie_dict):
            return self.omdb.enrich(movie_dict["title"], year=movie_dict.get("year"))

        with ThreadPoolExecutor(max_workers=min(8, len(movie_info_list) or 1)) as executor:
            omdb_results = list(executor.map(fetch_omdb, movie_info_list))

        omdb_lookup = {
            movie_info_list[i]["title"]: omdb_results[i]
            for i in range(len(movie_info_list))
        }

        for movie_dict in movie_info_list:
            trakt_data = trakt_lookup.get(movie_dict["title"], {})
            movie_dict["trending_rank"] = trakt_data.get("trending_rank", None)
            movie_dict["watchers"] = trakt_data.get("watchers", 0)
            movie_dict["popularity_rank"] = trakt_data.get("popularity_rank", None)
            movie_dict["total_plays"] = trakt_data.get("total_plays", 0)
            movie_dict["total_watchers"] = trakt_data.get("total_watchers", 0)
            movie_dict["collectors"] = trakt_data.get("collectors", 0)
            movie_dict["trakt_rating"] = trakt_data.get("trakt_rating", "N/A")
            movie_dict["rating_votes"] = trakt_data.get("rating_votes", "N/A")

            # Merge OMDb enrichment — only overwrite if we got real data
            omdb_data = omdb_lookup.get(movie_dict["title"]) or {}
            if omdb_data:
                # Scores — OMDb is authoritative for these
                movie_dict["imdbScore"] = omdb_data.get("imdbScore") or 0
                movie_dict["imdbVotes"] = omdb_data.get("imdbVotes")
                movie_dict["rtScore"] = omdb_data.get("rtScore") or 0
                movie_dict["metacriticScore"] = omdb_data.get("metacriticScore") or 0
                # Context fields — only set if not already populated by TMDb
                if omdb_data.get("writer"):
                    movie_dict["writer"] = omdb_data["writer"]
                if omdb_data.get("language"):
                    movie_dict["language"] = omdb_data["language"]
                if omdb_data.get("country"):
                    movie_dict["country"] = omdb_data["country"]
                if omdb_data.get("awards"):
                    movie_dict["awards"] = omdb_data["awards"]
                if omdb_data.get("boxOffice"):
                    movie_dict["boxOffice"] = omdb_data["boxOffice"]
        
        self.movies_with_desc = movie_info_list
        return None
    
    def run_movie_pull(self, settings):
        self.settings(settings)
        self.get_movies()
        self.get_movie_info()
        return self.movies_with_desc

# Takes in a list, ex [2,1,1,1,-1,-2], which defines the points a person allocated to each movie and the index states the order of the movies it was listed in
    def movie_points(self, JSON_scores):
        movies = {}
        for movie in self.movies_and_ids.keys():
            movies[movie] = JSON_scores


if __name__ == "__main__":
    films = FilmOnDemand()
    settings = json.dumps({
            "action": "start_game",
            "filters": {
                "genres": ["Romance", "Action"],
                "services": ["Netflix","Prime Video"],
                "actor": "",
                "similarMovies": []
            }
        })
    print(films.run_movie_pull(settings))
