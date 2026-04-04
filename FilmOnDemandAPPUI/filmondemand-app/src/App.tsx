import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'motion/react';
import useWebSocket from 'react-use-websocket';
import { EntryScreen } from './screens/EntryScreen';
import { SettingsScreen, RoomFilters } from './screens/SettingsScreen';
import { LobbyScreen } from './screens/LobbyScreen';
import { SwipeScreen } from './screens/SwipeScreen';
import { CountdownScreen } from './screens/CountdownScreen';
import { ResultsScreen } from './screens/ResultsScreen';
import { MovieDetailOverlay } from './components/MovieDetailOverlay';
import { Movie } from './data/movies';

export type AppState = 'ENTRY' | 'SETTINGS' | 'LOBBY' | 'SWIPING' | 'COUNTDOWN' | 'RESULTS';

// Note: A more robust app might use UUIDs, this gives us a random unique id for the user session
const CLIENT_ID = Math.random().toString(36).substring(2, 10);

// Dynamically resolve the backend URL based on how the user connects to this frontend
const hostIP = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
const WS_URL = `ws://${hostIP}:8000/ws/rooms`;
const API_URL = `http://${hostIP}:8000/api/rooms`;

export default function App() {
  const [appState, setAppState] = useState<AppState>('ENTRY');
  const [roomCode, setRoomCode] = useState<string>('');
  const [playerCount, setPlayerCount] = useState<number>(1);
  const [isHost, setIsHost] = useState<boolean>(false);
  const [deck, setDeck] = useState<Movie[]>([]);
  
  const [scores, setScores] = useState<Record<string, number>>({});
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  // Auto-join routing when scanned from QR code
  useEffect(() => {
    const pathSegments = window.location.pathname.split('/');
    if (pathSegments.length >= 3 && pathSegments[1] === 'join') {
      const codeFromUrl = pathSegments[2].toUpperCase();
      if (codeFromUrl && appState === 'ENTRY') {
        handleJoinRoom(codeFromUrl);
        // Clean up URL so it doesn't look weird
        window.history.replaceState({}, '', '/');
      }
    }
  }, []);

  const socketUrl = roomCode ? `${WS_URL}/${roomCode}/${CLIENT_ID}` : null;
  const { sendJsonMessage, lastJsonMessage } = useWebSocket(socketUrl, {
    shouldReconnect: () => true,
  });

  useEffect(() => {
    if (lastJsonMessage) {
      const data = lastJsonMessage as any;
      if (data.type === 'player_joined') {
        setPlayerCount(data.count);
      } else if (data.type === 'game_started') {
        setDeck(data.deck);
        setAppState('SWIPING');
      } else if (data.type === 'game_over') {
        setScores(data.scores || {});
        setAppState('COUNTDOWN');
      }
    }
  }, [lastJsonMessage]);

  const handleJoinRoom = async (code: string) => {
    try {
      const res = await fetch(`${API_URL}/${code}`);
      if (res.ok) {
        setRoomCode(code);
        setIsHost(false);
        setAppState('LOBBY');
      } else {
        alert("Room not found!");
      }
    } catch (e) {
      alert("Error connecting to server");
    }
  };

  const handleCreateRoom = async () => {
    try {
      const res = await fetch(`${API_URL}/create`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setRoomCode(data.room_code);
        setIsHost(true);
        setAppState('SETTINGS');
      } else {
        alert("Failed to create room");
      }
    } catch (e) {
      alert("Error connecting to server");
    }
  };

  const handleStartSwiping = (filters: RoomFilters) => {
    // Notify the server to start the game with the selected settings
    sendJsonMessage({ action: 'start_game', filters });
    // Note: State changes to SWIPING automatically when the server broadcasts 'game_started'
  };

  const handlePlayerFinished = () => {
    sendJsonMessage({ action: 'player_finished' });
  };

  const handleCountdownFinish = () => {
    setAppState('RESULTS');
  };

  const handleReroll = () => {
    setScores({});
    setAppState(isHost ? 'SETTINGS' : 'LOBBY');
  };

  const handleServerSwipe = (movieId: string, liked: boolean) => {
    if (liked) {
      sendJsonMessage({ action: 'swipe_right', movie_id: movieId });
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans overflow-hidden selection:bg-rose-500/30">
      {appState === 'ENTRY' && (
        <EntryScreen onJoin={handleJoinRoom} onCreate={handleCreateRoom} />
      )}
      {appState === 'LOBBY' && (
        <LobbyScreen roomCode={roomCode} playerCount={playerCount} />
      )}
      {appState === 'SETTINGS' && (
        <SettingsScreen 
          roomCode={roomCode}
          playerCount={playerCount}
          onStart={handleStartSwiping} 
        />
      )}
      {appState === 'SWIPING' && (
        <SwipeScreen 
           movies={deck} 
           onPlayerFinished={handlePlayerFinished} 
           onSwipeServer={handleServerSwipe} 
        />
      )}
      {appState === 'COUNTDOWN' && (
        <CountdownScreen onFinish={handleCountdownFinish} />
      )}
      {appState === 'RESULTS' && (
        <ResultsScreen 
          movies={deck} 
          scores={scores} 
          onReroll={handleReroll} 
          onMovieClick={setSelectedMovie} 
        />
      )}

      <AnimatePresence>
        {selectedMovie && (
          <MovieDetailOverlay 
            movie={selectedMovie} 
            onClose={() => setSelectedMovie(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}
