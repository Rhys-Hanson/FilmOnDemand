import json
import os
from functools import lru_cache
from pathlib import Path
import urllib.request
from urllib.parse import urlencode

from dotenv import load_dotenv


WATCHMODE_DIR = Path(__file__).resolve().parent.parent / "WatchmodeAPI"
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _rank_option(option: str, query: str) -> tuple[int, int, int, str]:
    option_lower = option.lower()
    query_lower = query.lower().strip()

    if not query_lower:
        return (3, 9999, len(option), option_lower)

    if option_lower == query_lower:
        return (0, 0, len(option), option_lower)
    if option_lower.startswith(query_lower):
        return (1, 0, len(option), option_lower)

    index = option_lower.find(query_lower)
    if index >= 0:
        return (2, index, len(option), option_lower)

    return (3, 9999, len(option), option_lower)


@lru_cache(maxsize=1)
def load_watchmode_filter_data() -> dict[str, list[str]]:
    api_data = json.loads((WATCHMODE_DIR / "api_data.json").read_text(encoding="utf-8"))
    genres = sorted({entry["name"] for entry in api_data["genre_data"] if entry.get("name")})
    services = sorted({entry["name"] for entry in api_data["source_data"] if entry.get("name")})
    return {"genres": genres, "services": services}


@lru_cache(maxsize=1)
def load_actor_names() -> list[str]:
    actor_map = json.loads((WATCHMODE_DIR / "person_id_map.json").read_text(encoding="utf-8"))
    return list(actor_map.keys())


def search_actor_names(query: str, limit: int = 12) -> list[str]:
    actor_names = load_actor_names()
    clean_query = query.strip().lower()

    if not clean_query:
        return []

    matches = [name for name in actor_names if clean_query in name.lower()]
    matches.sort(key=lambda name: _rank_option(name, clean_query))
    return [name.title() for name in matches[:limit]]


def search_movie_titles(query: str, limit: int = 12) -> list[str]:
    clean_query = query.strip()
    if len(clean_query) < 2:
        return []

    api_key = os.getenv("WATCHMODE_API_KEY")
    if not api_key:
        return []

    params = {
        "apiKey": api_key,
        "search_field": "name",
        "types": "movie",
        "search_value": clean_query,
    }
    url = f"https://api.watchmode.com/v1/search/?{urlencode(params)}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    with opener.open(url, timeout=10) as response:
        payload = json.loads(response.read().decode())

    raw_titles = [
        item.get("name", "")
        for item in payload.get("title_results", [])
        if item.get("type") == "movie" and item.get("name")
    ]

    deduped_titles = list(dict.fromkeys(raw_titles))
    deduped_titles.sort(key=lambda title: _rank_option(title, clean_query))
    return deduped_titles[:limit]
