from WatchmodeAPI import WatchmodeAPI
from TraktAPI import TraktAPI
from TMDbAPI import TMDbAPI
from TasteDiveAPI import TasteDiveAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.trakt = TraktAPI()
        self.tmdb = TMDbAPI()
        self.tastedive = TasteDiveAPI()

    def settings(self, fetch_type, sources=None):
        self.sources = sources
        self.fetch_type = fetch_type
        return None

    def get_movies(self):        
        
        # From Watchmode API
        if self.fetch_type in ["actor", "actors", "actress", "actresses"]:
            actor_name = input("Actor Name: ")
            movies = self.watchmode.run_for_actors(actor_name,   self.sources)
            return movies
        elif self.fetch_type in ["genre", "genres"]:
            genres = []
            user_input = input("Enter Genres: (Press Enter to Stop Adding Genres)\n>>> ")
            while user_input != "":
                genres.append(user_input)
                user_input = input(">>> ")
            movies = self.watchmode.run_for_genres(genres, self.sources)
            return movies
        
        # From TasteDive API
        elif self.fetch_type in ["similar movies", "similarmovies"]:
            seed_movies = []
            user_input = input("Enter Movies for Similarity: (Press Enter to Leave)\n>>> ").strip()

            while user_input != "":
                seed_movies.append(user_input)
                user_input = input(">>> ").strip()

            if not seed_movies:
                print("No movies entered.")
                return []

            movies = self.tastedive.run(",".join(seed_movies))
            return movies
        
        # CURRENTLY RETURNS 20 MOVIES IN A LIST
        # Implement TMDb to ensure it only displays movies 


    def get_movie_info(self, movies):
        print("\n--- Fetching TMDb Details ---")
        movie_info = {movie : self.tmdb.movie_info(movie) for movie in movies}
        #
        #
        #Append trakt movie info tho this dictionary SAMUEL
        #
        #
        return movie_info


if __name__ == "__main__":
    films = FilmOnDemand()
    sources = []
    user_input = input("Enter Streaming Service(s): >>Press \"Enter\" to Leave<<\n>>> ").lower().strip()
    while user_input != "":
        sources.append(user_input)
        user_input = input(">>> ").lower().strip()
    

    fetch_type = input("Recommend by: \"Genre\", \"Actor/Actress\", \"Similar Movies\":\n>>>").lower().strip()
    while fetch_type not in ["genre", "genres", "actor", "actors", "actress", "actresses", "similar movies", "similarmovies"]:
        fetch_type = input("Unrecognized Answer!\n>>> ").lower().strip()
    
    films.settings(fetch_type, sources)
    
    movies = films.get_movies()
    movies_with_desc = films.get_movie_info(movies)

    # Take user input, decide on what settings they would like to set up:
    # --> if the user wants top 10 movies by genre, actor or movies similar to a movie provided
    # --> input what streaming services the user has access to
    # 
    # Use the get_?_movies() function for the specific setting