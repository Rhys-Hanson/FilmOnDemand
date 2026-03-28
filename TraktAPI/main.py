import requests
from dotenv import load_dotenv
import os

load_dotenv()

"Data pulled from api call on Trakt"

class TraktAPI:
    API_KEY = os.getenv("TRAKT_API_KEY")
    base_url = "https://api.trakt.tv"

    def fetch_movies(self, movie_title):
        """
        Searches Trakt trending and popular endpoints for a given movie title.
        Returns raw result data if found, otherwise None.
        """
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.API_KEY
        }

        # Step 1: Check trending endpoint
        trending_url = f"{self.base_url}/movies/trending"
        response = requests.get(trending_url, headers=headers, params={"limit": 100})

        if response.status_code != 200:
            print(f"❌ API key test FAILED. Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

        trending_data = response.json()
        for rank, entry in enumerate(trending_data, start=1):
            if entry["movie"]["title"].lower() == movie_title.lower():
                return self.parse_results(entry, movie_title, rank, source="trending")

        # Step 2: Fallback to popular endpoint
        popular_url = f"{self.base_url}/movies/popular"
        response = requests.get(popular_url, headers=headers, params={"limit": 100})

        if response.status_code != 200:
            print(f"❌ API key test FAILED on popular endpoint. Status code: {response.status_code}")
            return None

        popular_data = response.json()
        for rank, movie in enumerate(popular_data, start=1):
            if movie["title"].lower() == movie_title.lower():
                return self.parse_results({"movie": movie, "watchers": 0}, movie_title, rank, source="popular")

        # Movie not found in either list
        return {"title": movie_title, "found": False, "source": "Trakt"}

    def parse_results(self, raw_data, title, rank, source):
        """
        Parses raw Trakt API response into a structured Movie-compatible dictionary.
        """
        return {
            "title": title,
            "found": True,
            "trending_rank": rank,
            "popularity_score": raw_data.get("watchers", 0),
            "vote_count": raw_data.get("watchers", 0),
            "source": f"Trakt ({source})"
        }


def main():
    api = TraktAPI()
    print("=" * 50)
    print("       Trakt API Key Tester — FilmOnDemand")
    print("=" * 50)
    print("Type a movie title to test the API.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        movie_title = input("Enter a movie title: ").strip()

        if not movie_title:
            print("   Please enter a valid movie title.\n")
            continue

        if movie_title.lower() in ("quit", "exit"):
            print("Exiting tester. Goodbye!")
            break

        print(f"   Searching Trakt for '{movie_title}'...")
        result = api.fetch_movies(movie_title)

        if result is None:
            print("❌ Something went wrong. Check your API key and try again.\n")
        elif not result.get("found"):
            print(f"✅ API key works! But '{movie_title}' was not found in trending or popular lists.")
            print(f"   (The movie may exist on Trakt but isn't currently trending/popular)\n")
        else:
            print(f"✅ API key works! Results for '{movie_title}':")
            for key, value in result.items():
                print(f"   {key}: {value}")
            print()


if __name__ == "__main__":
    main()