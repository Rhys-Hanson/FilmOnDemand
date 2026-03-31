"Streaming data powered by Watchmode.com"

from dotenv import load_dotenv
import os
from api_data import genre_data
from api_data import source_data
import urllib.request
import urllib.parse
import json

class WatchmodeAPI:
    def __init__(self):
        load_dotenv()

        self.API_KEY = os.getenv("WATCHMODE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file")

        self.base_url = "https://api.watchmode.com/v1/list-titles/?"

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

#
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

# takes genre_data or source_data and returns its corresponding ID
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

# takes actor name as parameter and returns corresponding Watchmode ID
    def get_actor_id(self,actor_name):
        with open("WatchmodeAPI/person_id_map.json", "r", encoding="utf-8") as f:
            person_map = json.load(f)
        return(person_map.get(actor_name))

# take the data and parse the results to top 10
    def parse_results(self, data): 
        movies = []
        for item in data["titles"]:
            movies.append(item["title"])
        return movies


#--------------------
#testing code below:
#--------------------




api = WatchmodeAPI()
source_ids = api.get_genre_or_source_ids(source_data, ["netflix", "amazon"])
sort_setting = (input("Sort by Genres or Actor?\n")).lower().strip()
if sort_setting == "genre" or sort_setting == "genres":
    genre_ids = api.get_genre_or_source_ids(genre_data, ["romance","comedy"])
    data = api.fetch_movies_by_genre(genre_ids, source_ids)
elif sort_setting == "actor":
    actor_name = input("Enter Actor Name: ") # right now assuming name exists
    actor_id = api.get_genre_or_source_ids(actor_name)
    data = api.fetch_movies_by_actor(actor_id, source_ids)

movies = api.parse_results(data) # take the data and parse the results to top 10

print()
for item in movies:
    print(item)







