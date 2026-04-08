# FilmOnDemand

**Settle the "what should we watch?" debate before it starts.**

FilmOnDemand is a real-time group movie recommendation platform built for couples, roommates, and friend groups. Instead of endlessly scrolling through streaming apps, users create a shared room, join with a room code or QR code, set their preferences, and vote through a curated deck of instantly watchable movies. When everyone finishes, the app ranks the results by group score so the best pick rises to the top.

## Question of Interest

How can we solve the "what should we watch?" debate for groups and couples by recommending highly-rated movies which match shared tastes, are similar to existing favorites, and are available right now on the streaming services they already own?

## Our Goal

We want to build a data pipeline that takes the frustration out of group movie nights. Instead of scrolling endlessly, the system cross-references the group's favorite films, preferred genres, and streaming services to suggest crowd-pleasing movies. The recommendations are designed to be high quality, culturally relevant, and instantly watchable without extra rental fees. On top of that, FilmOnDemand delivers the experience through a visually polished real-time UI built for fast group decisions.

## What the App Does

- Creates a shared movie room for any number of participants.
- Lets people join instantly using a 6-character game room code or QR code.
- Allows the host to choose streaming services plus recommendation filters such as genres, favorite actors/directors, similar movies, or an AI prompt.
- Builds a recommendation deck using live movie data from multiple APIs.
- Lets each participant vote on every movie in real time.
- Shows movie details and plays the trailer in an embedded player before the group commits.
- Produces a ranked results screen showing what the group wants to watch most.

## How the UI Works

### 1. Create or Join a Room

One person creates a room and becomes the host. Everyone else joins using either:

- the room code
- the QR code shown on the settings screen

### 2. Host Chooses Movie Parameters

The host selects the inputs that shape the recommendation deck:

- streaming services the group already owns
- genres
- a favorite actor or director
- movies to find similar titles to
- an optional AI prompt for more natural-language recommendations

### 3. Everyone Votes on the Deck

Each player swipes through the recommended movies and gives each one a score:

- `Like` = `+1`
- `Dislike` = `-1`
- `Super Like` = `+2`
- `Already seen it / do not want to rewatch` = `-2`

`Super Like` is a one-time power vote per player, so it can only be used once each round.

While voting, users can also:

- open the movie details overlay
- read extra information about the movie
- watch the trailer through the embedded player

### 4. Final Ranked Results

Once every player has finished voting, FilmOnDemand totals the scores and displays the movies in descending order from most wanted to least wanted, making it easy for the group to pick the winner.

## Voting System

FilmOnDemand uses weighted scoring so the final ranking reflects both enthusiasm and resistance:

- Positive group interest pushes a movie upward.
- Strong dislike or "already seen it" feedback pushes it downward.
- Super likes give standout movies a meaningful boost.
- Movies everyone likes can surface as clear crowd favorites.

## Recommendation Pipeline

FilmOnDemand combines several data sources to build better recommendations:

- `TMDb` for movie discovery and metadata
- `Trakt` for popularity and community-driven signals
- `Watchmode` for streaming availability
- `OMDb` for ratings and enrichment data
- `TasteDive` for similarity-based recommendations
- `Gemini` for prompt-based recommendation support

This lets the app recommend movies that are:

- relevant to the group's tastes
- similar to existing favorites
- highly rated
- available on the streaming services the group already pays for

## Tech Stack

- Frontend: `React`, `TypeScript`, `Vite`, `Tailwind CSS`, `motion`
- Backend: `FastAPI`, `Python`, `WebSockets`
- AI + APIs: `Gemini`, `TMDb`, `Trakt`, `Watchmode`, `OMDb`, `TasteDive`

## Project Structure

```text
.
|-- FilmOnDemandAPPUI/filmondemand-app   # React frontend
|-- server                               # FastAPI backend and real-time room logic
|-- FilmOnDemand                         # Movie aggregation pipeline
|-- TMDbAPI
|-- TraktAPI
|-- WatchmodeAPI
|-- OMDbAPI
|-- TasteDiveAPI
|-- documentation
|-- cli.py
|-- .env.example
```

## Team GitHub Accounts

For course and submission context, these school GitHub accounts map to the following personal accounts:

- `rdifeli` = `Rhys-Hanson`
- `ajami558` = `darkprince558`
- `bchyn999` = `beanchyn`
- `VinceJH` = `VinceJH`

## Environment Variables

Copy the root env template before running the backend:

```bash
cp .env.example .env
```

Required keys are documented directly in [`C:\Users\rhysh\OneDrive\Documents\AISE2251B\project\.env.example`](C:\Users\rhysh\OneDrive\Documents\AISE2251B\project\.env.example).

You will need:

- `TASTEDIVE_API_KEY`
- `TMDB_API_KEY`
- `TRAKT_API_KEY`
- `WATCHMODE_API_KEY`
- `OMDB_API_KEY`
- `GEMINI_API_KEY`

## How to Get the API Keys

### TasteDive

1. Create or sign in to your TasteDive account.
2. Request API access at [TasteDive API Access](https://tastedive.com/account/api_access).
3. Copy the API key into `TASTEDIVE_API_KEY`.

### TMDb

1. Create or sign in to your account at [TMDb](https://www.themoviedb.org/).
2. Open [TMDb API Settings](https://www.themoviedb.org/settings/api).
3. Request an API key and copy it into `TMDB_API_KEY`.

### Trakt

1. Create a free account at [Trakt](https://trakt.tv).
2. Go to [Trakt API Applications](https://trakt.tv/oauth/applications).
3. Click `New Application`.
4. Use any app name, such as `FilmOnDemand`.
5. Set the redirect URI to `urn:ietf:wg:oauth:2.0:oob`.
6. Save the application.
7. Copy the generated `Client ID` into `TRAKT_API_KEY`.

### Watchmode

1. Request an API key from [Watchmode API Key Request](https://api.watchmode.com/requestApiKey/).
2. Copy the key into `WATCHMODE_API_KEY`.

### OMDb

1. Request a key at [OMDb API Key Request](https://www.omdbapi.com/apikey.aspx).
2. Copy the key into `OMDB_API_KEY`.

### Gemini

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Create or manage an API key from the Gemini API key area in AI Studio.
4. Copy the key into `GEMINI_API_KEY`.

## Running the Project

### Option 1: One-Command Startup

On Windows:

```powershell
.\RunFOD.bat
```

On macOS/Linux:

```bash
./RunFOD.sh
```

These scripts install dependencies, start the FastAPI backend on port `8000`, and run the React frontend on port `3000`.

### Option 2: Start Everything Manually

Backend:

```powershell
pip install -r requirements.txt
python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd FilmOnDemandAPPUI\filmondemand-app
npm install
npm run dev
```

Then open:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Optional Local Flags

- `USE_MOCK_DATA=false` uses live APIs
- `USE_MOCK_DATA=true` uses mock movie data for testing

## CLI Mode

The repository also includes a CLI for testing the recommendation pipeline without the UI.

By default, it now launches an interactive prompt flow:

```powershell
python cli.py
```

It will ask for:

- streaming services
- whether to recommend by `genres`, `actor/director`, or `similar movies`
- up to `3` genres
- up to `3` similar movies
- up to `1` actor or director

The CLI then prints a polished movie profile for each recommendation, including the same core details shown in the UI such as ratings, streaming services, synopsis, cast, filmmakers, awards, box office, trailer ID, and poster URL.

You can still use flags if you want to skip prompts:

```powershell
python cli.py --genres "Action,Sci-Fi" --services "Netflix,Prime Video"
```

You can also use mock mode:

```powershell
python cli.py --mock
```

## Docker Demo

Build the image:

```powershell
docker build -t filmon-demand .
```

Run the interactive container demo:

```powershell
docker run -it --env-file .env filmon-demand
```

Run with mock data instead of live APIs:

```powershell
docker run -it --env-file .env -e USE_MOCK_DATA=true filmon-demand
```

This container flow is ideal for demonstrating that:

- the image can be built successfully
- dependencies are included in the image
- the container starts correctly
- the app runs properly inside the container
- the recommendation output is clear and presentation-ready

## Why FilmOnDemand Matters

FilmOnDemand is designed to remove friction from group entertainment decisions. It transforms movie night from a long, frustrating search into a fast, collaborative, and fun shared experience.


## Demo Videos

| AI-Powered UI Demo | Parameter Input UI Demo |
|---|---|
| [![AI-Powered UI Demo](docs/Images/FilmOnDemand_Logo.png)](docs/Videos/AI_Powered_UI_Demo.mp4) | [![Parameter Input UI Demo](docs/Images/FilmOnDemand_Logo.png)](docs/Videos/Parameter_Input_UI_Demo.mp4) |
