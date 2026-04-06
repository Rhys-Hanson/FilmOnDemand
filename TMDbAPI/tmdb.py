import os
from pathlib import Path

from dotenv import load_dotenv
import requests
from tmdbv3api import TMDb, Movie, Search

IMAGE_BASE_W500 = "https://image.tmdb.org/t/p/w500"
IMAGE_BASE_W185 = "https://image.tmdb.org/t/p/w185"
IMAGE_BASE_ORIGINAL = "https://image.tmdb.org/t/p/original"
YOUTUBE_WATCH = "https://www.youtube.com/watch?v="


class TMDbAPI:
    def __init__(self):
        ROOT_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(ROOT_DIR / ".env")

        api_key = os.getenv("TMDb_API_KEY")
        if not api_key:
            raise ValueError("TMDb_API_KEY is missing. Check your .env file.")

        tmdb = TMDb()
        tmdb.api_key = api_key
        tmdb.language = "en"

        self._movie = Movie()
        self._search = Search()

    # ------------------------------------------------------------------
    # Public interface — return shape is identical to the old tmdb3 version
    # ------------------------------------------------------------------
    def movie_info(self, title: str) -> dict:
        # 1. Search for the movie to get its TMDb ID
        results = self._search.movies(title)
        if not results:
            return {"error": "No movie found"}

        movie_id = results[0].id

        # 2. Fetch full details, credits, videos, and release dates
        detail = self._movie.details(movie_id)
        credits = self._movie.credits(movie_id)
        videos = self._movie.videos(movie_id)
        release_dates = self._movie.release_dates(movie_id)

        # --- Poster URL ---
        poster_url = None
        if getattr(detail, "poster_path", None):
            try:
                poster_url = IMAGE_BASE_W500 + detail.poster_path
            except Exception:
                poster_url = IMAGE_BASE_ORIGINAL + detail.poster_path

        # --- Release Year ---
        year = None
        raw_date = getattr(detail, "release_date", None)
        if raw_date:
            try:
                year = int(str(raw_date)[:4])
            except (ValueError, TypeError):
                pass

        # --- YouTube Trailer ---
        youtube_id = None
        video_results = list(getattr(videos, "results", None) or [])
        for v in video_results:
            if getattr(v, "site", "") == "YouTube" and getattr(v, "type", "") == "Trailer":
                youtube_id = v.key
                break
        if youtube_id is None and video_results:
            youtube_id = getattr(video_results[0], "key", None)

        # --- Runtime ---
        runtime_str = "Unknown"
        runtime_mins = getattr(detail, "runtime", None)
        if runtime_mins:
            hours = runtime_mins // 60
            minutes = runtime_mins % 60
            runtime_str = f"{hours}h {minutes}m"

        # --- Maturity Rating (US certification) ---
        maturity_rating = "Unrated"
        rd_results = list(getattr(release_dates, "results", None) or [])
        for country in rd_results:
            if getattr(country, "iso_3166_1", "") == "US":
                dates = list(getattr(country, "release_dates", None) or [])
                for d in dates:
                    cert = getattr(d, "certification", "") or ""
                    if cert:
                        maturity_rating = cert
                        break
                break

        # --- Cast List (Top 4) ---
        cast_list = []
        raw_cast = list(getattr(credits, "cast", None) or [])
        for actor in raw_cast[:4]:
            image_url = None
            profile_path = getattr(actor, "profile_path", None)
            if profile_path:
                try:
                    image_url = IMAGE_BASE_W185 + profile_path
                except Exception:
                    image_url = IMAGE_BASE_ORIGINAL + profile_path
            cast_list.append({
                "name": getattr(actor, "name", ""),
                "character": getattr(actor, "character", ""),
                "imageUrl": image_url,
            })

        # --- Genres ---
        genres = [g.name for g in list(getattr(detail, "genres", None) or [])]

        # --- Director ---
        director = "Unknown"
        raw_crew = list(getattr(credits, "crew", None) or [])
        directors = [p.name for p in raw_crew if getattr(p, "job", "") == "Director"]
        if directors:
            director = ", ".join(directors)

        # --- Studio ---
        studio = "Unknown"
        companies = list(getattr(detail, "production_companies", None) or [])
        if companies:
            studio = getattr(companies[0], "name", "Unknown")

        # --- Streaming Providers (TMDb - US/CA/GB fallback) ---
        streaming_services = []
        try:
            prov_res = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={self._movie.tmdb.api_key}", 
                timeout=5
            )
            if prov_res.ok:
                prov_data = prov_res.json().get("results", {})
                # Prioritize CA since watchmode is restricted to CA in this deployment, fallback to US
                regional_providers = prov_data.get("CA") or prov_data.get("US", {})
                flatrate = regional_providers.get("flatrate", [])
                for provider in flatrate:
                    name = provider.get("provider_name")
                    if name and name not in streaming_services:
                        streaming_services.append(name)
        except Exception:
            pass

        return {
            "title": getattr(detail, "title", title),
            "description": getattr(detail, "overview", "No description available."),
            "posterUrl": poster_url,
            "year": year,
            "youtubeId": youtube_id,
            "runtime": runtime_str,
            "maturityRating": maturity_rating,
            "castList": cast_list,
            "genres": genres,
            "director": director,
            "studio": studio,
            "streamingServices": streaming_services,
        }