import json
from FilmOnDemand.main import FilmOnDemand

engine = FilmOnDemand()
settings = json.dumps({
    "action": "start_game",
    "filters": {
        "genres": ["Horror", "Action"],
        "services": ["Netflix"],
        "actors": ["tom cruise"],
        "yearRange": [1990, 2024],
        "similarMovies": []
    }
})
print("Starting pull...")
try:
    deck = engine.run_movie_pull(settings)
    print("Deck length:", len(deck) if deck else deck)
    print(deck)
except Exception as e:
    import traceback
    traceback.print_exc()
