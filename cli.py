import argparse
import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Add the current directory to sys.path to allow importing from server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.movie_service import build_deck
from server.mock_data import MOCK_MOVIES

def parse_args():
    parser = argparse.ArgumentParser(description="FilmOnDemand Movie Recommendation CLI")
    
    parser.add_argument("--genres", type=str, help="Comma-separated list of genres (e.g., 'Action,Sci-Fi')")
    parser.add_argument("--services", type=str, help="Comma-separated list of streaming services (e.g., 'Netflix,Hulu')")
    parser.add_argument("--actors", type=str, help="Comma-separated list of actor names")
    parser.add_argument("--movies", type=str, help="Comma-separated list of similar movie titles")
    
    # Default to USE_MOCK_DATA env var if flag is not provided
    use_mock_env = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    parser.add_argument("--mock", action="store_true", default=use_mock_env, help="Use mock data instead of live API calls")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    filters = {
        "genres": [g.strip() for g in args.genres.split(",")] if args.genres else [],
        "services": [s.strip() for s in args.services.split(",")] if args.services else [],
        "actors": [a.strip() for a in args.actors.split(",")] if args.actors else [],
        "movies": [m.strip() for m in args.movies.split(",")] if args.movies else []
    }
    
    print("\n--- FilmOnDemand Recommendation Engine ---")
    if args.mock:
        print("[MODE] Using Mock Data")
        deck = MOCK_MOVIES
    else:
        print("[MODE] Fetching Live Data (This may take a moment)...")
        try:
            deck = build_deck(filters)
        except Exception as e:
            print(f"Error: Failed to fetch movies. {e}")
            sys.exit(1)
            
    if not deck:
        print("No movies found matching your criteria.")
        return

    print(f"\nFound {len(deck)} recommendations. Top 10 listed below:\n")
    print("-" * 60)
    
    for i, movie in enumerate(deck[:10], 1):
        title = movie.get("title", "Unknown Title")
        year = movie.get("year", "N/A")
        summary = movie.get("summary") or movie.get("description") or "No summary available."
        
        print(f"{i}. {title} ({year})")
        print(f"   Summary: {summary}")
        print("-" * 60)

if __name__ == "__main__":
    main()
