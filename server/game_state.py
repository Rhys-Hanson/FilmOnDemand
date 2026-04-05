from collections import Counter
from typing import Dict

class GameState:
    def __init__(self, room_code: str, initial_player_count: int):
        self.room_code = room_code
        self.total_players = initial_player_count
        self.finished_players = 0
        
        # Using Python's built in Counter to easily tally scores like: {'movie_id_1': 4}
        self.scores = Counter() 
        
        # Optional: For future time limit feature
        self.time_limit = None 

    def register_swipe(self, movie_id: str, liked: bool):
        """Called when a player swipes right or super-likes. Increment score here."""
        if liked:
            self.scores[movie_id] += 1

    def player_finished_deck(self):
        """Called when a player hits the end of their deck. Increment finished_players count."""
        self.finished_players += 1
        
    def is_game_over(self) -> bool:
        """Returns True if finished_players == total_players."""
        return self.finished_players >= self.total_players

    def get_final_results(self) -> Dict[str, int]:
        """Returns the dictionary of the final scores nicely formatted for the frontend."""
        # most_common() returns a list of tuples sorted by count, so we convert back to dict
        return dict(self.scores.most_common())
