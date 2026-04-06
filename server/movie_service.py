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

        # Prefer real OMDb/IMDb score over the Trakt mislabel
        imdb_score = movie.get("imdbScore") or movie.get("imdb_rating") or 0
        if not isinstance(imdb_score, (int, float)):
            try:
                imdb_score = float(imdb_score)
            except (TypeError, ValueError):
                imdb_score = 0

        rt_score = movie.get("rtScore") or movie.get("rt_score") or 0
        metacritic_score = movie.get("metacriticScore") or movie.get("metascore") or 0

        normalized_movies.append(
            {
                "id": str(movie.get("id") or index),
                "title": movie.get("title", "Unknown Title"),
                "posterUrl": movie.get("posterUrl") or "",
                "description": movie.get("description") or "No description available.",
                "cast": cast_names,
                "castList": cast_list,
                "rtScore": rt_score,
                "imdbScore": imdb_score,
                "metacriticScore": metacritic_score,
                "imdbVotes": movie.get("imdbVotes") or movie.get("imdb_votes") or None,
                "summary": movie.get("description") or "No summary available.",
                "genre": movie.get("genres") or [],
                "year": movie.get("year"),
                "youtubeId": movie.get("youtubeId") or "",
                "maturityRating": movie.get("maturityRating") or "Unrated",
                "runtime": movie.get("runtime") or "Unknown",
                "streamingServices": movie.get("streamingServices") or requested_services,
                # OMDb enrichment fields
                "director": movie.get("director") or None,
                "writer": movie.get("writer") or None,
                "language": movie.get("language") or None,
                "country": movie.get("country") or None,
                "awards": movie.get("awards") or None,
                "boxOffice": movie.get("boxOffice") or movie.get("box_office") or None,
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
