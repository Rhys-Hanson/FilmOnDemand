from tmdb3 import searchMovie, set_key, set_cache, Movie #import the python wrapper for the TMDb API
import os
from dotenv import load_dotenv

class TMDbAPI:
    def __init__(self):
        load_dotenv()
        
        self.API_KEY = os.getenv("TMDb_API_KEY")
        
        if not self.API_KEY:
            raise ValueError("TMDb_API_KEY is missing. Check your .env file.")
            
        set_key(self.API_KEY) 
        
        set_cache("null")
        

    def movie_info(self, title):
        possibleMovies = searchMovie(title)

        if len(possibleMovies) == 0: #boundary chcek
            return {"error": "No movie found"}

        # Take the first movie from the list of possible ones
        movie = possibleMovies[0] 

        # Poster URL
        posterUrl = None
        if movie.poster:
            try:
                posterUrl = movie.poster.geturl('w500') #try to get medium sized poster first
            except:
                posterUrl = movie.poster.geturl('original')

        # Year
        year = None
        if movie.releasedate: #boundary check
            year = movie.releasedate.year # gets yrea datetime object

        # YouTube ID
        youtubeId = None
        if movie.youtube_trailers: #boundary check
            url = movie.youtube_trailers[0].geturl()
            if 'v=' in url:
                youtubeId = url.split('v=')[-1] #to extrcat the video ID

        # Runtime
        runtime_str = "Unknown"
        if movie.runtime:#gives runtmie in integer value (so prolly minutes)
            hours = movie.runtime // 60
            minutes = movie.runtime % 60
            runtime_str = f"{hours}h {minutes}m"

        # Maturity Rating
        maturityRating = "Unrated"
        if movie.releases and 'US' in movie.releases:
            maturityRating = movie.releases['US'].certification or "Unrated"

        # Cast List (Top 4)
        castList = []
        if movie.cast:
            for actor in movie.cast[:4]:
                imageUrl = None
                if actor.profile:
                    try:
                        imageUrl = actor.profile.geturl('w185')
                    except:
                        imageUrl = actor.profile.geturl('original')
                
                castList.append({
                    "name": actor.name,
                    "character": actor.character,
                    "imageUrl": imageUrl
                })

        # Genres
        genres = []
        if movie.genres:
            genres = [g.name for g in movie.genres]

        # Director 
        director = "Unknown"
        if movie.crew:
            directors = [person.name for person in movie.crew if person.job == 'Director']
            if directors:
                director = ", ".join(directors)

        # Studio
        studio = "Unknown"
        if movie.studios:
            studio = movie.studios[0].name

        # Return the Dictionary
        return {
            "title": movie.title,
            "description": movie.overview,
            "posterUrl": posterUrl,
            "year": year,
            "youtubeId": youtubeId,
            "runtime": runtime_str,
            "maturityRating": maturityRating,
            "castList": castList,
            "genres": genres,        
            "director": director,    
            "studio": studio
        }