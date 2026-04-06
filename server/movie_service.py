import json
import logging
import os
from contextlib import contextmanager
from typing import Any

from FilmOnDemand.main import FilmOnDemand


logger = logging.getLogger(__name__)


@contextmanager
def _direct_network_env():
    proxy_keys = (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "all_proxy",
        "ALL_PROXY",
    )
    original = {key: os.environ.get(key) for key in proxy_keys}
    original_no_proxy = os.environ.get("NO_PROXY")

    try:
        for key in proxy_keys:
            os.environ.pop(key, None)
        os.environ["NO_PROXY"] = "*"
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        if original_no_proxy is None:
            os.environ.pop("NO_PROXY", None)
        else:
            os.environ["NO_PROXY"] = original_no_proxy


def normalize_movie_payload(filters: dict[str, Any], raw_movies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_movies: list[dict[str, Any]] = []
    requested_services = filters.get("services", [])

    for index, movie in enumerate(raw_movies, start=1):
        cast_list = movie.get("castList") or []
        cast_names = [person.get("name", "") for person in cast_list if person.get("name")]

        trakt_rating = movie.get("trakt_rating")
        imdb_score = trakt_rating if isinstance(trakt_rating, (int, float)) else 0

        normalized_movies.append(
            {
                "id": str(movie.get("id") or index),
                "title": movie.get("title", "Unknown Title"),
                "posterUrl": movie.get("posterUrl") or "",
                "description": movie.get("description") or "No description available.",
                "cast": cast_names,
                "castList": cast_list,
                "rtScore": 0,
                "imdbScore": imdb_score,
                "metacriticScore": 0,
                "summary": movie.get("description") or "No summary available.",
                "genre": movie.get("genres") or [],
                "year": movie.get("year"),
                "youtubeId": movie.get("youtubeId") or "",
                "maturityRating": movie.get("maturityRating") or "Unrated",
                "runtime": movie.get("runtime") or "Unknown",
                "streamingServices": requested_services,
            }
        )

    return normalized_movies


def build_deck(filters: dict[str, Any]) -> list[dict[str, Any]]:
    payload = {"action": "start_game", "filters": filters}

    try:
        with _direct_network_env():
            engine = FilmOnDemand()
            raw_movies = engine.run_movie_pull(json.dumps(payload))
    except Exception:
        logger.exception("FilmOnDemand movie pull failed")
        raise

    if not isinstance(raw_movies, list):
        raise ValueError("FilmOnDemand returned an unexpected response")

    return normalize_movie_payload(filters, raw_movies)
