from argparse import Namespace

import cli


def test_build_filters_from_args_applies_limits():
    args = Namespace(
        genres="Action,Sci-Fi,Drama,Comedy",
        services="Netflix,Prime Video",
        actors="Tom Cruise,Emily Blunt",
        movies="Dune,Inception,Arrival,Interstellar",
    )

    filters = cli.build_filters_from_args(args)

    assert filters["genres"] == ["Action", "Sci-Fi", "Drama"]
    assert filters["services"] == ["Netflix", "Prime Video"]
    assert filters["actors"] == ["Tom Cruise"]
    assert filters["movies"] == ["Dune", "Inception", "Arrival"]


def test_collect_interactive_filters_genres(monkeypatch):
    answers = iter(["Netflix,Disney+", "1", "Action,Sci-Fi,Adventure"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    filters = cli.collect_interactive_filters()

    assert filters == {
        "genres": ["Action", "Sci-Fi", "Adventure"],
        "services": ["Netflix", "Disney+"],
        "actors": [],
        "movies": [],
    }


def test_get_deck_mock_returns_normalized_movies():
    filters = {
        "genres": ["Action"],
        "services": ["Max"],
        "actors": [],
        "movies": [],
    }

    deck = cli.get_deck(filters, mock_mode=True)

    assert deck
    first_movie = deck[0]
    assert "genre" in first_movie
    assert "description" in first_movie
    assert "castList" in first_movie
    assert "streamingServices" in first_movie
