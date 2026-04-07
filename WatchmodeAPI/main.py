"Streaming data powered by Watchmode.com"

from dotenv import load_dotenv
import os
from pathlib import Path 
import json
import requests
from functools import lru_cache


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@lru_cache(maxsize=1)
def _load_api_data():
    data_path = Path(__file__).resolve().parent / "api_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_person_map():
    file_path = Path(__file__).resolve().parent / "person_id_map.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_lookup_name(value):
    return str(value).strip().lower()


class WatchmodeAPI:

# creates an object of the class
    def __init__(self):
        data = _load_api_data()

        self.genre_data = data["genre_data"]
        self.source_data = data["source_data"]

        self.API_KEY = os.getenv("WATCHMODE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file\n Get your free api key: https://api.watchmode.com/requestApiKey/")

        self.base_url = "https://api.watchmode.com/v1/list-titles/"
        self.session = requests.Session()
        self.session.trust_env = False
        self._genre_lookup = {
            _normalize_lookup_name(item["name"]): item["id"]
            for item in self.genre_data
            if item.get("name")
        }
        self._source_lookup = {
            _normalize_lookup_name(item["name"]): item["id"]
            for item in self.source_data
            if item.get("name")
        }
        self._source_name_lookup = {
            item["id"]: item["name"]
            for item in self.source_data
            if item.get("id") and item.get("name")
        }

# takes a list of strings through the genres param and returns a corresponding list of IDs
    def get_genre_ids(self, genres):
        return [
            self._genre_lookup[name]
            for genre in genres
            if (name := _normalize_lookup_name(genre)) in self._genre_lookup
        ]

# takes a list of strings through the sources param and returns a corresponding list of IDs
    def get_source_ids(self, sources):
        return [
            self._source_lookup[name]
            for source in sources
            if (name := _normalize_lookup_name(source)) in self._source_lookup
        ]

# takes an actor name as parameter and returns corresponding Watchmode ID from the .json file data provided by Watchmode.com
    def get_actor_id(self, actor_name=None):
        if actor_name:
            return _load_person_map().get(_normalize_lookup_name(actor_name))
        else:
            return None


# fetches movies by genre, actor, and source, returning the json script showing top 20 movies
    def fetch_movies(self, genre_ids=None, actor_id=None, source_ids=None):
        params = {
            "apiKey": self.API_KEY,
            "types": "movie",
            "regions": "CA",
            "sort_by": "popularity_desc",
            "limit": 20,
            "source_types": "sub"
        }
        if source_ids:
            params["source_ids"] = ",".join(str(x) for x in source_ids)
        if genre_ids:
            params["genres"] = ",".join(str(x) for x in genre_ids)
        if actor_id:
            params["person_id"] = actor_id
        
        response = self.session.get(self.base_url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def get_watchmode_movie_info(self, movie_input):
        search_value = movie_input.strip().lower()
        params = {
            "apiKey": self.API_KEY,
            "search_field": "name",
            "types": "movie",
            "search_value": search_value
        }

        response = self.session.get(
            "https://api.watchmode.com/v1/search/",
            params=params,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        exact_match = [
            movie for movie in data.get("title_results", [])
            if movie.get("name", "").lower() == search_value
            and movie.get("type") == "movie"
        ]

        if not exact_match:
            return None

        title_id = exact_match[0]["id"]
        tmdb_id = exact_match[0]["tmdb_id"]

        detail_params = {
            "apiKey": self.API_KEY,
            "append_to_response": "sources",
            "regions": "CA"
        }

        response = self.session.get(
            f"https://api.watchmode.com/v1/title/{title_id}/details/",
            params=detail_params,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        sources = data.get("sources", [])
        sources = [source["source_id"] for source in sources if source.get("type") == "sub"]

        return {"tmdb_id": tmdb_id, "sources": sources}

    def get_source_names(self, source_ids):
        names = []
        seen = set()
        for source_id in source_ids or []:
            name = self._source_name_lookup.get(source_id)
            if name and name not in seen:
                seen.add(name)
                names.append(name)
        return names

# take the json file from fetch_movies_by_? and parses the results and creates a dict of format {titles: tmdb_id}
    def parse_results(self, data): 
        movies = {}
        for item in data["titles"]:
            movies[item["title"]] = item["tmdb_id"]
        return movies
    
