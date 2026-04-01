from tmdb3 import searchMovie, set_key #import the python wrapper for the TMDb API


class TMDbAPI:
    def __init__(self):
        set_key('API_KEY_HERE') #put API key here
        
#from TasteDive API, it will gather a list of movies similar to the title the user inputs
#list will be sent here to be processed and filtered for movies of the rating range and genre
    def quality_check(self, TDmovies, required_genre, min_rating):
        filteredMovies = []
        for TDmovie in TDmovies: ##for each movie from the list of similar movies from TasteDive
            filmList = searchMovie(TDmovie) #creates another list of similar movies for each movie from original list
            for film in filmList: #takes each movie from the new list
                if film.title and film.title.lower() == TDmovie.lower(): #matches the title of the movie from both lists
                    if film.genres != None and required_genre in [g.name for g in film.genres]: #checks if genre inputted matches one of the genres of the movie
                        if film.userrating != None and min_rating <= film.userrating: #checks if the user rating is in the range inputted
                            filteredMovies.append(TDmovie) #passed all filters so it is added to a new filtered list of movies
                            break
        return filteredMovies

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