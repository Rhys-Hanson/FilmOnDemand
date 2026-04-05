from collections import Counter
from typing import Dict

class GameState:
    def __init__(self, room_code: str, initial_player_count: int):
        self.room_code = room_code
        self.total_players = initial_player_count
        self.finished_players = 0
        
        # Using Python's built in Counter to easily tally scores like: {'movie_id_1': 4}
        self.scores = Counter()
        
        # Separate counter: tracks how many players super-liked each movie (+2 pts each)
        self.super_likes = Counter()
        
        # Optional: For future time limit feature
        self.time_limit = None

    def register_swipe(self, movie_id: str, liked: bool):
        """Called when a player swipes right (+1 point)."""
        if liked:
            self.scores[movie_id] += 1

    def register_super_like(self, movie_id: str):
        """Called when a player super-likes (+2 points, tracked separately)."""
        self.scores[movie_id] += 2
        self.super_likes[movie_id] += 1

    def player_finished_deck(self):
        """Called when a player hits the end of their deck. Increment finished_players count."""
        self.finished_players += 1
        
    def is_game_over(self) -> bool:
        """Returns True if finished_players == total_players."""
        return self.finished_players >= self.total_players

    def get_final_results(self) -> dict:
        """Returns scores and super_like counts for the frontend."""
        return {
            "scores": dict(self.scores.most_common()),
            "super_likes": dict(self.super_likes),
        }
