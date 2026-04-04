# Film On Demand: Full Implementation Plan

## Quick Task Tracker
Use this table to keep track of exactly what has been accomplished, and what your teammates still need to integrate.

| Phase | Component | Assigned To | Status |
|---|---|---|---|
| **Phase 1: Database APIs** | Refactor `TMDbAPI` to return JSON dicts with `posterUrl` / `castList` | Back-End Team | 🔴 Not Started |
| **Phase 1: Database APIs** | Refactor `WatchmodeAPI` to natively return streaming platform info | Back-End Team | 🔴 Not Started |
| **Phase 1: Database APIs** | Update `FilmOnDemand/main.py` wrapper to not use `input()` | Back-End Team | 🔴 Not Started |
| **Phase 2: Game Engine** | Scaffold FastAPI server and Basic Room Manager | Front-End Team | 🟢 Complete |
| **Phase 2: Game Engine** | Implement `GameState` score caching (`server/game_state.py`) | Back-End Team | 🔴 Not Started |
| **Phase 2: Game Engine** | Hook live filter logic to `start_game` WebSocket event | Back-End Team | 🔴 Not Started |
| **Phase 3: React Frontend** | `react-use-websocket` integration & dynamic architecture | Front-End Team | 🟢 Complete |
| **Phase 3: React Frontend** | Dynamic Local Network Wi-Fi routing & QR scanning | Front-End Team | 🟢 Complete |
| **Phase 3: React Frontend** | Host Game Settings/Filter transmission | Front-End Team | 🟢 Complete |
| **Phase 3: React Frontend** | `SwipeScreen` syncing, Wait Screen overlay | Front-End Team | 🟢 Complete |
| **Phase 3: React Frontend** | Build out the final `ResultsScreen.tsx` UI | Front-End Team | 🔴 Not Started |
| **Phase 4: Deployment** | Deploy Python FastAPI server onto Render.com | Whole Team | 🔴 Not Started |
| **Phase 4: Deployment** | Deploy Vite React App onto Vercel / Netlify | Whole Team | 🔴 Not Started |

---


## 1. Executive Summary
**Objective:** Transform the current API wrapper/UI prototype into a full-scale, deployed web application. 
**Core Concept:** A party-game style movie recommendation platform. Users join a "room" via a code (like Kahoot), select their filters, and swipe left/right on movies (like Tinder). When everyone matches on a movie, the group has their winner.

**Current State:**
- The React frontend prototype looks great but runs entirely on local, hard-coded mock data.
- The Python API wrappers (`WatchmodeAPI`, `TMDbAPI`, `TasteDiveAPI`) can successfully fetch external data but only print to the terminal.
- There is no central backend server or database connecting these two pieces.

---

## 2. System Architecture

To achieve the "Kahoot-style" live room functionality, the architecture must support **real-time communication**.

- **Frontend:** React (Vite) + Tailwind CSS + Framer Motion (already built).
- **Backend Framework:** **FastAPI** or **Flask with Flask-SocketIO**. (SocketIO is highly recommended for the real-time Kahoot-style room syncing).
- **In-Memory Store / Database:** **Redis** or a simple in-memory Python dictionary to store active rooms, who is in them, and the current swipe scores.
- **External Data Sources:** Watchmode (Streaming availability), TMDb (Metadata/Posters/Cast), TasteDive (Seed recommendations).

---

## 3. Phase 1: Refactoring the Python APIs (Immediate Next Steps)

Your team's Python APIs were built as terminal scripts. They must be modified to act as data providers for a web server.

### 3.1. Returning Dicts, Not Prints
- **TMDbAPI (`tmdb.py`):** Update the `movie_info()` method to `return` a comprehensive Python dictionary that matches what the React frontend expects, rather than printing lines to the console.
- **Required Metadata:** Ensure `TMDbAPI` is fetching the following fields:
  - `posterUrl` (Full image path)
  - `castList` (Actor name, character name, actor headshot URL)
  - `runtime` and `maturityRating`
  - `youtubeId` (for the trailer)

### 3.2. Unique Identifiers
- **WatchmodeAPI:** When parsing results, return both the movie title **and** its unique ID (like the TMDb ID). Searching TMDb by plain text title is error-prone (e.g., getting the 1989 version of *The Batman* instead of the 2022 version).
- **TasteDiveAPI:** Needs to be integrated into `FilmOnDemand/main.py` so a user can supply a "Seed Movie" to generate the list of titles for the room.

---

## 4. Phase 2: Building the Web Server (The Engine)

You need to build a central backend server to bridge the Python scripts to the React frontend. 

### 4.1. Core Server Setup
- Create an `app.py` in the root directory using Flask and Flask-SocketIO (or FastAPI & WebSockets).
- Import the `FilmOnDemand` object so the server can call the APIs.

### 4.2. REST Endpoints (The Setup)
- `POST /api/rooms/create`: The host creates a room. The server generates a random 6-digit room code (e.g., "X7B9Q2").
  - *QR Code Generation:* The server (or frontend) should generate a QR code linking securely to `https://[your-domain]/join/X7B9Q2`. This allows players to instantly join by scanning the code on the host's screen instead of manually typing the 6 digits.
- `GET /api/rooms/<code_id>`: Check if a room exists before letting a player join via the Entry Screen.

### 4.3. WebSockets / Real-time Events (The Gameplay)
Because this acts like Kahoot, players need to see real-time updates.
1. **Event `join_room`:** Updates the lobby screen for the host to show "X friends joined" in real-time.
2. **Event `start_game`:** The Host hits "Start swiping". The server:
   - Takes the room settings (Genres, Streaming Services, Actors, Year Range).
   - Feeds them instantly to the `FilmOnDemand` API wrapper.
   - Pushes the generated `Movie[]` JSON deck to all connected clients in that room.
3. **Event `swipe_registered`:** When a player swipes right on a movie, the frontend sends a packet to the server. The server increments the score for that movie ID in the room's memory.
4. **Event `match_found`:** If the server detects that the movie score equals the number of players in the room, it emits a `match_found` event to immediately trigger the countdown/winner screen for everyone.

---

## 5. Phase 3: Frontend Integration

The UI components in your React app need to be wired up to the internet.

- **Add Packages:** Run `npm install socket.io-client react-qr-code` in the frontend directory.
- **QR Code Display UI:** Update the `SettingsScreen.tsx` to display the QR code next to the 6-digit room code. This will allow nearby friends to scan the screen with their phone cameras, which will open the app and automatically insert the join code.
- **State Management:** When connecting to the Socket room, replace the `handleJoinRoom` mock transition with actual network logic. Wait for the server's `start_game` event before transitioning from `SettingsScreen` to `SwipeScreen`.
- **Replacing `MOVIE_DATA`:** Remove the hardcoded `movies.ts` mock data. The `<SwipeScreen />` should iterate through the JSON deck received from the backend.

---

## 6. Phase 4: Full Deployment To Production

Once it works locally on your machine, it's time to put it on the internet so anyone can play from their phone.

### 6.1. Hosting the Backend
- Since the backend runs Python and WebSockets, you need a stable host. 
- **Recommendation:** Deploy the Flask/FastAPI app on **Render.com** (easiest for Python/Sockets) or **Heroku**.
- *Requirements:* Ensure you have a `requirements.txt` listing Flask, Flask-SocketIO, requests, and your API wrappers. Make sure your `.env` variables (TMDb, Watchmode api keys) are loaded into the hosting provider's dashboard.

### 6.2. Hosting the Frontend
- The React application is static and highly optimized.
- **Recommendation:** Deploy the `filmondemand-app` folder directly to **Vercel** or **Netlify**.
- *Requirements:* Update all API calls in the React code to point to the live Render.com backend URL (e.g., `https://filmondemand-backend.onrender.com/api`) instead of `localhost:5000`.

### 6.3. Polish
- Test the platform on mobile browsers since swiping feels best on phones.
- Ensure the Kahoot code logic effectively cleans up "dead rooms" from memory after 2 hours so your server doesn't crash.
