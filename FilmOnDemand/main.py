from WatchmodeAPI import WatchmodeAPI


class FilmOnDemand:
    def __init__(self):
        self.watchmode = WatchmodeAPI()

    def settings(self):
        return None

    def get_watchmode_movies(self):
        source_ids = self.watchmode.get_source_ids(["netflix", "amazon"])
        sort_setting = input("Sort by Genres or Actor/Actress?\n").lower().strip()

        if sort_setting == "genre" or sort_setting == "genres":
            genre_ids = self.watchmode.get_genre_ids(["romance", "comedy"])
            data = self.watchmode.fetch_movies_by_genre(genre_ids, source_ids)

        elif sort_setting == "actor" or sort_setting == "actress":
            actor_name = input("Enter Actor Name: ").lower().strip()
            actor_id = self.watchmode.get_actor_id(actor_name)
            print("actor_id: ")
            print(actor_id)
            
            if actor_id is None:
                print("Actor not found.")
                return []

            data = self.watchmode.fetch_movies_by_actor(actor_id, source_ids)

        else:
            print("Invalid option.")
            return []

        movies = self.watchmode.parse_results(data)
        print(movies)
        return movies

    def get_tastedive_movies(self):
        # something like return self.tastedive.get_similar_movies()
        return None

    def get_movie_info(self):
        return None

    def get_movie_trailer(self):
        return None

if __name__ == "__main__":
    var = FilmOnDemand()
    var.get_watchmode_movies()
    # Take user input, decide on what settings they would like to set up:
    # --> if the user wants top 10 movies by genre, actor or movies similar to a movie provided
    # --> input what streaming services the user has access to
    # 
    # Use the get_?_movies() function for the specific setting