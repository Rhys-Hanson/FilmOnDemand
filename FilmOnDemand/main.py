from WatchmodeAPI import WatchmodeAPI
from TraktAPI import TraktAPI
from TMDbAPI import TMDbAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.trakt = TraktAPI()
        self.tmdb = TMDbAPI()

    def settings(self):
        return None

    def get_watchmode_movies(self, sort_setting):        
        if sort_setting not in ["genre", "genres", "actor", "actress"]:
            print("Invalid option.")
            return []
        
        sources = []
        user_input = input("Enter Streaming Service(s): >>Press \"Enter\" to Leave<<\n>>> ").lower().strip()
        while True:
            if user_input == "": 
                break
            else: 
                sources.append(user_input)
            user_input = input(">>> ").lower().strip()
        source_ids = self.watchmode.get_source_ids(sources)

        if sort_setting == "genre" or sort_setting == "genres":
            genres = []
            user_input = input("Enter Genre(s): >>Press \"Enter\" to Leave<<\n>>> ").lower().strip()
            while True:
                if user_input == "": 
                    break
                else: 
                    genres.append(user_input)
                user_input = input(">>> ").lower().strip()
            genre_ids = self.watchmode.get_genre_ids(genres)
            data = self.watchmode.fetch_movies_by_genre(genre_ids, source_ids)

        elif sort_setting == "actor" or sort_setting == "actress":
            actor_name = input("Enter Actor Name: ").lower().strip()
            actor_id = self.watchmode.get_actor_id(actor_name)
            
            if actor_id is None:
                print("Actor not found.")
                return []

            data = self.watchmode.fetch_movies_by_actor(actor_id, source_ids)

        movies = self.watchmode.parse_results(data)
        return movies

    def get_tastedive_movies(self):
        # something like return self.tastedive.get_similar_movies()
        return None

    def get_movie_info(self, movies):
        print("\n--- Fetching TMDb Details ---")
        movie_info = {movie : self.tmdb.movie_info(movie) for movie in movies}

        # Fetch Trakt stats for all movies in one batch
        print("\n--- Fetching Trakt Details ---")
        trakt_results = self.trakt.rank_movies(movies)

        # Build a lookup by title so we can match results back
        trakt_lookup = {entry["title"]: entry for entry in trakt_results}

        for movie in movies:
            trakt_data = trakt_lookup.get(movie, {})
            movie_info[movie]["trending_rank"] = trakt_data.get("trending_rank", None)
            movie_info[movie]["watchers"] = trakt_data.get("watchers", 0)
            movie_info[movie]["popularity_rank"] = trakt_data.get("popularity_rank", None)
            movie_info[movie]["plays_weekly"] = trakt_data.get("plays_weekly", 0)
            movie_info[movie]["unique_watchers_weekly"] = trakt_data.get("unique_watchers_weekly", 0)
            movie_info[movie]["collectors"] = trakt_data.get("collectors", 0)
            movie_info[movie]["collect_count"] = trakt_data.get("collect_count", 0)
            movie_info[movie]["trakt_rating"] = trakt_data.get("trakt_rating", "N/A")
            movie_info[movie]["rating_votes"] = trakt_data.get("rating_votes", "N/A")

        return movie_info


if __name__ == "__main__":
    var = FilmOnDemand()
    sort_setting = input("Sort by Genres or Actor/Actress?\n>>>").lower().strip()
    movies = var.get_watchmode_movies(sort_setting)
    movies_with_desc = var.get_movie_info(movies)

    # Take user input, decide on what settings they would like to set up:
    # --> if the user wants top 10 movies by genre, actor or movies similar to a movie provided
    # --> input what streaming services the user has access to
    # 
    # Use the get_?_movies() function for the specific setting