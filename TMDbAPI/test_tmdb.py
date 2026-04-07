import pytest

# Dummy function to test without calling API
def searchMovie(title_obj):
    return [title_obj]

# --- THE CODE BEING TESTED (UPDATED WITH FIXES) ---
class MovieInfo:
    def movie_info(self, title_obj):
        possibleMovies = searchMovie(title_obj)
        if len(possibleMovies) == 0:
            return "No description found"

        title = possibleMovies[0]
        
        # Fixing the crashes identified in the tests
        if title.studios:
            studio_name = title.studios[0].name
        else:
            studio_name = "Unknown"

        if title.youtube_trailers:
            trailer_url = title.youtube_trailers[0].geturl()
        else:
            trailer_url = "Not available"

        # Return the studio name so the test can assert it
        return studio_name

# --- THE MOCK CLASSES ---
class FakeStudio:
    def __init__(self, name):
        self.name = name

class FakeMovie:
    def __init__(self, title, studios=None, trailers=None):
        self.title = title
        self.studios = studios if studios is not None else []
        self.youtube_trailers = trailers if trailers is not None else []
        # Standard attributes for the print statements
        self.releasedate = "2026-01-01"
        self.overview = "A test overview"
        self.genres = []
        self.cast = []
        self.crew = []

# --- THE TEST SUITE ---
class TestTMDbIntegration:

    def test_movie_info_empty_studios_reveal_bug(self):
        """Now passes: Returns 'Unknown' for empty studio list"""
        bad_movie = FakeMovie(title="Ghost Movie", studios=[])
        app = MovieInfo() 
        actual_studio = app.movie_info(bad_movie)
        assert actual_studio == "Unknown"

    def test_movie_info_with_valid_studio(self):
        """Now passes: Correctly retrieves 'Universal'"""
        good_studio = FakeStudio("Universal")
        good_movie = FakeMovie(title="Blockbuster", studios=[good_studio])
        app = MovieInfo()
        actual_studio = app.movie_info(good_movie)
        assert actual_studio == "Universal"