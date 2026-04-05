"Streaming data powered by Watchmode.com"

from dotenv import load_dotenv
import os
from .api_data import genre_data, source_data
import urllib.request
from urllib.parse import urlencode
from pathlib import Path 
import json


class WatchmodeAPI:

# creates an object of the class
    def __init__(self):
        self.genre_data = genre_data
        self.source_data = source_data
        
        ROOT_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(ROOT_DIR / ".env")

        self.API_KEY = os.getenv("WATCHMODE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file\n Get your free api key: https://api.watchmode.com/requestApiKey/")

        self.base_url = "https://api.watchmode.com/v1/list-titles/?"

# takes a list of strings through the genres param and returns a corresponding list of IDs
    def get_genre_ids(self, genres):
        ids = [] # List of ids for the api call
        temp_dict = {}
        for item in self.genre_data:
            temp_dict[str(item["name"]).lower()] = item["id"]
        
        for name in genres:
            name = name.lower().strip()
        if name in temp_dict:
            ids.append(temp_dict[name])
        
        return ids

# takes a list of strings through the sources param and returns a corresponding list of IDs
    def get_source_ids(self, sources):
        ids = [] # List of ids for the api call
        temp_dict = {}
        for item in self.source_data:
            temp_dict[str(item["name"]).lower()] = item["id"]
        
        for name in sources:
            name = name.lower().strip()
        if name in temp_dict:
            ids.append(temp_dict[name])
        
        return ids

# takes an actor name as parameter and returns corresponding Watchmode ID from the .json file data provided by Watchmode.com
    def get_actor_id(self, actor_name):
        file_path = Path(__file__).resolve().parent / "person_id_map.json"
        with open(file_path, "r", encoding="utf-8") as f:
            person_map = json.load(f)
        return person_map.get(actor_name.lower().strip())


# takes a list of genres ids and source ids and outputs the json script of the top 10 movies
    def fetch_movies_by_genre(self, genre_ids, source_ids=None):
        params = {
            "apiKey": self.API_KEY,
            "source_ids": ",".join(str(x) for x in source_ids),
            "types": "movie",
            "regions": "CA",
            "sort_by": "popularity_desc",
            "limit": 20,
            "genres": ",".join(str(x) for x in genre_ids)
        }
        url = self.base_url + urlencode(params)
        
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

# takes in the actor's id and the source ids and outputs the json script of the top 10 movies 
    def fetch_movies_by_actor(self, actor_id, source_ids=None):
        params = {
            "apiKey": self.API_KEY,
            "source_ids": ",".join(str(x) for x in source_ids),
            "types": "movie",
            "regions": "CA",
            "sort_by": "popularity_desc",
            "limit": 20,
            "person_id": actor_id
        }
        url = self.base_url + urlencode(params)
        
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

    def get_watchmode_movie_info(self, movie_input):
        search_value = movie_input.lower()
        params = {
            "apiKey": self.API_KEY,
            "search_field": "name",
            "types" : "movie",
            'search_value': search_value
        }

        url = f'https://api.watchmode.com/v1/search/?{urlencode(params)}'

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        exact_match = [
            movie for movie in data.get("title_results", [])
            if movie.get("name", "").lower() == movie_input
            and movie.get("type") == "movie"
        ]
        if not exact_match:
            return None

        title_id = exact_match[0]["id"] 
        
        url = f'https://api.watchmode.com/v1/title/{title_id}/details/?apiKey={self.API_KEY}&append_to_response=sources&regions=CA'

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        sources = data.get("sources", [])
        sources = [source["source_id"] for source in sources if source["type"] == "sub"]
        
        return {"sources": sources}

# take the json file from fetch_movies_by_? and parses the results and creates a dict of format {titles: tmdb_id}
    def parse_results(self, data): 
        movies = {}
        for item in data["titles"]:
            movies[item["title"]] = item["tmdb_id"]
        return movies
    
    def run_for_actors(self, actor_name, sources):
        source_ids = self.get_source_ids(sources)
        actor_id = self.get_actor_id(actor_name.lower().strip())

        if actor_id is None:
            print("Actor not found.")
            return []

        data = self.fetch_movies_by_actor(actor_id, source_ids)
        movie_list = self.parse_results(data)
        return movie_list
    
    def run_for_genres(self, genres, sources):
        source_ids = self.get_source_ids(sources)
        genre_ids = self.get_genre_ids(genres)

        data = self.fetch_movies_by_genre(genre_ids, source_ids)
        movie_list = self.parse_results(data)
        return movie_list

