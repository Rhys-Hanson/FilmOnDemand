"""
test_omdb_api.py
================
Pytest test suite for OMDbAPI (main.py)
Run with:  pytest OMDbAPI/test_omdb_api.py -v

Structure
---------
1. TestOMDbAPIInit        — key loading and fallback behaviour
2. TestParseHelper        — _parse() static method (no network)
3. TestEnrichLive         — enrich() live API calls (requires OMDB_API_KEY in .env)
4. TestEnrichByTitle      — title-only lookups
5. TestEnrichEdgeCases    — empty / invalid / N/A inputs
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OMDbAPI.main import OMDbAPI


# ─────────────────────────────────────────────
# SHARED FIXTURE
# ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def api():
    """Creates a single OMDbAPI instance shared across all tests in the module."""
    return OMDbAPI()


# ─────────────────────────────────────────────
# SAMPLE RESPONSES (reused across test classes)
# ─────────────────────────────────────────────

INCEPTION_RESPONSE = {
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

NOT_FOUND_RESPONSE = {
    "Response": "False",
    "Error": "Movie not found!",
}


# ─────────────────────────────────────────────
# 1. INIT TESTS
# ─────────────────────────────────────────────

class TestOMDbAPIInit:

    def test_api_key_loaded_from_env(self, api):
        """OMDB_API_KEY should be loaded from the .env file."""
        assert api._api_key, (
            "OMDB_API_KEY is empty — make sure your .env file has OMDB_API_KEY set."
        )

    def test_api_key_is_string(self, api):
        """OMDB_API_KEY should be a non-empty string."""
        assert isinstance(api._api_key, str)
        assert len(api._api_key) > 0

    def test_no_key_returns_none_immediately(self):
        """enrich() should return None without making a network call when key is missing."""
        with patch("OMDbAPI.main.os.getenv", return_value=""):
            keyless_api = OMDbAPI()
        result = keyless_api.enrich("Inception", year=2010)
        assert result is None, "Expected None when OMDB_API_KEY is not set"


# ─────────────────────────────────────────────
# 2. PARSER TESTS (no network required)
# ─────────────────────────────────────────────

class TestParseHelper:
    """Unit-tests for OMDbAPI._parse() — exercises every field without hitting the network."""

    def test_parse_returns_dict(self):
        """_parse() should always return a dict."""
        assert isinstance(OMDbAPI._parse(INCEPTION_RESPONSE), dict)

    def test_parse_imdb_score(self):
        """imdbScore should be parsed as a float."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["imdbScore"] == 8.8

    def test_parse_imdb_votes_preserved_as_string(self):
        """imdbVotes should be kept as a formatted string (e.g. '2,793,322')."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["imdbVotes"] == "2,793,322"

    def test_parse_rt_score(self):
        """Rotten Tomatoes % should be parsed from the Ratings list."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["rtScore"] == 87.0

    def test_parse_metacritic_score(self):
        """Metascore should be parsed as a float."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["metacriticScore"] == 74.0

    def test_parse_awards(self):
        """awards should contain the full awards string."""
        assert "Won 4 Oscars" in OMDbAPI._parse(INCEPTION_RESPONSE)["awards"]

    def test_parse_box_office(self):
        """boxOffice should be the raw dollar string from OMDb."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["boxOffice"] == "$292,587,330"

    def test_parse_writer(self):
        """writer should be the screenwriter credit string."""
        assert OMDbAPI._parse(INCEPTION_RESPONSE)["writer"] == "Christopher Nolan"

    def test_parse_language(self):
        """language should include all languages listed."""
        assert "Japanese" in OMDbAPI._parse(INCEPTION_RESPONSE)["language"]

    def test_parse_country(self):
        """country should include all production countries."""
        assert "United States" in OMDbAPI._parse(INCEPTION_RESPONSE)["country"]

    def test_parse_na_awards_becomes_none(self):
        """An 'N/A' awards field should be normalised to None."""
        response = {**INCEPTION_RESPONSE, "Awards": "N/A"}
        assert OMDbAPI._parse(response)["awards"] is None

    def test_parse_na_box_office_becomes_none(self):
        """An 'N/A' BoxOffice field should be normalised to None."""
        response = {**INCEPTION_RESPONSE, "BoxOffice": "N/A"}
        assert OMDbAPI._parse(response)["boxOffice"] is None

    def test_parse_na_writer_becomes_none(self):
        """An 'N/A' Writer field should be normalised to None."""
        response = {**INCEPTION_RESPONSE, "Writer": "N/A"}
        assert OMDbAPI._parse(response)["writer"] is None

    def test_parse_na_language_becomes_none(self):
        """An 'N/A' Language field should be normalised to None."""
        response = {**INCEPTION_RESPONSE, "Language": "N/A"}
        assert OMDbAPI._parse(response)["language"] is None

    def test_parse_missing_rt_rating_defaults_to_zero(self):
        """If Rotten Tomatoes is absent from Ratings list, rtScore should default to 0.0."""
        response = {**INCEPTION_RESPONSE, "Ratings": [
            {"Source": "Internet Movie Database", "Value": "8.8/10"},
        ]}
        assert OMDbAPI._parse(response)["rtScore"] == 0.0

    def test_parse_missing_metascore_defaults_to_zero(self):
        """A missing or 'N/A' Metascore should default to 0.0."""
        response = {**INCEPTION_RESPONSE, "Metascore": "N/A"}
        assert OMDbAPI._parse(response)["metacriticScore"] == 0.0

    def test_parse_all_expected_keys_present(self):
        """_parse() output must contain all 9 enrichment keys."""
        result = OMDbAPI._parse(INCEPTION_RESPONSE)
        for key in ["imdbScore", "imdbVotes", "rtScore", "metacriticScore",
                    "awards", "boxOffice", "writer", "language", "country"]:
            assert key in result, f"Missing key: {key}"


# ─────────────────────────────────────────────
# 3. LIVE ENRICH TESTS (requires valid API key)
# ─────────────────────────────────────────────

class TestEnrichLive:
    """Live calls to the OMDb API — these require OMDB_API_KEY in .env."""

    def test_enrich_well_known_movie_returns_dict(self, api):
        """enrich() should return a dict for a well-known movie."""
        result = api.enrich("Inception", year=2010)
        assert isinstance(result, dict), "Expected a dict — check your OMDB_API_KEY"

    def test_enrich_returns_all_required_keys(self, api):
        """Live enrich() result must contain all 9 enrichment keys."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        for key in ["imdbScore", "imdbVotes", "rtScore", "metacriticScore",
                    "awards", "boxOffice", "writer", "language", "country"]:
            assert key in result, f"Missing key in live response: {key}"

    def test_enrich_imdb_score_reasonable_range(self, api):
        """Inception's IMDb score should be between 1.0 and 10.0."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        score = result["imdbScore"]
        assert 1.0 <= score <= 10.0, f"IMDb score {score} is outside expected range"

    def test_enrich_rt_score_reasonable_range(self, api):
        """Inception's RT score should be between 0 and 100."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        score = result["rtScore"]
        assert 0 <= score <= 100, f"RT score {score} is outside expected range"

    def test_enrich_imdb_votes_is_formatted_string(self, api):
        """imdbVotes should be a non-empty string containing digits (e.g. '2,793,322')."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        votes = result["imdbVotes"]
        assert isinstance(votes, str)
        assert any(c.isdigit() for c in votes), f"Unexpected imdbVotes format: {votes}"

    def test_enrich_awards_contains_text(self, api):
        """Awards string for Inception should be non-empty."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        assert result["awards"] and len(result["awards"]) > 0

    def test_enrich_box_office_starts_with_dollar(self, api):
        """BoxOffice value should start with '$'."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        box = result["boxOffice"]
        assert box and box.startswith("$"), f"Unexpected BoxOffice format: {box}"

    def test_enrich_writer_is_nonempty_string(self, api):
        """Writer credit should be a non-empty string."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        assert isinstance(result["writer"], str)
        assert len(result["writer"]) > 0

    def test_enrich_language_contains_english(self, api):
        """Inception's language list should include English."""
        result = api.enrich("Inception", year=2010)
        assert result is not None
        assert "English" in result["language"]

    def test_enrich_by_imdb_id(self, api):
        """Lookup by IMDb ID tt1375666 (Inception) should succeed."""
        result = api.enrich("Inception", imdb_id="tt1375666")
        assert result is not None
        assert result["imdbScore"] > 0


# ─────────────────────────────────────────────
# 4. TITLE-ONLY LOOKUP TESTS
# ─────────────────────────────────────────────

class TestEnrichByTitle:
    """Verify title-only lookups (no year supplied) work correctly."""

    def test_title_only_returns_dict(self, api):
        """enrich() with title only (no year) should still return a dict."""
        result = api.enrich("Parasite")
        assert isinstance(result, dict)

    def test_title_only_imdb_score_nonzero(self, api):
        """imdbScore should be > 0 for a well-known title lookup without a year."""
        result = api.enrich("Parasite")
        assert result is not None
        assert result["imdbScore"] > 0

    def test_different_movies_different_scores(self, api):
        """Two movies with clearly different IMDb scores should not return identical results."""
        inception = api.enrich("Inception", year=2010)
        batman = api.enrich("The Batman", year=2022)
        assert inception is not None and batman is not None
        assert inception["imdbScore"] != batman["imdbScore"]


# ─────────────────────────────────────────────
# 5. EDGE CASE TESTS
# ─────────────────────────────────────────────

class TestEnrichEdgeCases:

    def test_nonexistent_title_returns_none(self, api):
        """A nonsense title that doesn't exist should return None, not raise."""
        result = api.enrich("xyzzy_fake_movie_title_99999zzz")
        assert result is None, "Expected None for a movie that doesn't exist"

    def test_network_error_returns_none(self, api):
        """
        BUG TEST — a network failure should return None gracefully
        rather than propagating an exception up to the engine.
        """
        import urllib.request
        with patch.object(urllib.request, "urlopen", side_effect=OSError("Network down")):
            result = api.enrich("Inception", year=2010)
        assert result is None, "Expected None on network failure, not an exception"

    def test_malformed_json_returns_none(self, api):
        """
        BUG TEST — if OMDb returns malformed JSON, enrich() should return
        None instead of raising a json.JSONDecodeError.
        """
        import urllib.request
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not valid json {{{"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch.object(urllib.request, "urlopen", return_value=mock_resp):
            result = api.enrich("Inception", year=2010)
        assert result is None

    def test_response_false_returns_none(self, api):
        """
        BUG TEST — when OMDb returns Response=False (not found),
        enrich() should return None, not an empty dict or a crash.
        """
        import json
        import urllib.request
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(NOT_FOUND_RESPONSE).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch.object(urllib.request, "urlopen", return_value=mock_resp):
            result = api.enrich("Totally Fake Movie Title ZZZZZ")
        assert result is None

    def test_year_parameter_narrows_results(self, api):
        """Providing a year should not break the lookup vs title-only."""
        with_year = api.enrich("Inception", year=2010)
        without_year = api.enrich("Inception")
        # Both should resolve to the same movie
        assert with_year is not None and without_year is not None
        assert with_year["imdbScore"] == without_year["imdbScore"]
