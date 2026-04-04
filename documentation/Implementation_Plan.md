# Film On Demand: Full Implementation Plan & Tracker

## 1. Quick Task Tracker
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

## 2. Executive Summary
**Objective:** Transform the current API wrapper/UI prototype into a full-scale, deployed web application. 
**Core Concept:** A party-game style movie recommendation platform. Users join a "room" via a code (like Kahoot), select their filters, and swipe left/right on movies (like Tinder). When everyone matches on a movie, the group has their winner.


---

## 2. System Architecture Reference

To achieve the "Kahoot-style" live room functionality, the architecture supports **real-time communication**.

- **Frontend:** React (Vite) + Tailwind CSS + Framer Motion.
- **Backend Framework:** **FastAPI** + Python WebSockets using Uvicorn.
- **Real-Time State:** Stored entirely in python dictionaries on the server using `GameState` class to count final scores and enforce game limits.
- **External Data Sources:** Watchmode (Streaming availability), TMDb (Metadata/Posters/Cast), TasteDive (Seed recommendations).

---

## 3. Deployment Checklist

Once every task in the Tracker table reads **Complete**, you are ready for Production.

### Hosting the Backend
- Since the backend runs Python and WebSockets, you need a stable host. 
- **Recommendation:** Deploy the FastAPI app on **Render.com** (easiest for Python/Sockets) or **Heroku**.
- *Requirements:* Ensure you have a `requirements.txt` correctly listing `fastapi`, `uvicorn`, `requests`, and your API wrappers. Make sure your `.env` variables (TMDb, Watchmode api keys) are injected into the hosting provider's variables dashboard.

### Hosting the Frontend
- The React application is static and highly optimized.
- **Recommendation:** Deploy the `filmondemand-app` folder directly to **Vercel** or **Netlify**.
- *Requirements:* Update `window.location.hostname` in `App.tsx` to point to the live Render.com backend URL instead of guessing the local Wi-Fi IP address.
