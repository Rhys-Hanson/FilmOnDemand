import os
import requests
from dotenv import load_dotenv


class TasteDiveAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("TASTEDIVE_API_KEY")
        self.base_url = "https://tastedive.com/api/similar"

        if not self.api_key:
            raise ValueError("TASTEDIVE_API_KEY not found in .env file")

    # Return the api json from query: "List of movies separated by commas"
    def get_movies(self, query, media_type="movie"):
        params = {
            "q": query,
            "type": media_type,
            "limit": 20,
            "k": self.api_key,
            "info": 1
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None

    def parse_results(self, data):
        if not data:
            print("No data returned.")
            return

        similar = data.get("similar", {})
        results = similar.get("results", []) #the actual list of data
        movie_list = []
        
        if not results:
            print("No recommendations found.")
            return
        
        for item in results:
            movie_list.append(item.get("name"))
        return movie_list

    def run(self, query):
        data = self.get_movies(query)
        movies = self.parse_results(data)
        return movies