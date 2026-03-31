from WatchmodeAPI.main import WatchmodeAPI

from TraktAPI.main import TraktAPI
from TMDbAPI.tmdb import TMDbAPI
from TasteDiveAPI.main import TasteDiveAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()
        self.tmdb = TMDbAPI()
        self.trakt = TraktAPI()
        self.tastedive = TasteDiveAPI()

    def settings(self):
        return None

    def get_watchmode_movies(self):
        source_ids = self.watchmode.get_genre_or_source_ids(self.watchmode.source_data, ["netflix", "amazon"])
        sort_setting = (input("Sort by Genres or Actor?\n")).lower().strip()
        if sort_setting == "genre" or sort_setting == "genres":
            genre_ids = self.watchmode.get_genre_or_source_ids(self.watchmode.genre_data, ["romance","comedy"])
            data = self.watchmode.fetch_movies_by_genre(genre_ids, source_ids)
        elif sort_setting == "actor":
            actor_name = input("Enter Actor Name: ") # right now assuming name exists
            actor_id = self.watchmode.get_genre_or_source_ids(actor_name)
            data = self.watchmode.fetch_movies_by_actor(actor_id, source_ids)
        
        movies = self.watchmode.parse_results(data) # take the data and parse the results to top 10
        
        return movies

    def get_tastedive_movies(self):
        return self.tastedive.get_similar_movies()

    def get_movie_info(self):
        return None

    def get_movie_trailer(self):
        return None

if __name__ == "__main__":
    var = FilmOnDemand()
    
    # Take user input, decide on what settings they would like to set up:
    # --> if the user wants top 10 movies by genre, actor or movies similar to a movie provided
    # --> input what streaming services the user has access to
    # 
    # Use the get_?_movies() function for the specific setting