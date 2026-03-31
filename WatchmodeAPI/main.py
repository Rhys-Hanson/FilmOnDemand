"Streaming data powered by Watchmode.com"

from dotenv import load_dotenv
import os
from api_data import genre_data
from api_data import source_data
import urllib.request
import urllib.parse
import json

class WatchmodeAPI:

# creates an object of the class
    def __init__(self):
        load_dotenv()

        self.API_KEY = os.getenv("WATCHMODE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file")

        self.base_url = "https://api.watchmode.com/v1/list-titles/?"

# takes a list of strings, genre_data or source_data, and returns its corresponding ID
    def get_genre_or_source_ids(self, data, genre_or_source):
        ids = [] # List of ids for the api call
        temp_dict = {}
        for item in data:
            temp_dict[str(item["name"]).lower()] = item["id"]
        
        for name in genre_or_source:
            name = name.lower().strip()
        if name in temp_dict:
            ids.append(temp_dict[name])
        
        return ids

# takes an actor name as parameter and returns corresponding Watchmode ID
    def get_actor_id(self,actor_name):
        with open("WatchmodeAPI/person_id_map.json", "r", encoding="utf-8") as f:
            person_map = json.load(f)
        return(person_map.get(actor_name))

    def fetch_movies_by_genre(self, genre_ids, source_ids):
        params = {
            "apiKey": self.API_KEY,
            "source_ids": ",".join(str(x) for x in source_ids),
            "types": "movie",
            "regions": "CA",
            "sort_by": "popularity_desc",
            "limit": 10,
            "genres": ",".join(str(x) for x in genre_ids)
        }
        url = self.base_url + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

# takes in the actor's id and the source ids and outputs the json script of the top 10 movies 
    def fetch_movies_by_actor(self, actor_id, source_ids):
        params = {
            "apiKey": self.API_KEY,
            "source_ids": ",".join(str(x) for x in source_ids),
            "types": "movie",
            "regions": "CA",
            "sort_by": "popularity_desc",
            "limit": 10,
            "person_id": actor_id
        }
        url = self.base_url + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

# take the json file from fetch_movies_by_... and parses the results to put only the movie titles in a list
    def parse_results(self, data): 
        movies = []
        for item in data["titles"]:
            movies.append(item["title"])
        return movies






