"""
OMDb API Module
===============
Fetches movie enrichment data from the Open Movie Database (OMDb).
Provides: IMDb score, IMDb vote count, Rotten Tomatoes %, Metacritic score,
          Awards string, Box Office gross, Writer credits, Language, Country.

Usage:
    omdb = OMDbAPI()
    data = omdb.enrich("Inception", year=2010)
    # Returns a dict or None if not found / key missing

API key:
    Register free at https://www.omdbapi.com/apikey.aspx
    Add  OMDB_API_KEY=your_key  to your .env file.
    Free tier allows 1 000 requests/day (plenty for a game session).

Fallback behaviour:
    If OMDB_API_KEY is missing or unset, enrich() returns None immediately
    so the rest of the pipeline continues with zeroed scores rather than crashing.
"""

import json
import logging
import os
import ssl
import urllib.request
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Single shared unverified SSL context (same pattern used in WatchmodeAPI)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


class OMDbAPI:
    BASE_URL = "https://www.omdbapi.com/"

    def __init__(self):
        ROOT_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(ROOT_DIR / ".env")
        self._api_key = os.getenv("OMDB_API_KEY", "")
        if not self._api_key:
            logger.warning(
                "OMDB_API_KEY not set – OMDb enrichment will be skipped. "
                "Get a free key at https://www.omdbapi.com/apikey.aspx"
            )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def enrich(self, title: str, year: int | None = None, imdb_id: str | None = None) -> dict | None:
        """
        Fetch OMDb data for a movie.

        Lookup priority:
          1. imdb_id   (tt-number)  – most accurate
          2. title + year           – fast title search
          3. title only             – fallback if year is unavailable

        Returns a dict with the enrichment fields on success, or None on
        failure (network error, not found, missing API key, quota exceeded).
        """
        if not self._api_key:
            return None

        params = {"apikey": self._api_key, "type": "movie", "r": "json"}
        if imdb_id:
            params["i"] = imdb_id
        else:
            params["t"] = title
            if year:
                params["y"] = str(year)

        url = self.BASE_URL + "?" + urllib.parse.urlencode(params)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FilmOnDemand/1.0"})
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
            data = json.loads(raw)
        except Exception as exc:
            logger.warning("OMDb request failed for '%s': %s", title, exc)
            return None

        if data.get("Response") != "True":
            logger.debug("OMDb returned no match for '%s': %s", title, data.get("Error"))
            return None

        return self._parse(data)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(data: dict) -> dict:
        """Extract and normalise the fields we care about."""

        def _rating(source: str) -> str | None:
            for entry in data.get("Ratings", []):
                if entry.get("Source") == source:
                    return entry.get("Value")
            return None

        def _float(val: str | None) -> float:
            if not val or val in ("N/A", ""):
                return 0.0
            try:
                return float(val.split("/")[0].replace("%", "").strip())
            except ValueError:
                return 0.0

        def _int_str(val: str | None) -> str | None:
            """Keep as formatted string (e.g. '2,452,073') or None."""
            if not val or val == "N/A":
                return None
            return val.strip()

        imdb_rating = _float(data.get("imdbRating"))
        imdb_votes = _int_str(data.get("imdbVotes"))

        rt_raw = _rating("Rotten Tomatoes")
        rt_score = _float(rt_raw) if rt_raw else 0.0

        mc_raw = data.get("Metascore")
        metacritic_score = _float(mc_raw) if mc_raw else 0.0

        awards = data.get("Awards")
        if awards == "N/A":
            awards = None

        box_office = data.get("BoxOffice")
        if box_office == "N/A":
            box_office = None

        writer = data.get("Writer")
        if writer == "N/A":
            writer = None

        language = data.get("Language")
        if language == "N/A":
            language = None

        country = data.get("Country")
        if country == "N/A":
            country = None

        return {
            "imdbScore": imdb_rating,
            "imdbVotes": imdb_votes,
            "rtScore": rt_score,
            "metacriticScore": metacritic_score,
            "awards": awards,
            "boxOffice": box_office,
            "writer": writer,
            "language": language,
            "country": country,
        }
