# FilmOnDemand: Task 5 Finalization & Containerization

This document summarizes the FilmOnDemand system, the core research question it addresses, and instructions for running the containerized version as required for the final project submission.

## 1. System Description
**FilmOnDemand** is a comprehensive movie recommendation engine designed to solve the "choice paralysis" often experienced by users when trying to decide what to watch. Unlike generic recommendation systems, FilmOnDemand integrates multiple specialized data sources:
- **Watchmode API**: For real-time streaming availability and provider filtering.
- **TMDb API**: For rich metadata, synopses, and poster art.
- **Trakt API**: For community popularity and trending statistics.
- **OMDb API**: For detailed critical ratings (IMDb, Rotten Tomatoes, Metacritic).
- **TasteDive API**: For finding similar titles based on a user's existing favorites.

The system features a real-time multiplayer "swipe" interface (web-based) and a newly implemented CLI for quick terminal-based lookups.

## 2. Core Research Question
> **"How can we streamline the group movie-selection process by combining real-time streaming availability with multi-platform critical scores and community trends into a unified, interactive decision-making interface?"**

FilmOnDemand answers this by aggregating disparate API data and presenting it through a gamified "swipe" mechanic that ensures the final selection is both highly-rated and actually available to the users on their specific streaming services.

## 3. Design Models
The architecture of FilmOnDemand is built on a modular, multi-layered service pattern. Updated design considerations and implementation guides can be found in the following core documents:
- **[API Refactoring Guide](file:///Users/anish/_A/coding/AISE2251/project/ACCProject/group-project-group10-1/documentation/API_Refactoring_Guide.md)**: Details the normalization layer between various third-party APIs.
- **[GameState Implementation Guide](file:///Users/anish/_A/coding/AISE2251/project/ACCProject/group-project-group10-1/documentation/GameState_Implementation_Guide.md)**: Outlines the real-time synchronization logic for multiplayer sessions.
- **[Host/Filter Guide](file:///Users/anish/_A/coding/AISE2251/project/ACCProject/group-project-group10-1/documentation/Host_Filter_API_Guide.md)**: Describes how user preferences are translated into API queries.

## 4. Container Image (Docker)
The application has been containerized to ensure cross-platform compatibility and ease of deployment. 

### Public Container Image Link
**Image Name:** `FilmOndemand`  
*(Note: Link to public registry like Docker Hub would be provided here once published)*

### How to Run (Local Build)
To build and run the image locally using the provided `Dockerfile`:

1. **Build the image:**
   ```bash
   docker build -t FilmOndemand .
   ```

2. **Run the container (CLI Mode):**
   ```bash
   # Run with mock data (default)
   docker run --rm FilmOndemand --mock

   # Run with live data (requires .env file with API keys)
   docker run --rm --env-file .env FilmOndemand --genres "Action,Sci-Fi" --services "Netflix"
   ```

### CLI Arguments
- `--genres`: Comma-separated list of genres.
- `--services`: Comma-separated list of streaming services.
- `--actors`: Comma-separated list of actor names.
- `--movies`: Comma-separated list of similar movie titles for recommendations.
- `--mock`: Use static mock data instead of live API calls.
