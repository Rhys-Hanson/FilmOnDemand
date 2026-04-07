import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


class TraktAPI:
    ROOT_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(ROOT_DIR / ".env")

    API_KEY = os.getenv("TRAKT_API_KEY")
    base_url = "https://api.trakt.tv"

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.API_KEY,
        }

    def fetch_movies(self, movie_title):
        """
        Searches Trakt trending and popular endpoints for a given movie title.
        Returns raw result data if found, otherwise None.
        """
        headers = self.get_headers()

        trending_url = f"{self.base_url}/movies/trending"
        response = requests.get(trending_url, headers=headers, params={"limit": 100}, timeout=20)

        if response.status_code != 200:
            print(f"API key test FAILED. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        movie_title_lower = movie_title.lower()
        for rank, entry in enumerate(response.json(), start=1):
            if entry["movie"]["title"].lower() == movie_title_lower:
                return self.parse_results(entry, movie_title, rank, source="trending")

        popular_url = f"{self.base_url}/movies/popular"
        response = requests.get(popular_url, headers=headers, params={"limit": 100}, timeout=20)

        if response.status_code != 200:
            print(f"API key test FAILED on popular endpoint. Status code: {response.status_code}")
            return None

        for rank, movie in enumerate(response.json(), start=1):
            if movie["title"].lower() == movie_title_lower:
                return self.parse_results({"movie": movie, "watchers": 0}, movie_title, rank, source="popular")

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
            "source": f"Trakt ({source})",
        }

    def rank_movies(self, movie_titles):
        """
        Takes a list of movie title strings, fetches stats for each from Trakt,
        ranks them by trending position and returns structured movie metadata.
        """
        headers = self.get_headers()
        limit = 100

        trending_map = {}
        response = requests.get(
            f"{self.base_url}/movies/trending",
            headers=headers,
            params={"limit": limit},
            timeout=20,
        )
        if response.status_code == 200:
            for rank, entry in enumerate(response.json(), start=1):
                title = entry.get("movie", {}).get("title", "")
                trending_map[title.lower()] = {
                    "trending_rank": rank,
                    "watchers": entry.get("watchers", 0),
                }

        popular_map = {}
        response = requests.get(
            f"{self.base_url}/movies/popular",
            headers=headers,
            params={"limit": limit},
            timeout=20,
        )
        if response.status_code == 200:
            for rank, movie in enumerate(response.json(), start=1):
                title = movie.get("title", "")
                popular_map[title.lower()] = rank

        def build_entry(title):
            title_lower = title.lower()
            entry = {"title": title}

            search_response = requests.get(
                f"{self.base_url}/search/movie",
                headers=headers,
                params={"query": title, "limit": 1},
                timeout=20,
            )
            if search_response.status_code == 200 and search_response.json():
                movie_data = search_response.json()[0].get("movie", {})
                ids = movie_data.get("ids", {})
                slug = ids.get("slug")
                entry["year"] = movie_data.get("year", "N/A")
                entry["trakt_id"] = ids.get("trakt", "N/A")
                entry["imdb_id"] = ids.get("imdb", "N/A")
                entry["tmdb_id"] = ids.get("tmdb", "N/A")

                if slug:
                    ratings_response = requests.get(
                        f"{self.base_url}/movies/{slug}/ratings",
                        headers=headers,
                        timeout=20,
                    )
                    if ratings_response.status_code == 200:
                        ratings_data = ratings_response.json()
                        entry["trakt_rating"] = round(ratings_data.get("rating", 0), 2)
                        entry["rating_votes"] = ratings_data.get("votes", 0)
                    else:
                        entry["trakt_rating"] = "N/A"
                        entry["rating_votes"] = "N/A"

                    stats_response = requests.get(
                        f"{self.base_url}/movies/{slug}/stats",
                        headers=headers,
                        timeout=20,
                    )
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        entry["total_plays"] = stats_data.get("plays", 0)
                        entry["total_watchers"] = stats_data.get("watchers", 0)
                        entry["collectors"] = stats_data.get("collectors", 0)
            else:
                entry["year"] = "N/A"
                entry["trakt_id"] = "N/A"
                entry["imdb_id"] = "N/A"
                entry["tmdb_id"] = "N/A"
                entry["trakt_rating"] = "N/A"
                entry["rating_votes"] = "N/A"

            trending_data = trending_map.get(title_lower, {})
            entry["trending_rank"] = trending_data.get("trending_rank", None)
            entry["watchers"] = trending_data.get("watchers", 0)
            entry["popularity_rank"] = popular_map.get(title_lower, None)
            entry.setdefault("total_plays", 0)
            entry.setdefault("total_watchers", 0)
            entry.setdefault("collectors", 0)
            return entry

        if movie_titles:
            with ThreadPoolExecutor(max_workers=min(8, len(movie_titles))) as executor:
                entries = list(executor.map(build_entry, movie_titles))
        else:
            entries = []

        ranked = []
        not_found = []
        for entry in entries:
            if entry["trending_rank"] is not None or entry["popularity_rank"] is not None:
                ranked.append(entry)
            else:
                not_found.append(entry)

        ranked.sort(
            key=lambda x: (
                x["trending_rank"] if x["trending_rank"] is not None else float("inf"),
                x["popularity_rank"] if x["popularity_rank"] is not None else float("inf"),
            )
        )
        return ranked + not_found

    def get_rating_fallbacks(self, movie_titles):
        """
        Fetch lightweight Trakt rating data for a batch of titles.
        Returns a lookup keyed by the requested title so callers can backfill
        missing score fields without paying for the heavier stats workflow.
        """
        headers = self.get_headers()

        def build_entry(title):
            entry = {
                "title": title,
                "trakt_rating": 0.0,
                "rating_votes": 0,
                "rt_like_score": 0,
                "metacritic_like_score": 0,
            }

            search_response = requests.get(
                f"{self.base_url}/search/movie",
                headers=headers,
                params={"query": title, "limit": 1},
                timeout=20,
            )
            if search_response.status_code != 200 or not search_response.json():
                return entry

            movie_data = search_response.json()[0].get("movie", {})
            slug = movie_data.get("ids", {}).get("slug")
            if not slug:
                return entry

            ratings_response = requests.get(
                f"{self.base_url}/movies/{slug}/ratings",
                headers=headers,
                timeout=20,
            )
            if ratings_response.status_code != 200:
                return entry

            ratings_data = ratings_response.json()
            trakt_rating = float(ratings_data.get("rating") or 0)
            rating_votes = int(ratings_data.get("votes") or 0)

            # Trakt gives us a 0-10 rating, so we derive percentage-style
            # fallback values for the score cards when OMDb is blank.
            scaled_score = max(0, min(100, round(trakt_rating * 10)))

            entry["trakt_rating"] = round(trakt_rating, 2)
            entry["rating_votes"] = rating_votes
            entry["rt_like_score"] = scaled_score
            entry["metacritic_like_score"] = scaled_score
            return entry

        if movie_titles:
            with ThreadPoolExecutor(max_workers=min(8, len(movie_titles))) as executor:
                entries = list(executor.map(build_entry, movie_titles))
        else:
            entries = []

        return {entry["title"]: entry for entry in entries}

    def fetch_category(self, category):
        """
        Fetches top movies for a given category and returns a list of movie entries
        with relevant stats depending on the category.
        """
        headers = self.get_headers()
        limit = 100
        period_categories = ["played", "watched", "collected"]
        params = {"limit": limit}

        if category in period_categories:
            url = f"{self.base_url}/movies/{category}/weekly"
        else:
            url = f"{self.base_url}/movies/{category}"

        response = requests.get(url, headers=headers, params=params, timeout=20)

        if response.status_code == 429:
            print("Rate limit hit. Please wait a moment and try again.")
            return None
        if response.status_code != 200:
            print(f"Failed to fetch {category}. Status code: {response.status_code}")
            return None

        data = response.json()
        movies = []

        for rank, entry in enumerate(data, start=1):
            if category == "trending":
                movie = entry.get("movie", {})
                stats = {"watchers_right_now": entry.get("watchers", "N/A")}
            elif category == "popular":
                movie = entry
                stats = {}
            elif category == "played":
                movie = entry.get("movie", {})
                stats = {
                    "play_count": entry.get("plays", "N/A"),
                    "unique_watchers": entry.get("watchers", "N/A"),
                }
            elif category == "watched":
                movie = entry.get("movie", {})
                stats = {
                    "unique_watchers": entry.get("watchers", "N/A"),
                    "play_count": entry.get("plays", "N/A"),
                }
            elif category == "collected":
                movie = entry.get("movie", {})
                stats = {
                    "collectors": entry.get("collectors", "N/A"),
                    "collect_count": entry.get("collects", "N/A"),
                }
            elif category == "anticipated":
                movie = entry.get("movie", {})
                stats = {"list_count": entry.get("list_count", "N/A")}
            else:
                movie = entry
                stats = {}

            movies.append(
                {
                    "rank": rank,
                    "title": movie.get("title", "Unknown"),
                    "year": movie.get("year", "N/A"),
                    "stats": stats,
                }
            )

        return movies

    def save_category_to_file(self, category, movies):
        """
        Saves or updates a category's movie list to a dedicated text file.
        Creates the file if it doesn't exist, overwrites it if it does.
        """
        output_folder = os.path.join(os.path.dirname(__file__), "Trakt_Movies_Lists")
        filename = os.path.join(output_folder, f"trakt_{category}.txt")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        stat_labels = {
            "trending": {"watchers_right_now": "Watchers Right Now"},
            "popular": {},
            "played": {"play_count": "Total Plays", "unique_watchers": "Unique Watchers"},
            "watched": {"unique_watchers": "Unique Watchers", "play_count": "Total Plays"},
            "collected": {"collectors": "Collectors", "collect_count": "Total Collects"},
            "anticipated": {"list_count": "Lists Featuring This Movie"},
        }

        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write(f"  Trakt Top {len(movies)} - {category.upper()} Movies\n")
            f.write(f"  Last Updated: {now}\n")
            f.write("=" * 60 + "\n\n")

            for movie in movies:
                f.write(f"#{movie['rank']:>3}. {movie['title']} ({movie['year']})\n")
                labels = stat_labels.get(category, {})
                for key, value in movie["stats"].items():
                    label = labels.get(key, key.replace("_", " ").title())
                    if isinstance(value, int):
                        f.write(f"       {label}: {value:,}\n")
                    else:
                        f.write(f"       {label}: {value}\n")
                f.write("\n")

        print(f"Saved to '{filename}' successfully!")
        return filename


def main():
    api = TraktAPI()

    categories = {
        "1": "trending",
        "2": "popular",
        "3": "played",
        "4": "watched",
        "5": "collected",
        "6": "anticipated",
    }

    print("=" * 50)
    print("       Trakt API Key Tester - FilmOnDemand")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("  1. Search for a movie")
        print("  2. Browse a category (saves to file)")
        print("  3. Rank a list of movies by trending")
        print("  4. Quit")

        choice = input("\nEnter choice (1/2/3/4): ").strip()

        if choice == "1":
            while True:
                movie_title = input("\nEnter a movie title (or 'back' to return): ").strip()

                if not movie_title:
                    print("   Please enter a valid movie title.")
                    continue

                if movie_title.lower() == "back":
                    break

                print(f"   Searching Trakt for '{movie_title}'...")
                result = api.fetch_movies(movie_title)

                if result is None:
                    print("Something went wrong. Check your API key and try again.")
                elif not result.get("found"):
                    print(f"API key works, but '{movie_title}' was not found in trending or popular lists.")
                    print("The movie may exist on Trakt but isn't currently trending/popular.")
                else:
                    print(f"API key works. Results for '{movie_title}':")
                    for key, value in result.items():
                        print(f"   {key}: {value}")

        elif choice == "2":
            print("\nChoose a category:")
            for num, cat in categories.items():
                print(f"  {num}. {cat.capitalize()}")

            cat_choice = input("\nEnter category number: ").strip()

            if cat_choice not in categories:
                print("   Invalid choice, please try again.")
                continue

            category = categories[cat_choice]
            print(f"\n   Fetching top 100 {category} movies from Trakt...")
            movies = api.fetch_category(category)

            if movies:
                print(f"\n   Top 5 {category.upper()} movies right now:")
                for movie in movies[:5]:
                    print(f"   #{movie['rank']}. {movie['title']} ({movie['year']})")

                api.save_category_to_file(category, movies)

        elif choice == "3":
            print("\nEnter movie titles one by one.")
            print("Press Enter with no input when done.\n")

            movie_list = []
            while True:
                title = input(f"  Movie {len(movie_list) + 1}: ").strip()
                if not title:
                    if len(movie_list) == 0:
                        print("  Please enter at least one movie.")
                        continue
                    break
                movie_list.append(title)

            print(f"\n   Ranking {len(movie_list)} movies by trending score...")
            results = api.rank_movies(movie_list)

            print(f"\n{'=' * 55}")
            print(f"  Ranked Results ({len(results)} movies)")
            print(f"{'=' * 55}")
            for i, movie in enumerate(results, start=1):
                print(f"\n  #{i}. {movie['title']} ({movie.get('year', 'N/A')})")
                print(f"      Trakt Rating       : {movie.get('trakt_rating', 'N/A')} ({movie.get('rating_votes', 'N/A')} votes)")
                print(f"      Trending Rank      : {'#' + str(movie['trending_rank']) if movie['trending_rank'] else 'Not trending'}")
                print(f"      Watchers Right Now : {movie.get('watchers', 0):,}")
                print(f"      Popularity Rank    : {'#' + str(movie['popularity_rank']) if movie['popularity_rank'] else 'Not in top 100'}")
                print(f"      Total Plays        : {movie.get('total_plays', 0):,}")
                print(f"      Total Watchers     : {movie.get('total_watchers', 0):,}")
                print(f"      Collectors         : {movie.get('collectors', 0):,}")
                print(f"      IMDb ID            : {movie.get('imdb_id', 'N/A')}")
                print(f"      TMDb ID            : {movie.get('tmdb_id', 'N/A')}")
            print(f"\n{'=' * 55}\n")

        elif choice == "4":
            print("Exiting. Goodbye!")
            break

        else:
            print("   Invalid choice, please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
