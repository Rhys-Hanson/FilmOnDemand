import requests
import os
from dotenv import load_dotenv
from datetime import datetime


class TraktAPI:
    load_dotenv()
    
    API_KEY = os.getenv("TRAKT_API_KEY")
    base_url = "https://api.trakt.tv"

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.API_KEY
        }

    def fetch_movies(self, movie_title):
        """
        Searches Trakt trending and popular endpoints for a given movie title.
        Returns raw result data if found, otherwise None.
        """
        headers = self.get_headers()

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

    def rank_movies(self, movie_titles):
        """
        Takes a list of movie title strings, fetches stats for each from Trakt,
        ranks them by trending position (movies not trending are ranked last by popularity),
        and returns an ordered list of dictionaries with relevant data.

        Each dictionary contains:
            - title                  : Movie title
            - year                   : Release year
            - trending_rank          : Rank in Trakt trending (None if not trending)
            - watchers               : Number of people watching right now (from trending)
            - popularity_rank        : Rank in Trakt all-time popular (None if not in top 100)
            - total_plays            : Total plays (all time, from /stats)
            - total_watchers         : Unique watchers (all time, from /stats)
            - collectors             : Number of users who collected the movie (from /stats)
            - trakt_rating           : Trakt community rating out of 10
            - rating_votes           : Number of votes for the rating
            - trakt_id               : Trakt internal ID (useful for other API calls)
            - imdb_id                : IMDb ID
            - tmdb_id                : TMDb ID

        Movies are sorted by trending_rank first (lower = better),
        then by popularity_rank for non-trending movies.
        Movies not found in either list are appended at the end.

        Usage example:
            api = TraktAPI()
            results = api.rank_movies(["Inception", "The Dark Knight", "Interstellar"])
            for movie in results:
                print(movie)
        """
        headers = self.get_headers()
        limit = 100

        # ── Step 1: Fetch all category lists once (avoid repeated API calls) ──

        # Trending: currently being watched right now
        trending_map = {}  # title.lower() -> {rank, watchers}
        r = requests.get(f"{self.base_url}/movies/trending", headers=headers, params={"limit": limit})
        if r.status_code == 200:
            for rank, entry in enumerate(r.json(), start=1):
                t = entry.get("movie", {}).get("title", "")
                trending_map[t.lower()] = {
                    "trending_rank": rank,
                    "watchers": entry.get("watchers", 0)
                }

        # Popular: all-time popularity ranking
        popular_map = {}  # title.lower() -> rank
        r = requests.get(f"{self.base_url}/movies/popular", headers=headers, params={"limit": limit})
        if r.status_code == 200:
            for rank, movie in enumerate(r.json(), start=1):
                t = movie.get("title", "")
                popular_map[t.lower()] = rank

        # (Per-movie stats are fetched individually via /movies/{slug}/stats below)

        # ── Step 2: For each movie, look up its slug and ratings ──
        ranked = []
        not_found = []

        for title in movie_titles:
            title_lower = title.lower()
            entry = {"title": title}

            # Search for the movie to get its slug and IDs
            r = requests.get(
                f"{self.base_url}/search/movie",
                headers=headers,
                params={"query": title, "limit": 1}
            )
            if r.status_code == 200 and r.json():
                movie_data = r.json()[0].get("movie", {})
                ids = movie_data.get("ids", {})
                slug = ids.get("slug")
                entry["year"]     = movie_data.get("year", "N/A")
                entry["trakt_id"] = ids.get("trakt", "N/A")
                entry["imdb_id"]  = ids.get("imdb", "N/A")
                entry["tmdb_id"]  = ids.get("tmdb", "N/A")

                # Fetch Trakt rating for this movie
                if slug:
                    r2 = requests.get(f"{self.base_url}/movies/{slug}/ratings", headers=headers)
                    if r2.status_code == 200:
                        rd = r2.json()
                        entry["trakt_rating"] = round(rd.get("rating", 0), 2)
                        entry["rating_votes"] = rd.get("votes", 0)
                    else:
                        entry["trakt_rating"] = "N/A"
                        entry["rating_votes"] = "N/A"

                    # Fetch per-movie stats (watchers, plays, collectors)
                    r3 = requests.get(f"{self.base_url}/movies/{slug}/stats", headers=headers)
                    if r3.status_code == 200:
                        sd = r3.json()
                        entry["total_plays"]    = sd.get("plays", 0)
                        entry["total_watchers"] = sd.get("watchers", 0)
                        entry["collectors"]     = sd.get("collectors", 0)
            else:
                entry["year"]         = "N/A"
                entry["trakt_id"]     = "N/A"
                entry["imdb_id"]      = "N/A"
                entry["tmdb_id"]      = "N/A"
                entry["trakt_rating"] = "N/A"
                entry["rating_votes"] = "N/A"

            # ── Step 3: Pull data from the pre-fetched category maps ──
            trending_data = trending_map.get(title_lower, {})

            entry["trending_rank"]   = trending_data.get("trending_rank", None)
            entry["watchers"]        = trending_data.get("watchers", 0)
            entry["popularity_rank"] = popular_map.get(title_lower, None)
            # Per-movie stats default to 0 if the slug lookup or /stats call failed
            entry.setdefault("total_plays", 0)
            entry.setdefault("total_watchers", 0)
            entry.setdefault("collectors", 0)

            # Separate found vs not found for sorting
            if entry["trending_rank"] is not None or entry["popularity_rank"] is not None:
                ranked.append(entry)
            else:
                not_found.append(entry)

        # ── Step 4: Sort by trending rank first, then popularity rank ──
        # Movies with no trending rank get sorted to the bottom of the trending group
        ranked.sort(key=lambda x: (
            x["trending_rank"] if x["trending_rank"] is not None else float("inf"),
            x["popularity_rank"] if x["popularity_rank"] is not None else float("inf")
        ))

        # Append movies not found in any list at the end
        return ranked + not_found

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
            # Period Options: weekly, monthly, yearly, all. Just change the weekly at the end here.
        else:
            url = f"{self.base_url}/movies/{category}"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            print("❌ Rate limit hit. Please wait a moment and try again.")
            return None
        elif response.status_code != 200:
            print(f"❌ Failed to fetch {category}. Status code: {response.status_code}")
            return None

        data = response.json()
        movies = []

        for rank, entry in enumerate(data, start=1):
            # Each category returns data in a slightly different structure
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

            movies.append({
                "rank": rank,
                "title": movie.get("title", "Unknown"),
                "year": movie.get("year", "N/A"),
                "stats": stats
            })

        return movies

    def save_category_to_file(self, category, movies):
        """
        Saves or updates a category's movie list to a dedicated text file.
        Creates the file if it doesn't exist, overwrites it if it does.
        """
        output_folder = os.path.join(os.path.dirname(__file__), "Trakt_Movies_Lists")
        filename = os.path.join(output_folder, f"trakt_{category}.txt")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Friendly stat labels per category
        stat_labels = {
            "trending":    {"watchers_right_now": "Watchers Right Now"},
            "popular":     {},
            "played":      {"play_count": "Total Plays", "unique_watchers": "Unique Watchers"},
            "watched":     {"unique_watchers": "Unique Watchers", "play_count": "Total Plays"},
            "collected":   {"collectors": "Collectors", "collect_count": "Total Collects"},
            "anticipated": {"list_count": "Lists Featuring This Movie"},
        }

        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write(f"  Trakt Top {len(movies)} — {category.upper()} Movies\n")
            f.write(f"  Last Updated: {now}\n")
            f.write("=" * 60 + "\n\n")

            for movie in movies:
                f.write(f"#{movie['rank']:>3}. {movie['title']} ({movie['year']})\n")
                labels = stat_labels.get(category, {})
                for key, value in movie["stats"].items():
                    label = labels.get(key, key.replace("_", " ").title())
                    f.write(f"       {label}: {value:,}\n" if isinstance(value, int) else f"       {label}: {value}\n")
                f.write("\n")

        print(f"✅ Saved to '{filename}' successfully!")
        return filename


def main():
    api = TraktAPI()

    categories = {
        "1": "trending",
        "2": "popular",
        "3": "played",
        "4": "watched",
        "5": "collected",
        "6": "anticipated"
    }

    print("=" * 50)
    print("       Trakt API Key Tester — FilmOnDemand")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("  1. Search for a movie")
        print("  2. Browse a category (saves to file)")
        print("  3. Rank a list of movies by trending")
        print("  4. Quit")

        choice = input("\nEnter choice (1/2/3/4): ").strip()

        # --- Option 1: Search for a movie ---
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
                    print("❌ Something went wrong. Check your API key and try again.")
                elif not result.get("found"):
                    print(f"✅ API key works! But '{movie_title}' was not found in trending or popular lists.")
                    print(f"   (The movie may exist on Trakt but isn't currently trending/popular)")
                else:
                    print(f"✅ API key works! Results for '{movie_title}':")
                    for key, value in result.items():
                        print(f"   {key}: {value}")

        # --- Option 2: Browse a category ---
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
                # Preview top 5 in terminal
                print(f"\n   Top 5 {category.upper()} movies right now:")
                for movie in movies[:5]:
                    print(f"   #{movie['rank']}. {movie['title']} ({movie['year']})")

                # Save full list to file
                api.save_category_to_file(category, movies)

        # --- Option 3: Rank a list of movies ---
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
            print(f"  📊 Ranked Results ({len(results)} movies)")
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

        # --- Option 4: Quit ---
        elif choice == "4":
            print("Exiting. Goodbye!")
            break

        else:
            print("   Invalid choice, please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()