from WatchmodeAPI.main import WatchmodeAPI

api = WatchmodeAPI()


# -------------------------
# get_genre_ids() tests
# -------------------------

def test_get_genre_ids_single_genre():
    input = ["Action"]
    actual_output = api.get_genre_ids(input)

    assert isinstance(actual_output, list)
    assert len(actual_output) == 1


def test_get_genre_ids_case_insensitive():
    input = ["action"]
    expected_output = api.get_genre_ids(["Action"])
    actual_output = api.get_genre_ids(input)

    assert expected_output == actual_output


def test_get_genre_ids_strips_whitespace():
    input = ["  Action  "]
    expected_output = api.get_genre_ids(["Action"])
    actual_output = api.get_genre_ids(input)

    assert expected_output == actual_output


def test_get_genre_ids_invalid_genre():
    input = ["FakeGenre"]
    expected_output = []
    actual_output = api.get_genre_ids(input)

    assert expected_output == actual_output


def test_get_genre_ids_multiple_genres():
    input = ["Action", "Comedy"]
    actual_output = api.get_genre_ids(input)

    assert len(actual_output) == 2


# -------------------------
# get_source_ids() tests
# -------------------------

def test_get_source_ids_single_source():
    input = ["Netflix"]
    actual_output = api.get_source_ids(input)

    assert isinstance(actual_output, list)
    assert len(actual_output) == 1


def test_get_source_ids_case_insensitive():
    input = ["netflix"]
    expected_output = api.get_source_ids(["Netflix"])
    actual_output = api.get_source_ids(input)

    assert expected_output == actual_output


def test_get_source_ids_strips_whitespace():
    input = ["  Netflix  "]
    expected_output = api.get_source_ids(["Netflix"])
    actual_output = api.get_source_ids(input)

    assert expected_output == actual_output


def test_get_source_ids_invalid_source():
    input = ["FakeStreamingService"]
    expected_output = []
    actual_output = api.get_source_ids(input)

    assert expected_output == actual_output


def test_get_source_ids_multiple_sources():
    input = ["Netflix", "Disney+"]
    actual_output = api.get_source_ids(input)

    assert len(actual_output) == 2


# -------------------------
# get_actor_id() tests
# -------------------------

def test_get_actor_id_valid_actor():
    input = "Ryan Reynolds"
    actual_output = api.get_actor_id(input)

    assert actual_output is not None


def test_get_actor_id_case_insensitive():
    input = "ryan reynolds"
    expected_output = api.get_actor_id("Ryan Reynolds")
    actual_output = api.get_actor_id(input)

    assert expected_output == actual_output


def test_get_actor_id_whitespace():
    input = "  Ryan Reynolds  "
    expected_output = api.get_actor_id("Ryan Reynolds")
    actual_output = api.get_actor_id(input)

    assert expected_output == actual_output


def test_get_actor_id_invalid_actor():
    input = "This Actor Does Not Exist 123"
    expected_output = None
    actual_output = api.get_actor_id(input)

    assert expected_output == actual_output


def test_get_actor_id_none():
    input = None
    expected_output = None
    actual_output = api.get_actor_id(input)

    assert expected_output == actual_output


# -------------------------
# parse_results() tests
# -------------------------

def test_parse_results_single_movie():
    input = {
        "titles": [
            {"title": "Inception", "tmdb_id": 27205}
        ]
    }
    expected_output = {"Inception": 27205}
    actual_output = api.parse_results(input)

    assert expected_output == actual_output


def test_parse_results_multiple_movies():
    input = {
        "titles": [
            {"title": "Inception", "tmdb_id": 27205},
            {"title": "Interstellar", "tmdb_id": 157336}
        ]
    }
    expected_output = {
        "Inception": 27205,
        "Interstellar": 157336
    }
    actual_output = api.parse_results(input)

    assert expected_output == actual_output


def test_parse_results_empty():
    input = {"titles": []}
    expected_output = {}
    actual_output = api.parse_results(input)

    assert expected_output == actual_output


# -------------------------
# fetch_movies_by_genre() tests
# live API tests
# -------------------------

def test_fetch_movies_by_genre_returns_dict():
    genre_ids = api.get_genre_ids(["Action"])
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_genre(genre_ids, source_ids)

    assert isinstance(actual_output, dict)


def test_fetch_movies_by_genre_contains_titles_key():
    genre_ids = api.get_genre_ids(["Action"])
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_genre(genre_ids, source_ids)

    assert "titles" in actual_output


def test_fetch_movies_by_genre_returns_list_of_titles():
    genre_ids = api.get_genre_ids(["Action"])
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_genre(genre_ids, source_ids)

    assert isinstance(actual_output["titles"], list)


# -------------------------
# fetch_movies_by_actor() tests
# live API tests
# -------------------------

def test_fetch_movies_by_actor_returns_dict():
    actor_id = api.get_actor_id("Ryan Reynolds")
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_actor(actor_id, source_ids)

    assert isinstance(actual_output, dict)


def test_fetch_movies_by_actor_contains_titles_key():
    actor_id = api.get_actor_id("Ryan Reynolds")
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_actor(actor_id, source_ids)

    assert "titles" in actual_output


def test_fetch_movies_by_actor_returns_list_of_titles():
    actor_id = api.get_actor_id("Ryan Reynolds")
    source_ids = api.get_source_ids(["Netflix"])
    actual_output = api.fetch_movies_by_actor(actor_id, source_ids)

    assert isinstance(actual_output["titles"], list)


# -------------------------
# get_watchmode_movie_info() tests
# live API tests
# -------------------------

def test_get_watchmode_movie_info_valid_movie_returns_dict():
    input = "Inception"
    actual_output = api.get_watchmode_movie_info(input)

    assert isinstance(actual_output, dict)


def test_get_watchmode_movie_info_valid_movie_has_tmdb_id():
    input = "Inception"
    actual_output = api.get_watchmode_movie_info(input)

    assert "tmdb_id" in actual_output


def test_get_watchmode_movie_info_valid_movie_has_sources():
    input = "Inception"
    actual_output = api.get_watchmode_movie_info(input)

    assert "sources" in actual_output


def test_get_watchmode_movie_info_invalid_movie_returns_none():
    input = "This Movie Does Not Exist 123456"
    expected_output = None
    actual_output = api.get_watchmode_movie_info(input)

    assert expected_output == actual_output


# -------------------------
# run_for_actors() tests
# top-level method tests
# -------------------------

def test_run_for_actors_invalid_actor():
    input_actor = "This Actor Does Not Exist 123"
    input_sources = ["Netflix"]
    expected_output = []
    actual_output = api.run_for_actors(input_actor, input_sources)

    assert expected_output == actual_output


def test_run_for_actors_valid_actor_returns_dict():
    input_actor = "Ryan Reynolds"
    input_sources = ["Netflix"]
    actual_output = api.run_for_actors(input_actor, input_sources)

    assert isinstance(actual_output, dict)


def test_run_for_actors_valid_actor_not_empty():
    input_actor = "Ryan Reynolds"
    input_sources = ["Netflix"]
    actual_output = api.run_for_actors(input_actor, input_sources)

    assert len(actual_output) > 0


# -------------------------
# run_for_genres() tests
# top-level method tests
# -------------------------

def test_run_for_genres_valid_genre_returns_dict():
    input_genres = ["Action"]
    input_sources = ["Netflix"]
    actual_output = api.run_for_genres(input_genres, input_sources)

    assert isinstance(actual_output, dict)


def test_run_for_genres_valid_genre_not_empty():
    input_genres = ["Action"]
    input_sources = ["Netflix"]
    actual_output = api.run_for_genres(input_genres, input_sources)

    assert len(actual_output) > 0


def test_run_for_genres_multiple_genres_returns_dict():
    input_genres = ["Action", "Comedy"]
    input_sources = ["Netflix"]
    actual_output = api.run_for_genres(input_genres, input_sources)

    assert isinstance(actual_output, dict)