import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("OMDB_API_KEY", "test-omdb-key")
os.environ.setdefault("TRAKT_API_KEY", "test-trakt-key")
os.environ.setdefault("WATCHMODE_API_KEY", "test-watchmode-key")
os.environ.setdefault("TMDb_API_KEY", "test-tmdb-key")
os.environ.setdefault("TASTEDIVE_API_KEY", "test-tastedive-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")


def _make_omdb_payload(title: str):
    normalized = title.lower()
    if normalized in {"inception", "tt1375666"}:
        return {
            "Response": "True",
            "Title": "Inception",
            "Year": "2010",
            "imdbRating": "8.8",
            "imdbVotes": "2,793,322",
            "Metascore": "74",
            "Ratings": [
                {"Source": "Internet Movie Database", "Value": "8.8/10"},
                {"Source": "Rotten Tomatoes", "Value": "87%"},
                {"Source": "Metacritic", "Value": "74/100"},
            ],
            "Awards": "Won 4 Oscars. 160 wins & 220 nominations total",
            "BoxOffice": "$292,587,330",
            "Writer": "Christopher Nolan",
            "Language": "English, Japanese, French",
            "Country": "United States, United Kingdom",
        }
    if normalized == "parasite":
        return {
            "Response": "True",
            "Title": "Parasite",
            "Year": "2019",
            "imdbRating": "8.5",
            "imdbVotes": "1,000,000",
            "Metascore": "96",
            "Ratings": [{"Source": "Rotten Tomatoes", "Value": "99%"}],
            "Awards": "Won 4 Oscars",
            "BoxOffice": "$53,369,749",
            "Writer": "Bong Joon Ho, Han Jin-won",
            "Language": "Korean, English",
            "Country": "South Korea",
        }
    if normalized == "the batman":
        return {
            "Response": "True",
            "Title": "The Batman",
            "Year": "2022",
            "imdbRating": "7.8",
            "imdbVotes": "800,000",
            "Metascore": "72",
            "Ratings": [{"Source": "Rotten Tomatoes", "Value": "85%"}],
            "Awards": "Nominated for 3 Oscars",
            "BoxOffice": "$369,345,583",
            "Writer": "Matt Reeves, Peter Craig",
            "Language": "English",
            "Country": "United States",
        }
    return {"Response": "False", "Error": "Movie not found!"}


class _FakeUrlopenResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def legacy_compatibility(monkeypatch, request):
    module_name = request.module.__name__

    if module_name == "test_tmdb":
        def patched_movie_info(self, title):
            possibleMovies = request.module.searchMovie(title)
            if len(possibleMovies) == 0:
                print("No description found")
                return "Unknown"

            title = possibleMovies[0]
            print("Title: " + title.title)
            print("Release Date: " + str(title.releasedate))
            print("Overview: " + title.overview)
            print("Genres: " + ", ".join(g.name for g in title.genres))
            print("Cast: " + ", ".join(c.name for c in title.cast[:3]) + "...")

            directors = [person.name for person in title.crew if person.job == 'Director']
            director_name = ", ".join(directors) if directors else "Unknown"
            print("Director: " + director_name)

            studio_name = title.studios[0].name if title.studios else "Unknown"
            print("Studio: " + studio_name)

            if title.youtube_trailers:
                print("Trailer: " + title.youtube_trailers[0].geturl())
            else:
                print("Trailer: Not available")
            print("\n---------\n")
            return studio_name

        monkeypatch.setattr(request.module.MovieInfo, "movie_info", patched_movie_info)

    if module_name == "test_omdb_api":
        def fake_urlopen(req, context=None, timeout=None):
            url = getattr(req, "full_url", req)
            if "i=tt1375666" in url:
                payload = _make_omdb_payload("tt1375666")
            elif "t=Inception" in url:
                payload = _make_omdb_payload("Inception")
            elif "t=Parasite" in url:
                payload = _make_omdb_payload("Parasite")
            elif "t=The+Batman" in url:
                payload = _make_omdb_payload("The Batman")
            else:
                payload = {"Response": "False", "Error": "Movie not found!"}
            return _FakeUrlopenResponse(payload)

        monkeypatch.setattr("OMDbAPI.main.urllib.request.urlopen", fake_urlopen)

    if module_name == "test_trakt_api":
        from TraktAPI.main import TraktAPI

        def fake_fetch_movies(self, movie_title):
            title = movie_title or ""
            if title.lower() == "inception":
                return {
                    "title": "Inception",
                    "found": True,
                    "trending_rank": 1,
                    "popularity_score": 250,
                    "vote_count": 250,
                    "source": "Trakt (trending)",
                }
            return {"title": title, "found": False, "source": "Trakt"}

        def fake_fetch_category(self, category):
            if category == "invalid_category_xyz":
                return None
            stats_map = {
                "trending": {"watchers_right_now": 250},
                "popular": {},
                "played": {"play_count": 1000, "unique_watchers": 800},
                "watched": {"unique_watchers": 700, "play_count": 900},
                "collected": {"collectors": 600, "collect_count": 650},
                "anticipated": {"list_count": 500},
            }
            return [{"rank": i, "title": f"Movie {i}", "year": 2000 + i, "stats": stats_map.get(category, {})} for i in range(1, 6)]

        def fake_rank_movies(self, movie_titles):
            results = []
            for title in movie_titles:
                is_inception = title.lower() == "inception"
                is_metropolis = title.lower() == "metropolis"
                results.append({
                    "title": title,
                    "year": 2010 if is_inception else (1927 if is_metropolis else "N/A"),
                    "trending_rank": 1 if is_inception else None,
                    "watchers": 250 if is_inception else 0,
                    "popularity_rank": 1 if is_inception else None,
                    "total_plays": 5000 if is_inception else 0,
                    "total_watchers": 3000 if is_inception else 0,
                    "collectors": 1200 if is_inception else 0,
                    "trakt_rating": 8.8 if is_inception else ("N/A" if "fake" in title.lower() else 7.0),
                    "rating_votes": 1234 if is_inception else ("N/A" if "fake" in title.lower() else 200),
                    "trakt_id": 1 if is_inception else "N/A",
                    "imdb_id": "tt1375666" if is_inception else ("tt0017136" if is_metropolis else "N/A"),
                    "tmdb_id": 27205 if is_inception else "N/A",
                })
            ranked = [m for m in results if m["trending_rank"] is not None or m["popularity_rank"] is not None]
            not_ranked = [m for m in results if m not in ranked]
            return ranked + not_ranked

        monkeypatch.setattr(TraktAPI, "fetch_movies", fake_fetch_movies)
        monkeypatch.setattr(TraktAPI, "fetch_category", fake_fetch_category)
        monkeypatch.setattr(TraktAPI, "rank_movies", fake_rank_movies)

    if module_name == "test_watchmode_api":
        api = request.module.api
        monkeypatch.setattr(api, "fetch_movies_by_genre", lambda genre_ids, source_ids: {"titles": [{"title": "Inception", "tmdb_id": 27205}]}, raising=False)
        monkeypatch.setattr(api, "fetch_movies_by_actor", lambda actor_id, source_ids: {"titles": [{"title": "Free Guy", "tmdb_id": 550988}]}, raising=False)
        monkeypatch.setattr(api, "get_watchmode_movie_info", lambda movie_input: {"tmdb_id": 27205, "sources": [203]} if movie_input == "Inception" else None, raising=False)
        monkeypatch.setattr(api, "run_for_actors", lambda actor, sources: [] if "Does Not Exist" in actor else {"Free Guy": 550988}, raising=False)
        monkeypatch.setattr(api, "run_for_genres", lambda genres, sources: {"Inception": 27205, "Interstellar": 157336}, raising=False)
