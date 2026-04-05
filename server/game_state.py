from collections import Counter
from typing import Dict

class GameState:
    def __init__(self, room_code: str, initial_player_count: int):
        self.room_code = room_code
        self.total_players = initial_player_count
        self.finished_players = 0
        
        # Net score: +1 right, +2 super-like, -1 left, -2 seen-it
        self.scores = Counter()
        
        # Raw positive votes (right swipe OR super-like) — used for unanimous detection
        self.likes = Counter()
        
        # Tracks how many players super-liked each movie
        self.super_likes = Counter()
        
        # Tracks how many players pressed "Already seen it"
        self.seen_count = Counter()
        
        self.time_limit = None

    def register_swipe(self, movie_id: str, liked: bool):
        """Swipe right (+1 pt, counts as a like) or swipe left (-1 pt)."""
        if liked:
            self.scores[movie_id] += 1
            self.likes[movie_id] += 1
        else:
            self.scores[movie_id] -= 1

    def register_super_like(self, movie_id: str):
        """Super-like: +2 pts, counts as a like, tracked separately."""
        self.scores[movie_id] += 2
        self.super_likes[movie_id] += 1
        self.likes[movie_id] += 1

    def register_seen(self, movie_id: str):
        """Already seen it: -2 pts, tracked separately."""
        self.scores[movie_id] -= 2
        self.seen_count[movie_id] += 1

    def player_finished_deck(self):
        """Called when a player hits the end of their deck. Increment finished_players count."""
        self.finished_players += 1
        
    def is_game_over(self) -> bool:
        """Returns True if finished_players == total_players."""
        return self.finished_players >= self.total_players

    def get_final_results(self) -> dict:
        """Returns all scoring data for the frontend."""
        # Unanimous = every player cast a positive vote (right or super-like)
        unanimous = [
            mid for mid, count in self.likes.items()
            if self.total_players > 0 and count >= self.total_players
        ]
        return {
            "scores": dict(self.scores.most_common()),
            "super_likes": dict(self.super_likes),
            "seen_counts": dict(self.seen_count),
            "unanimous": unanimous,
        }
