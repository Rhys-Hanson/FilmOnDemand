"""
TasteDive API CLI - Film On Demand (Phase 1)
Author: Anish Jami (ajami558)

Seed Selection Module: Generates an initial list of movie recommendations
by finding titles similar to the ones a user already loves.

Usage:
    python main.py
"""

import os
import sys
import requests
from dotenv import load_dotenv


class TasteDiveAPI:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.API_KEY = os.getenv("TASTEDIVE_API_KEY")
        if not self.API_KEY:
            raise ValueError("WATCHMODE_API_KEY not found in .env file\n Get your free api key: https://api.watchmode.com/requestApiKey/")
        BASE_URL = "https://tastedive.com/api/similar"


    def get_recommendations(query, media_type="movie", limit=10, verbose=True):
        """
        Fetch similar movie recommendations from TasteDive API.

        Args:
            query (str): Comma-separated movie titles to find similar results for.
            media_type (str): Type of media to search for (default: "movie").
            limit (int): Maximum number of recommendations to return (default: 10).
            verbose (bool): If True, include descriptions for each result.

        Returns:
            dict: API response containing similar items, or None on failure.
        """
        if not API_KEY:
            print("\n[ERROR] API key not found!")
            print("Please set your TasteDive API key in the .env file.")
            print("  1. Copy .env.example to .env")
            print("  2. Replace 'your_api_key_here' with your actual key")
            print("  Get a free key at: https://tastedive.com/account/api_access")
            return None

        params = {
            "q": query,
            "type": media_type,
            "limit": limit,
            "info": 1 if verbose else 0,
            "k": API_KEY,
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"\n[ERROR] HTTP error: {e}")
            if response.status_code == 401:
                print("Your API key may be invalid. Check your .env file.")
            return None
        except requests.exceptions.ConnectionError:
            print("\n[ERROR] Could not connect to TasteDive API.")
            print("Check your internet connection and try again.")
            return None
        except requests.exceptions.Timeout:
            print("\n[ERROR] Request timed out. Try again later.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] Request failed: {e}")
            return None


    def display_results(data):
        """
        Display the recommendation results in a formatted way.

        Args:
            data (dict): The API response data.
        """
        if not data or "similar" not in data:
            print("\nNo data to display.")
            return

        info = data["similar"].get("info", [])
        results = data["similar"].get("results", [])

        # Display what the user searched for
        print("\n" + "=" * 60)
        print("  SEED MOVIES (What you searched for)")
        print("=" * 60)
        for i, item in enumerate(info, 1):
            name = item.get("name", "Unknown")
            item_type = item.get("type", "Unknown").capitalize()
            print(f"\n  {i}. {name} [{item_type}]")
            
            # Check both wTeaser and description
            desc = item.get("wTeaser") or item.get("description")
            if desc:
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                print(f"     {desc}")

        # Display recommendations
        print("\n" + "=" * 60)
        print("  RECOMMENDATIONS (Similar titles)")
        print("=" * 60)

        if not results:
            print("\n  No recommendations found. Try different movies.")
            return

        for i, item in enumerate(results, 1):
            name = item.get("name", "Unknown")
            # Results often don't include type if filtered by type
            item_type = item.get("type", "movie").capitalize()
            print(f"\n  {i}. {name} [{item_type}]")
            
            desc = item.get("wTeaser") or item.get("description")
            if desc:
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                print(f"     {desc}")
            if item.get("yUrl"):
                print(f"     YouTube: {item['yUrl']}")


    def interactive_menu():
        """
        Run the interactive CLI menu for the TasteDive recommendation tool.
        """
        print("\n" + "=" * 60)
        print("  FILM ON DEMAND - TasteDive Recommendation Engine")
        print("  Phase 1: Seed Selection Module")
        print("  By: Anish Jami")
        print("=" * 60)

        while True:
            print("\n--- Main Menu ---")
            print("1. Get movie recommendations")
            print("2. Search by multiple movies (find common recommendations)")
            print("3. Change result limit")
            print("4. Quick demo (preset search)")
            print("5. Exit")

            choice = input("\nSelect an option (1-5): ").strip()
            result_limit = 10

            if choice == "1":
                movie = input("\nEnter a movie title: ").strip()
                if not movie:
                    print("Please enter a valid movie title.")
                    continue

                print(f"\nSearching for movies similar to '{movie}'...")
                data = get_recommendations(movie, limit=result_limit)
                display_results(data)

            elif choice == "2":
                print("\nEnter multiple movie titles separated by commas.")
                print("Example: The Matrix, Inception, Interstellar")
                movies = input("\nMovies: ").strip()
                if not movies:
                    print("Please enter at least one movie title.")
                    continue

                print(f"\nSearching for movies similar to '{movies}'...")
                data = get_recommendations(movies, limit=result_limit)
                display_results(data)

            elif choice == "3":
                try:
                    new_limit = int(input("\nEnter new result limit (1-30): ").strip())
                    if 1 <= new_limit <= 30:
                        result_limit = new_limit
                        print(f"Result limit set to {result_limit}.")
                    else:
                        print("Please enter a number between 1 and 30.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            elif choice == "4":
                print("\nRunning quick demo with: 'The Dark Knight, Inception'")
                data = get_recommendations("The Dark Knight, Inception", limit=5)
                display_results(data)

            elif choice == "5":
                print("\nGoodbye! Happy watching!")
                sys.exit(0)

            else:
                print("Invalid option. Please select 1-5.")


    def main():
        """Entry point for the CLI application."""
        # Allow a quick one-shot mode via command line args
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"\nSearching for movies similar to '{query}'...")
            data = get_recommendations(query)
            display_results(data)
        else:
            interactive_menu()


    if __name__ == "__main__":
        main()
