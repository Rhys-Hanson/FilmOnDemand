# Host Filter Integration Guide

**To the teammates building the Backend APIs:**

The React frontend has been updated to transmit the exact game settings that the Host selects (Genres, Streaming Services, Years, etc.) right before the Swiping game starts. You must use these variables when making your API calls to TMDb/Watchmode, otherwise everyone will swipe on default movies instead of user-selected ones!

## The JSON Payload
When the Host clicks "Start Swiping", the frontend sends a WebSocket message with the `start_game` action. It now firmly includes a `filters` dictionary that behaves exactly like this:

```json
{
  "action": "start_game",
  "filters": {
    "genres": ["Horror", "Action"],
    "services": ["Netflix"],
    "actors": [],
    "yearRange": [1990, 2024]
  }
}
```

## How to extract it inside `main.py`
Inside `server/main.py` (around line 70), in your WebSocket `start_game` listener block, you can extract the host settings cleanly:

```python
elif data["action"] == "start_game":
    
    # 1. Extract the dictionary of filters out of the WebSocket packet
    host_filters = data.get("filters", {})
    
    genres = host_filters.get("genres", [])           # Returns a list of strings
    services = host_filters.get("services", [])       # Returns a list of strings
    years = host_filters.get("yearRange", [1950, 2026]) # Returns a list [start_yr, end_yr]
    
    # 2. Pass these variables into your wrapper (FilmOnDemand) instead of using the mock data
    print(f"Server is fetching {genres} movies from {services} between {years[0]} - {years[1]}...")
    
    # new_deck = FilmOnDemand.search_with_filters(genres=genres, services=services, years=years)
    
    # 3. Broadcast the results to the room like normal
```

By hooking up the backend API code directly to these extracted variables, you will guarantee that the Swiping deck is customized perfectly to the Host's preferences!
