import pytest

#dummy function to test without calling API
def searchMovie(title_obj):
    return [title_obj]

#Code being tested
class MovieInfo:
    def movie_info(self, title):
        possibleMovies = searchMovie (title) #searches for the movie title and returns a list of movies with similar titles

        if len(possibleMovies) == 0:
            print("No description found")

        title = possibleMovies[0] #takes the first movie from the list of possible ones, which is the most likely match
        print("Title: " + title.title)
        print("Release Date: " + str(title.releasedate))
        print("Overview: " + title.overview)
        print("Genres: " + ", ".join(g.name for g in title.genres))
        print("Cast: " + ", ".join(c.name for c in title.cast[:3]) + "...") #prints the top 3 main cast members
        
        directors = [person.name for person in title.crew if person.job == 'Director']
        director_name = ", ".join(directors) if directors else "Unknown"
        print("Director: " + director_name)

        print("Studio: " + title.studios[0].name)
        print("Trailer: " + title.youtube_trailers[0].geturl())
        print("\n---------\n")

class FakeStudio:
    def __init__(self, name):
        self.name = name

# A fake 'Movie' object that has all the attributes your code calls
class FakeMovie:
    def __init__(self, title, studios=None, trailers=None):
        self.title = title
        self.releasedate = "2026-01-01"
        self.overview = "A test movie overview"
        self.genres = []
        self.cast = []
        self.crew = []
        # If no list is provided, we use an empty list to trigger the bug
        self.studios = studios if studios is not None else []
        self.youtube_trailers = trailers if trailers is not None else []

# --- THE TEST SUITE ---
class TestTMDbIntegration:

    def test_movie_info_empty_studios_reveal_bug(self):
        """
        Input: A movie object with an EMPTY studios list.
        Expected: The code should return 'Unknown' instead of crashing.
        """
        # 1. Input
        bad_movie = FakeMovie(title="Ghost Movie", studios=[])
        app = MovieInfo() 
        
        # 2. Actual
        actual_studio = app.movie_info(bad_movie)
            
            # 3. Assert
        assert actual_studio == "Unknown"

    def test_movie_info_with_valid_studio(self):
        """
        Input: A movie object with a valid studio.
        Expected: Return 'Universal'.
        """
        # 1. Input
        good_studio = FakeStudio("Universal")
        good_movie = FakeMovie(title="Blockbuster", studios=[good_studio])
        app = MovieInfo()

        # 2. Actual
        actual_studio = app.movie_info(good_movie)
            
        # 3. Assert
        assert actual_studio == "Universal"
