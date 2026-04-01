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

    def get_recommendations(self, query, media_type="movies", limit=10):
        params = {
            "q": query,
            "type": media_type,
            "limit": limit,
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

    def display_results(self, data):
        if not data:
            print("No data returned.")
            return

        similar = data.get("Similar", {})
        info = similar.get("Info", [])
        results = similar.get("Results", [])

        print("\nSeed movie(s):")
        for item in info:
            print("-", item.get("Name", "Unknown"))

        print("\nRecommendations:")
        if not results:
            print("No recommendations found.")
            return

        for item in results:
            print("-", item.get("Name", "Unknown"))

    def run(self, query):
        data = self.get_recommendations(query)
        self.display_results(data)
        return data