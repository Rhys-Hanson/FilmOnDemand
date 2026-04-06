"""
Tests for OMDbAPI module.
Run:  pytest OMDbAPI/test_omdb.py -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OMDbAPI.main import OMDbAPI


class TestOMDbAPINoKey:
    """These tests run without any API key set — verify graceful fallback."""

    def setup_method(self):
        os.environ.pop("OMDB_API_KEY", None)
        self.api = OMDbAPI()

    def test_enrich_returns_none_when_no_key(self):
        result = self.api.enrich("Inception", year=2010)
        assert result is None, "Should return None when OMDB_API_KEY is not set"

    def test_enrich_with_imdb_id_returns_none_when_no_key(self):
        result = self.api.enrich("Inception", imdb_id="tt1375666")
        assert result is None


class TestOMDbAPIParser:
    """Unit-test the _parse static method independently — no network needed."""

    SAMPLE_RESPONSE = {
        "Response": "True",
        "Title": "Inception",
        "Year": "2010",
        "imdbRating": "8.8",
        "imdbVotes": "2,452,073",
        "Metascore": "74",
        "Ratings": [
            {"Source": "Internet Movie Database", "Value": "8.8/10"},
            {"Source": "Rotten Tomatoes", "Value": "87%"},
            {"Source": "Metacritic", "Value": "74/100"},
        ],
        "Awards": "Won 4 Oscars. 160 wins & 220 nominations.",
        "BoxOffice": "$292,587,330",
        "Writer": "Christopher Nolan",
        "Language": "English, Japanese, French",
        "Country": "United States, United Kingdom",
    }

    def test_imdb_score(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["imdbScore"] == 8.8

    def test_imdb_votes(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["imdbVotes"] == "2,452,073"

    def test_rt_score(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["rtScore"] == 87.0

    def test_metacritic_score(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["metacriticScore"] == 74.0

    def test_awards(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert "Won 4 Oscars" in parsed["awards"]

    def test_box_office(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["boxOffice"] == "$292,587,330"

    def test_writer(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert parsed["writer"] == "Christopher Nolan"

    def test_language(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert "Japanese" in parsed["language"]

    def test_country(self):
        parsed = OMDbAPI._parse(self.SAMPLE_RESPONSE)
        assert "United States" in parsed["country"]

    def test_na_fields_become_none(self):
        response = dict(self.SAMPLE_RESPONSE)
        response["Awards"] = "N/A"
        response["BoxOffice"] = "N/A"
        parsed = OMDbAPI._parse(response)
        assert parsed["awards"] is None
        assert parsed["boxOffice"] is None

    def test_missing_rt_rating(self):
        response = dict(self.SAMPLE_RESPONSE)
        response["Ratings"] = [{"Source": "Internet Movie Database", "Value": "8.8/10"}]
        parsed = OMDbAPI._parse(response)
        assert parsed["rtScore"] == 0.0
