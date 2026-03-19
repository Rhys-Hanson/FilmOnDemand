"Streaming data powered by Watchmode.com"

from dotenv import load_dotenv
import os
from api_data import genre_data
from api_data import source_data
import urllib.request
import urllib.parse
import json


"Data pulled from api call on Watchmode.com"

class WatchmodeAPI:
    def __init__(self):
        load_dotenv()

        self.API_KEY = os.getenv("WATCHMODE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file")

        self.base_url = "https://api.watchmode.com/v1/list-titles/?"

    def fetch_movies(self, genre_ids, source_ids):
        params = {
            "apiKey": self.API_KEY,
            "source_ids": ",".join(str(x) for x in source_ids),
            "types": "movie",
            "sort_by": "popularity_desc",
            "limit": 10,
            "genres": ",".join(str(x) for x in genre_ids)
        }

        url = self.base_url + urllib.parse.urlencode(params)

        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

    def parse_results(self, data):
        movies = []
        for item in data["titles"]:
            movies.append(item["title"])
        return movies

    def get_ids(self, data, label):
        ids = [] # List of ids for the api call
        temp_dict = {}
        for item in data:
            temp_dict[item["name"].lower()] = item["id"]

        while True:
            user_input = input(f'Enter {label} (or type "esc" to finish): ').lower().strip()
            if user_input == "esc":
                break
            while user_input not in temp_dict:
                user_input = input(f'Invalid {label}. \nEnter {label} again or type "esc" to finish: ').lower().strip()
                if user_input == "esc":
                    break
            if user_input == "esc":
                break
            ids.append(temp_dict[user_input])
        return ids


input("Press enter to start")
api = WatchmodeAPI()
genre_ids = api.get_ids(genre_data, "genre")
source_ids = api.get_ids(source_data, "streaming service")
data = api.fetch_movies(genre_ids, source_ids)
movies = api.parse_results(data)

print()
for item in movies:
    print(item)







