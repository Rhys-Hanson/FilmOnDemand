import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Add the current directory to sys.path to allow importing from server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.mock_data import MOCK_MOVIES
from server.movie_service import build_deck, normalize_movie_payload

MAX_GENRES = 3
MAX_SIMILAR_MOVIES = 3
MAX_ACTORS = 1
DISPLAY_LIMIT = 10


def parse_args():
    parser = argparse.ArgumentParser(description="FilmOnDemand Movie Recommendation CLI")
    parser.add_argument("--genres", type=str, help="Comma-separated list of genres (max 3)")
    parser.add_argument("--services", type=str, help="Comma-separated list of streaming services")
    parser.add_argument("--actors", type=str, help="Comma-separated list of actor or director names (max 1)")
    parser.add_argument("--movies", type=str, help="Comma-separated list of similar movie titles (max 3)")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch the interactive prompt flow even when flags are provided",
    )

    use_mock_env = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    parser.add_argument("--mock", action="store_true", default=use_mock_env, help="Use mock data instead of live API calls")

    return parser.parse_args()


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def limit_items(items: list[str], maximum: int) -> list[str]:
    return items[:maximum]


def is_interactive_mode(args: argparse.Namespace) -> bool:
    has_filter_flags = any([args.genres, args.services, args.actors, args.movies])
    return args.interactive or not has_filter_flags


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter at least one value.")


def prompt_csv_list(label: str, maximum: int, required: bool = False) -> list[str]:
    while True:
        suffix = "s" if maximum > 1 else ""
        raw_value = input(f"{label} (comma-separated, max {maximum} item{suffix}): ").strip()
        values = split_csv(raw_value)

        if not values and not required:
            return []
        if not values and required:
            print("Please enter at least one value.")
            continue
        if len(values) > maximum:
            print(f"Please enter no more than {maximum} item{suffix}.")
            continue
        return values


def prompt_choice() -> str:
    options = {
        "1": "genres",
        "2": "actors",
        "3": "movies",
    }

    print("\nHow should we build your recommendations?")
    print("  1. Genres")
    print("  2. Actor or Director")
    print("  3. Similar Movies")

    while True:
        choice = input("Choose 1, 2, or 3: ").strip()
        if choice in options:
            return options[choice]
        print("Please choose 1, 2, or 3.")


def collect_interactive_filters() -> dict[str, list[str]]:
    print("\n" + "=" * 78)
    print("FILMONDEMAND CONTAINER DEMO")
    print("=" * 78)
    print("Answer a few prompts and we will build a movie recommendation deck for you.\n")

    services = prompt_csv_list("Enter your streaming services", maximum=10, required=True)
    chosen_mode = prompt_choice()

    filters = {
        "genres": [],
        "services": services,
        "actors": [],
        "movies": [],
    }

    if chosen_mode == "genres":
        filters["genres"] = prompt_csv_list("Enter up to 3 genres", maximum=MAX_GENRES, required=True)
    elif chosen_mode == "actors":
        filters["actors"] = prompt_csv_list("Enter 1 actor or director", maximum=MAX_ACTORS, required=True)
    else:
        filters["movies"] = prompt_csv_list("Enter up to 3 similar movies", maximum=MAX_SIMILAR_MOVIES, required=True)

    return filters


def build_filters_from_args(args: argparse.Namespace) -> dict[str, list[str]]:
    return {
        "genres": limit_items(split_csv(args.genres), MAX_GENRES),
        "services": split_csv(args.services),
        "actors": limit_items(split_csv(args.actors), MAX_ACTORS),
        "movies": limit_items(split_csv(args.movies), MAX_SIMILAR_MOVIES),
    }


def format_value(value: Any, fallback: str = "N/A") -> str:
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip()) or fallback
    return str(value)


def format_score(label: str, value: Any, suffix: str = "") -> str:
    if value in (None, "", 0):
        return f"{label}: N/A"
    if isinstance(value, float):
        return f"{label}: {value:.1f}{suffix}"
    return f"{label}: {value}{suffix}"


def format_cast(cast_list: list[dict[str, Any]]) -> str:
    if not cast_list:
        return "N/A"

    formatted_people = []
    for person in cast_list[:5]:
        name = person.get("name", "Unknown")
        character = person.get("character")
        if character:
            formatted_people.append(f"{name} as {character}")
        else:
            formatted_people.append(name)
    return "; ".join(formatted_people)


def print_filters_summary(filters: dict[str, list[str]], mock_mode: bool) -> None:
    mode_label = "Mock Data" if mock_mode else "Live APIs"
    print("\n" + "-" * 78)
    print(f"Mode: {mode_label}")
    print(f"Streaming Services: {format_value(filters.get('services', []))}")
    print(f"Genres: {format_value(filters.get('genres', []))}")
    print(f"Actor/Director: {format_value(filters.get('actors', []))}")
    print(f"Similar Movies: {format_value(filters.get('movies', []))}")
    print("-" * 78)


def print_movie_card(index: int, movie: dict[str, Any]) -> None:
    print("\n" + "=" * 78)
    print(f"Recommendation #{index}: {movie.get('title', 'Unknown Title')} ({format_value(movie.get('year'))})")
    print("=" * 78)
    print(f"Synopsis: {format_value(movie.get('description') or movie.get('summary'), 'No synopsis available.')}")
    print(
        f"Quick Facts: {format_value(movie.get('runtime'))} | "
        f"{format_value(movie.get('maturityRating'))} | "
        f"{format_value(movie.get('genre'))}"
    )
    print(
        "Ratings: "
        + " | ".join(
            [
                format_score("IMDb", movie.get("imdbScore")),
                format_score("Rotten Tomatoes", movie.get("rtScore"), "%"),
                format_score("Metacritic", movie.get("metacriticScore")),
            ]
        )
    )
    print(f"Streaming Services: {format_value(movie.get('streamingServices'))}")
    print(f"Director: {format_value(movie.get('director'))}")
    print(f"Writer: {format_value(movie.get('writer'))}")
    print(f"Language: {format_value(movie.get('language'))}")
    print(f"Country: {format_value(movie.get('country'))}")
    print(f"Awards: {format_value(movie.get('awards'))}")
    print(f"Box Office: {format_value(movie.get('boxOffice'))}")
    print(f"Trailer YouTube ID: {format_value(movie.get('youtubeId'))}")
    print(f"Poster URL: {format_value(movie.get('posterUrl'))}")
    print(f"Top Billed Cast: {format_cast(movie.get('castList') or [])}")


def get_deck(filters: dict[str, list[str]], mock_mode: bool) -> list[dict[str, Any]]:
    if mock_mode:
        return normalize_movie_payload(filters, MOCK_MOVIES)
    return build_deck(filters)


def main():
    args = parse_args()
    interactive_mode = is_interactive_mode(args)

    if interactive_mode:
        filters = collect_interactive_filters()
    else:
        filters = build_filters_from_args(args)

    print_filters_summary(filters, args.mock)

    if args.mock:
        print("\nFetching recommendations from mock data...")
    else:
        print("\nFetching recommendations from live APIs. This may take a moment...")

    try:
        deck = get_deck(filters, args.mock)
    except Exception as exc:
        print(f"\nError: Failed to fetch movies. {exc}")
        sys.exit(1)

    if not deck:
        print("\nNo movies found matching your criteria.")
        return

    print(f"\nFound {len(deck)} recommendations. Showing the top {min(DISPLAY_LIMIT, len(deck))} movie profiles.")

    for index, movie in enumerate(deck[:DISPLAY_LIMIT], start=1):
        print_movie_card(index, movie)

    print("\n" + "-" * 78)
    print("End of FilmOnDemand recommendation deck.")
    print("-" * 78)


if __name__ == "__main__":
    main()
