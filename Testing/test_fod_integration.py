import json

from FilmOnDemand.main import FilmOnDemand


def test_settings_selects_watchmode_path():
    engine = FilmOnDemand()
    engine.settings(
        json.dumps(
            {
                "filters": {
                    "genres": ["Action"],
                    "services": ["Netflix"],
                    "actors": ["Tom Cruise"],
                    "movies": [],
                    "offset": 10,
                }
            }
        )
    )
    assert engine.fetch_type == "watchmode"
    assert engine.genres == ["Action"]
    assert engine.sources == ["Netflix"]
    assert engine.actor == "Tom Cruise"
    assert engine.offset == 10


def test_get_movies_returns_empty_when_actor_cannot_be_mapped():
    engine = FilmOnDemand()
    engine.fetch_type = "watchmode"
    engine.sources = ["Netflix"]
    engine.genres = ["Action"]
    engine.actor = "Missing Actor"
    engine.watchmode = type(
        "WatchmodeStub",
        (),
        {
            "get_source_ids": lambda self, sources: [203],
            "get_genre_ids": lambda self, genres: [1],
            "get_actor_id": lambda self, actor: None,
        },
    )()
    result = engine.get_movies()
    assert result is None
    assert engine.movies_and_ids == {}


def test_get_movies_filters_similar_movies_by_selected_sources():
    engine = FilmOnDemand()
    engine.fetch_type = "similar_movies"
    engine.sources = ["Netflix"]
    engine.similar_movies = ["Inception"]
    engine.tastedive = type("TasteDiveStub", (), {"run": lambda self, query: ["Movie A", "Movie B"]})()
    engine.watchmode = type(
        "WatchmodeStub",
        (),
        {
            "get_source_ids": lambda self, sources: [203],
            "get_watchmode_movie_info": lambda self, title: {
                "Movie A": {"tmdb_id": 1, "sources": [203]},
                "Movie B": {"tmdb_id": 2, "sources": [387]},
            }[title],
        },
    )()
    engine.get_movies()
    assert engine.movies_and_ids == {"Movie A": 1}


def test_get_movie_info_enriches_tmdb_with_omdb_trakt_and_streaming():
    engine = FilmOnDemand()
    engine.movies_and_ids = {"Inception": 27205}
    engine.tmdb = type(
        "TMDbStub",
        (),
        {
            "movie_info": lambda self, title: {
                "title": title,
                "description": "Dreams within dreams",
                "posterUrl": "poster.jpg",
                "year": 2010,
                "youtubeId": "abc123",
                "runtime": "2h 28m",
                "maturityRating": "PG-13",
                "castList": [],
                "genres": ["Sci-Fi"],
                "director": "Christopher Nolan",
                "studio": "Warner Bros.",
            }
        },
    )()
    engine.omdb = type(
        "OMDbStub",
        (),
        {
            "enrich": lambda self, title, year=None: {
                "imdbScore": 8.8,
                "imdbVotes": "2,793,322",
                "rtScore": 87.0,
                "metacriticScore": 74.0,
                "writer": "Christopher Nolan",
                "language": "English",
                "country": "United States",
                "awards": "Won 4 Oscars",
                "boxOffice": "$292,587,330",
            }
        },
    )()
    engine.trakt = type(
        "TraktStub",
        (),
        {
            "get_rating_fallbacks": lambda self, titles: {
                "Inception": {"trakt_rating": 8.7, "rating_votes": 1234}
            }
        },
    )()
    engine._fetch_streaming_services = lambda title: ["Netflix", "Prime Video"]
    engine.get_movie_info()
    assert len(engine.movies_with_desc) == 1
    movie = engine.movies_with_desc[0]
    assert movie["id"] == "27205"
    assert movie["streamingServices"] == ["Netflix", "Prime Video"]
    assert movie["imdbScore"] == 8.8
    assert movie["traktRating"] == 8.7
    assert movie["writer"] == "Christopher Nolan"


def test_run_movie_pull_uses_ai_prompt(monkeypatch):
    engine = FilmOnDemand()
    captured = {}

    def fake_get_movie_info():
        engine.movies_with_desc = [{"title": "Inception"}]
        captured["called"] = True

    monkeypatch.setattr("server.ai_service.generate_movie_recommendations", lambda prompt, services: ["Inception"])
    monkeypatch.setattr(engine, "get_movie_info", fake_get_movie_info)
    result = engine.run_movie_pull(
        json.dumps(
            {
                "filters": {
                    "services": ["Netflix"],
                    "ai_prompt": "mind-bending sci-fi",
                }
            }
        )
    )
    assert captured["called"] is True
    assert engine.movies_and_ids == {"Inception": ""}
    assert result == [{"title": "Inception"}]
