# API Refactoring Guide & Requirements

**To The Team:** 
Our project is moving from terminal-based scripts to a full web application with a React frontend and a real-time web server. To make this work, **your APIs cannot `print()` data to the terminal anymore.** They must return explicitly structured Python dictionaries (`{}`) so the rest of the application can safely bundle the data into JSON and send it to user's phones.

You can refactor your code manually, or you can literally **copy and paste your section below into an AI (Claude/ChatGPT/Gemini)** alongside your current code, and the AI will refactor it perfectly.

---

## 1. Frontend Target Schema (The Goal)
Every movie the backend sends to the frontend must *eventually* look exactly like this JSON object. Keep this in mind when determining what your API needs to return:

```json
{
  "id": "123456",
  "title": "Dune: Part Two",
  "posterUrl": "https://image.tmdb.org/t/p/original/...",
  "description": "Paul Atreides unites with Chani...",
  "castList": [
    { 
      "name": "Timothée Chalamet", 
      "character": "Paul Atreides", 
      "imageUrl": "https://image.tmdb.org/t/p/w185/..."
    }
  ],
  "imdbScore": 8.8,
  "genre": ["Sci-Fi", "Adventure", "Action"],
  "year": 2024,
  "youtubeId": "Way9Dexny3w",
  "maturityRating": "PG-13",
  "runtime": "2h 46m",
  "streamingServices": ["Max"]
}
```

---

## 2. Instructions for the TMDb API Owner
**Current State:** The `movie_info()` script uses prints (e.g., `print("Title: " + title.title)`). 
**Goal:** We need rich metadata to populate the UI. 

### What You Need To Do:
1. **Change the input:** Instead of accepting a plain text string `title`, ideally accept a `tmdb_id` (so we avoid getting the wrong movie with the same name). If your wrapper doesn't support ID search, title search is okay, but ID is vastly preferred.
2. **Change the output:** Instead of printing, return a Python dictionary. 
3. **Fetch new fields:** You need to figure out how to retrieve the movie poster URL, runtime, release year, the maturity rating (e.g., R, PG-13), and headshot image URLs for the top 3-4 cast members.

### Prompt for AI (Copy & Paste this!):
> "Here is my Python script that uses the TMDb API (`tmdb.py`). We are converting this into a web application. I need you to completely remove all `print()` statements from `movie_info()`. Instead, `movie_info()` must return a Python dictionary containing the following keys: `title` (string), `description` (overview string), `posterUrl` (full image URL to the movie poster), `year` (integer release year), `youtubeId` (string ID of the youtube trailer), `runtime` (string formatted like "2h 10m"), `maturityRating` (string like "R" or "PG-13"), and `castList` (a list of dictionaries containing `name`, `character`, and `imageUrl` representing the actor's headshot). Please update the code to reliably fetch these specific fields and return the dictionary."


---

## 3. Instructions for the Watchmode API Owner
**Current State:** `parse_results()` loops through the API response and returns a list containing only the movie `titles`.
**Goal:** Text titles are dangerous because multiple movies have the same title. We need Watchmode to pass along unique IDs so TMDb knows exactly what to look for.

### What You Need To Do:
1. Update `parse_results(self, data)`. 
2. Watchmode's `list-titles` API usually returns a `tmdb_id` or an `imdb_id` alongside the title. Your function should extract this ID.
3. Instead of returning `['The Batman', 'Inception']`, return a list of dictionaries: `[{"title": "The Batman", "tmdb_id": 414906}, {"title": "Inception", "tmdb_id": 27205}]`.

### Prompt for AI (Copy & Paste this!):
> "Here is my Python script handling the Watchmode API. Currently, `parse_results(self, data)` receives the JSON from the Watchmode API and extracts only the title strings into a flat list. I need to change this. Please refactor `parse_results` so that instead of returning a list of strings, it returns a list of dictionaries. Each dictionary should contain the keys `'title'`, `'watchmode_id'`, and crucially `'tmdb_id'` or `'imdb_id'` (whichever the Watchmode API provides in its `list-titles` response). Please ensure that the code gracefully handles movies that might be missing one of those IDs."

---

## 4. Instructions for the TasteDive API Owner
**Current State:** You have a working script that fetches recommendations based on a seed movie and prints them to the terminal.
**Goal:** Like Watchmode, TasteDive needs to output data cleanly so it can be passed down the pipeline.

### What You Need To Do:
1. In `TasteDiveAPI/main.py`, modify it so that instead of printing the recommendations, the method returns a list of the recommended movie titles. 
2. Plug `TasteDiveAPI` actively into `FilmOnDemand/main.py`. The `get_tastedive_movies()` wrapper function is currently empty.

### Prompt for AI (Copy & Paste this!):
> "Here is my `TasteDiveAPI/main.py`. Right now it prints recommendations to the terminal. Please refactor the class to completely remove all print statements. When I call `get_recommendations`, it should silently fetch the API response, parse out only the recommended movie titles, and return them as a standard Python List of strings. Finally, write a tiny snippet showing how I would initialize this class and call this method from a wrapper class called `FilmOnDemand`."

---

## 5. Instructions for the Main Wrapper Owner (`FilmOnDemand/main.py`)
**Current State:** The wrapper relies on hard-coded `input()` calls to get user preferences and prints a dictionary.
**Goal:** The wrapper needs to become a passive engine. It takes input arguments from the web server and returns a fully formed list of movie dictionaries.

### What You Need To Do:
1. **Remove `input()` statements:** Functions like `get_watchmode_movies()` should take parameters (e.g., `def get_watchmode_movies(self, sort_setting, sources_list, genres_list):`) instead of pausing the program to ask `input("Enter Streaming Service(s): ")`. The Web Server will pass these parameters recursively.
2. **Merge the Data:** You are the final boss. You will get a list of IDs from Watchmode, pass them to TMDbAPI, ensure all the dictionaries look *exactly* like the "Frontend Target Schema", and then return the final massive list (`return final_movie_list`).
