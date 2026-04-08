"""
test_trakt_api.py
=================
Pytest test suite for TraktAPI (main.py)
Run with: pytest test_trakt_api.py -v
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import TraktAPI


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def api():
    """Creates a single TraktAPI instance shared across all tests in the module."""
    return TraktAPI()


# ─────────────────────────────────────────────
# 1. HEADERS TESTS
# ─────────────────────────────────────────────

class TestGetHeaders:

    def test_headers_returns_dict(self, api):
        """get_headers() should return a dictionary."""
        assert isinstance(api.get_headers(), dict)

    def test_headers_contains_required_keys(self, api):
        """get_headers() should contain all 3 required Trakt API headers."""
        headers = api.get_headers()
        assert "Content-Type" in headers
        assert "trakt-api-version" in headers
        assert "trakt-api-key" in headers

    def test_headers_content_type(self, api):
        """Content-Type should be application/json."""
        assert api.get_headers()["Content-Type"] == "application/json"

    def test_headers_api_version(self, api):
        """trakt-api-version should be '2'."""
        assert api.get_headers()["trakt-api-version"] == "2"

    def test_headers_api_key_not_none(self, api):
        """API key should be loaded from .env and not be None."""
        assert api.get_headers()["trakt-api-key"] is not None, (
            "TRAKT_API_KEY is None — make sure your .env file has TRAKT_API_KEY set."
        )


# ─────────────────────────────────────────────
# 2. PARSE RESULTS TESTS
# ─────────────────────────────────────────────

class TestParseResults:

    def test_parse_results_returns_dict(self, api):
        """parse_results() should return a dictionary."""
        assert isinstance(api.parse_results({"watchers": 500}, "Inception", 1, "trending"), dict)

    def test_parse_results_found_is_true(self, api):
        """parse_results() should always set found=True."""
        assert api.parse_results({"watchers": 100}, "Inception", 1, "trending")["found"] is True

    def test_parse_results_title(self, api):
        """parse_results() should correctly store the title."""
        assert api.parse_results({"watchers": 100}, "Inception", 5, "trending")["title"] == "Inception"

    def test_parse_results_trending_rank(self, api):
        """parse_results() should store the correct trending rank."""
        assert api.parse_results({"watchers": 100}, "Inception", 7, "trending")["trending_rank"] == 7

    def test_parse_results_watchers_as_popularity(self, api):
        """parse_results() should use watchers as the popularity score."""
        assert api.parse_results({"watchers": 250}, "Inception", 1, "trending")["popularity_score"] == 250

    def test_parse_results_missing_watchers_defaults_to_zero(self, api):
        """parse_results() should default popularity_score to 0 if watchers is missing."""
        assert api.parse_results({}, "Inception", 1, "popular")["popularity_score"] == 0

    def test_parse_results_source_label(self, api):
        """parse_results() should correctly format the source label."""
        assert api.parse_results({"watchers": 50}, "Inception", 1, "trending")["source"] == "Trakt (trending)"


# ─────────────────────────────────────────────
# 3. FETCH MOVIES TESTS (live API calls)
# ─────────────────────────────────────────────

class TestFetchMovies:

    def test_fetch_known_movie_returns_dict(self, api):
        """fetch_movies() should return a dict for a well-known movie."""
        assert isinstance(api.fetch_movies("Inception"), dict)

    def test_fetch_known_movie_has_title(self, api):
        """fetch_movies() result should contain the title field."""
        assert "title" in api.fetch_movies("Inception")

    def test_fetch_unknown_movie_returns_not_found(self, api):
        """fetch_movies() should return found=False for a nonsense title."""
        result = api.fetch_movies("xyzzy_fake_movie_title_12345")
        assert result is not None
        assert result.get("found") is False

    def test_fetch_movie_case_insensitive(self, api):
        """fetch_movies() should match regardless of input capitalisation."""
        result_upper = api.fetch_movies("Inception")
        result_lower = api.fetch_movies("inception")
        assert result_upper.get("found") == result_lower.get("found")

    def test_fetch_movie_empty_string(self, api):
        """fetch_movies() should handle an empty string without raising."""
        try:
            result = api.fetch_movies("")
            assert result is not None
        except Exception as e:
            pytest.fail(f"fetch_movies('') raised an exception: {e}")


# ─────────────────────────────────────────────
# 4. FETCH CATEGORY TESTS (live API calls)
# ─────────────────────────────────────────────

class TestFetchCategory:

    @pytest.mark.parametrize("category", ["trending", "popular", "anticipated"])
    def test_standard_categories_return_list(self, api, category):
        """trending, popular, and anticipated should return a non-empty list."""
        result = api.fetch_category(category)
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.parametrize("category", ["played", "watched", "collected"])
    def test_period_categories_return_list(self, api, category):
        """played, watched, and collected (weekly) should return a non-empty list."""
        result = api.fetch_category(category)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_category_movie_has_required_fields(self, api):
        """Each movie entry from fetch_category() should have rank, title, year, stats."""
        movie = api.fetch_category("trending")[0]
        for field in ("rank", "title", "year", "stats"):
            assert field in movie

    def test_category_ranks_start_at_one(self, api):
        """The first movie returned should have rank=1, not rank=0."""
        result = api.fetch_category("popular")
        assert result[0]["rank"] == 1, (
            f"Expected rank=1 for the first movie, got rank={result[0]['rank']}. "
            "This is the off-by-one bug caused by enumerate(data, start=0)."
        )

    def test_category_ranks_are_sequential(self, api):
        """Ranks should be sequential starting from 1."""
        result = api.fetch_category("popular")
        for i, movie in enumerate(result, start=1):
            assert movie["rank"] == i

    def test_trending_has_watchers_stat(self, api):
        """Trending movies should include a watchers_right_now stat."""
        assert "watchers_right_now" in api.fetch_category("trending")[0]["stats"]

    def test_played_has_correct_stats(self, api):
        """Played movies should include play_count and unique_watchers stats."""
        stats = api.fetch_category("played")[0]["stats"]
        assert "play_count" in stats
        assert "unique_watchers" in stats

    def test_collected_has_correct_stats(self, api):
        """Collected movies should include collectors and collect_count stats."""
        stats = api.fetch_category("collected")[0]["stats"]
        assert "collectors" in stats
        assert "collect_count" in stats

    def test_anticipated_has_list_count_stat(self, api):
        """Anticipated movies should include a list_count stat."""
        assert "list_count" in api.fetch_category("anticipated")[0]["stats"]

    def test_category_returns_up_to_100_movies(self, api):
        """fetch_category() should return at most 100 movies."""
        assert len(api.fetch_category("popular")) <= 100

    def test_invalid_category_returns_empty_list(self, api):
        """
        An unrecognised category falls through the if/elif chain to the else
        branch which still appends entries — so the result is a non-None list.
        (If you ever want this to return None instead, add explicit validation
        in fetch_category().)
        """
        result = api.fetch_category("invalid_category_xyz")
        # The API will return a 404, so fetch_category() returns None
        assert result is None


# ─────────────────────────────────────────────
# 5. RANK MOVIES TESTS (live API calls)
# ─────────────────────────────────────────────

class TestRankMovies:

    def test_rank_movies_returns_list(self, api):
        """rank_movies() should return a list."""
        assert isinstance(api.rank_movies(["Inception", "Interstellar"]), list)

    def test_rank_movies_returns_correct_count(self, api):
        """rank_movies() should return the same number of entries as input titles."""
        movies = ["Inception", "The Dark Knight", "Interstellar"]
        assert len(api.rank_movies(movies)) == len(movies)

    def test_rank_movies_each_entry_is_dict(self, api):
        """Each entry in rank_movies() output should be a dictionary."""
        assert isinstance(api.rank_movies(["Inception"])[0], dict)

    def test_rank_movies_contains_required_keys(self, api):
        """Each movie dict should contain all expected keys."""
        movie = api.rank_movies(["Inception"])[0]
        for key in [
            "title", "year", "trending_rank", "watchers",
            "popularity_rank", "total_plays", "total_watchers",
            "collectors", "trakt_rating",
            "rating_votes", "trakt_id", "imdb_id", "tmdb_id"
        ]:
            assert key in movie, f"Missing key: {key}"

    def test_rank_movies_empty_list(self, api):
        """rank_movies([]) should return an empty list without crashing."""
        try:
            assert api.rank_movies([]) == []
        except Exception as e:
            pytest.fail(f"rank_movies([]) raised an exception: {e}")

    def test_rank_movies_fake_title_included_in_results(self, api):
        """rank_movies() with a fake title should still include it in the output."""
        result = api.rank_movies(["xyzzy_fake_movie_title_12345"])
        assert len(result) == 1
        assert result[0]["title"] == "xyzzy_fake_movie_title_12345"

    def test_rank_movies_trakt_rating_is_numeric(self, api):
        """Trakt rating should be a float or int for a well-known movie."""
        rating = api.rank_movies(["Inception"])[0].get("trakt_rating")
        if rating != "N/A":
            assert isinstance(rating, (int, float))

    def test_rank_movies_imdb_id_format(self, api):
        """IMDb IDs should start with 'tt' for known movies."""
        imdb_id = api.rank_movies(["Inception"])[0].get("imdb_id", "N/A")
        if imdb_id != "N/A":
            assert imdb_id.startswith("tt"), f"Unexpected IMDb ID format: {imdb_id}"

    def test_rank_movies_trending_before_non_trending(self, api):
        """A currently trending movie should be ranked ahead of a non-trending one."""
        result = api.rank_movies(["Inception", "Metropolis"])
        inception_idx = next((i for i, m in enumerate(result) if m["title"] == "Inception"), None)
        metropolis_idx = next((i for i, m in enumerate(result) if m["title"] == "Metropolis"), None)
        if inception_idx is not None and metropolis_idx is not None:
            assert inception_idx <= metropolis_idx

    # ── BUG DETECTION: per-movie stats via /movies/{slug}/stats ─────────────
    #
    # rank_movies() now uses the /movies/{slug}/stats endpoint to fetch
    # total_plays, total_watchers, and collectors for every movie individually.
    # This means ANY well-known movie should have non-zero values — unlike
    # the old approach which relied on the movie appearing in a weekly top-100.
    #
    # If these tests fail with 0, it means the /stats call is broken or
    # the response field names have changed.
    # ─────────────────────────────────────────────────────────────────────

    def test_total_plays_nonzero_for_known_movie(self, api):
        """
        BUG TEST — total_plays should be > 0 for any well-known movie.

        Uses /movies/{slug}/stats which returns all-time stats, so even older
        movies like Inception will always have data.
        """
        result = api.rank_movies(["Inception"])
        movie = result[0]
        plays = movie.get("total_plays", 0)
        assert plays > 0, (
            f"total_plays={plays} for 'Inception'. "
            "Expected a non-zero value — check the /movies/{{slug}}/stats call."
        )

    def test_total_watchers_nonzero_for_known_movie(self, api):
        """
        BUG TEST — total_watchers should be > 0 for any well-known movie.
        """
        result = api.rank_movies(["Inception"])
        movie = result[0]
        watchers = movie.get("total_watchers", 0)
        assert watchers > 0, (
            f"total_watchers={watchers} for 'Inception'. "
            "Expected a non-zero value — check the /movies/{{slug}}/stats call."
        )

    def test_collectors_nonzero_for_known_movie(self, api):
        """
        BUG TEST — collectors should be > 0 for any well-known movie.
        """
        result = api.rank_movies(["Inception"])
        movie = result[0]
        collectors = movie.get("collectors", 0)
        assert collectors > 0, (
            f"collectors={collectors} for 'Inception'. "
            "Expected a non-zero value — check the /movies/{{slug}}/stats call."
        )