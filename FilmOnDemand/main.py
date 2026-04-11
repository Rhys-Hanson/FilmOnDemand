import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to Python's path so we can import the sibling folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OMDbAPI.main import OMDbAPI
from TMDbAPI.tmdb import TMDbAPI
from TasteDiveAPI.main import TasteDiveAPI
from TraktAPI.main import TraktAPI
from WatchmodeAPI.main import WatchmodeAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.tmdb = TMDbAPI()
        self.tastedive = TasteDiveAPI()
        self.omdb = OMDbAPI()
        self.trakt = TraktAPI()

        self.fetch_type = None
        self.sources = []
        self.genres = []
        self.actor = ""
        self.similar_movies = []

        self.movies_and_ids = {}
        self.movies_with_desc = {}

    def _fetch_streaming_services(self, movie_title):
        watchmode_info = self.watchmode.get_watchmode_movie_info(movie_title)
        if not watchmode_info:
            return []
        return self.watchmode.get_source_names(watchmode_info.get("sources", []))

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
        actors_list = filters.get("actors", [])
        self.actor = actors_list[0] if actors_list else filters.get("actor", "")
        self.similar_movies = filters.get("movies", filters.get("similarMovies", []))
        self.offset = filters.get("offset", 0)

        if self.similar_movies:
            self.fetch_type = "similar_movies"
        else:
            self.fetch_type = "watchmode"

    def get_movies(self):
        if self.fetch_type == "watchmode":
            source_ids = self.watchmode.get_source_ids(self.sources) if self.sources else None
            genre_ids = self.watchmode.get_genre_ids(self.genres) if self.genres else None
            actor_id = self.watchmode.get_actor_id(self.actor) if self.actor else None

            if self.actor and actor_id is None:
                self.movies_and_ids = {}
                return None

            data = self.watchmode.fetch_movies(genre_ids, actor_id, source_ids)
            self.movies_and_ids = self.watchmode.parse_results(data)
            return None

        if self.fetch_type == "similar_movies":
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

        return None

    def get_movie_info(self):
        print("\n--- Fetching TMDb Details ---")
        movie_entries = list(self.movies_and_ids.items())[:20]

        def fetch_tmdb_info(movie_entry):
            movie, movie_id = movie_entry
            try:
                info = self.tmdb.movie_info(movie, movie_id=movie_id)
            except TypeError:
                info = self.tmdb.movie_info(movie)
            info["id"] = str(movie_id or movie)
            info["title"] = movie
            return info

        if movie_entries:
            with ThreadPoolExecutor(max_workers=min(8, len(movie_entries))) as executor:
                movie_info_list = list(executor.map(fetch_tmdb_info, movie_entries))
        else:
            movie_info_list = []

        print("\n--- Fetching Supplemental Details ---")

        def enrich_movie(movie_dict):
            title = movie_dict["title"]
            return {
                "title": title,
                "omdb": self.omdb.enrich(title, year=movie_dict.get("year")) or {},
                "streamingServices": self._fetch_streaming_services(title),
            }

        if movie_info_list:
            with ThreadPoolExecutor(max_workers=min(8, len(movie_info_list))) as executor:
                supplemental_results = list(executor.map(enrich_movie, movie_info_list))
        else:
            supplemental_results = []

        supplemental_lookup = {item["title"]: item for item in supplemental_results}
        trakt_fallbacks = self.trakt.get_rating_fallbacks([movie["title"] for movie in movie_info_list])

        for movie_dict in movie_info_list:
            supplemental_data = supplemental_lookup.get(movie_dict["title"], {})
            movie_dict["streamingServices"] = supplemental_data.get("streamingServices", [])
            movie_dict["imdbScoreSource"] = "omdb"
            movie_dict["rtScoreSource"] = "omdb"
            movie_dict["metacriticScoreSource"] = "omdb"

            omdb_data = supplemental_data.get("omdb") or {}
            trakt_data = trakt_fallbacks.get(movie_dict["title"], {})
            if omdb_data:
                movie_dict["imdbScore"] = omdb_data.get("imdbScore") or 0
                movie_dict["imdbVotes"] = omdb_data.get("imdbVotes")
                movie_dict["rtScore"] = omdb_data.get("rtScore") or 0
                movie_dict["metacriticScore"] = omdb_data.get("metacriticScore") or 0
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

            if not movie_dict.get("imdbScore"):
                movie_dict["imdbScore"] = trakt_data.get("trakt_rating", 0)
                movie_dict["imdbScoreSource"] = "trakt"
            if not movie_dict.get("imdbVotes") and trakt_data.get("rating_votes"):
                movie_dict["imdbVotes"] = f"{trakt_data['rating_votes']:,}"
            if not movie_dict.get("rtScore"):
                movie_dict["rtScore"] = trakt_data.get("trakt_rating", 0)
                movie_dict["rtScoreSource"] = "trakt"
            if not movie_dict.get("metacriticScore"):
                movie_dict["metacriticScore"] = trakt_data.get("rating_votes", 0)
                movie_dict["metacriticScoreSource"] = "trakt"

            movie_dict["traktRating"] = trakt_data.get("trakt_rating", 0)
            movie_dict["traktVotes"] = trakt_data.get("rating_votes", 0)

        self.movies_with_desc = movie_info_list
        return None

    def run_movie_pull(self, settings):
        self.settings(settings)
        filters = json.loads(settings).get("filters", {})
        if filters.get("ai_prompt"):
            from server.ai_service import generate_movie_recommendations

            ai_titles = generate_movie_recommendations(filters.get("ai_prompt"), filters.get("services", []))
            self.movies_and_ids = {title: "" for title in ai_titles}
        else:
            self.get_movies()
        self.get_movie_info()
        return self.movies_with_desc


if __name__ == "__main__":
    films = FilmOnDemand()
    settings = json.dumps(
        {
            "action": "start_game",
            "filters": {
                "genres": ["Romance", "Action"],
                "services": ["Netflix", "Prime Video"],
                "actor": "",
                "similarMovies": [],
            },
        }
    )
    print(films.run_movie_pull(settings))
