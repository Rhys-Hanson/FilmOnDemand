# GameState Class Implementation Guide

**To The Teammate Building the GameState Backend:**

Our objective is to create a robust caching/counter system that governs the rules of the room. It needs to track movie scores, know how many players are in the room, and determine exactly when the game is over so it can broadcast the final results to all players simultaneously.

## 1. File Structure
**Yes, this should be in its own file.** Please create a new file called `server/game_state.py`. Keeping it separate from `main.py` keeps our server clean and object-oriented.

---

## 2. The `GameState` Class Skeleton
Below is the blueprint of what your class needs to accomplish. You don't have to copy this exactly, but it outlines the methods the main server will expect to call.

```python
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
        pass

    def player_finished_deck(self):
        """Called when a player hits the end of their deck. Increment finished_players count."""
        pass
        
    def is_game_over(self) -> bool:
        """Returns True if finished_players == total_players (or if the time limit is elapsed)."""
        pass

    def get_final_results(self) -> Dict[str, int]:
        """Returns the dictionary of the final scores nicely formatted for the frontend."""
        pass
```

---

## 3. Integrating with `main.py`

When you finish building the class, you will need to update `server/main.py` to use it.

1. **Import it:** `from .game_state import GameState`
2. **Initialize it:** Inside the `start_game` WebSocket event, figure out how many players are currently connected (`len(manager.rooms[room_code])`), and create the `GameState` object. Save it to `active_rooms[room_code]["game_state"]`.
3. **Register Swipes:** Update the `swipe_right` listener to call `active_rooms[room_code]["game_state"].register_swipe(...)`.
4. **Listen for 'player_finished':** Add a new `elif data["action"] == "player_finished":` block. Inside, call your `player_finished_deck()` method. Then check your `is_game_over()` method. If it returns `True`, broadcast a `{"type": "game_over", "scores": ...}` message to the room!
