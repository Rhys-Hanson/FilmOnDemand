import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { EntryScreen } from './screens/EntryScreen';
import { SettingsScreen, RoomFilters } from './screens/SettingsScreen';
import { LobbyScreen } from './screens/LobbyScreen';
import { DeckLoadingScreen } from './screens/DeckLoadingScreen';
import { SwipeScreen } from './screens/SwipeScreen';
import { CountdownScreen } from './screens/CountdownScreen';
import { ResultsScreen } from './screens/ResultsScreen';
import { MovieDetailOverlay } from './components/MovieDetailOverlay';
import { Movie } from './data/movies';

export type AppState = 'ENTRY' | 'SETTINGS' | 'LOBBY' | 'LOADING_DECK' | 'SWIPING' | 'COUNTDOWN' | 'RESULTS';

const getOrCreateClientId = () => {
  if (typeof window === 'undefined') return Math.random().toString(36).substring(2, 10);
  let id = localStorage.getItem('FOM_CLIENT_ID');
  if (!id) {
    id = Math.random().toString(36).substring(2, 10);
    localStorage.setItem('FOM_CLIENT_ID', id);
  }
  return id;
};

const CLIENT_ID = getOrCreateClientId();
const hostIP = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
const WS_URL = `ws://${hostIP}:8000/ws/rooms`;
const API_URL = `http://${hostIP}:8000/api/rooms`;

export default function App() {
  const [appState, setAppState] = useState<AppState>('ENTRY');
  const [roomCode, setRoomCode] = useState<string>(() => {
    return typeof window !== 'undefined' ? localStorage.getItem('FOM_ROOM_CODE') || '' : '';
  });
  const [playerCount, setPlayerCount] = useState<number>(1);
  const [isHost, setIsHost] = useState<boolean>(() => {
    return typeof window !== 'undefined' ? localStorage.getItem('FOM_IS_HOST') === 'true' : false;
  });
  const [deck, setDeck] = useState<Movie[]>([]);
  const [deckOffset, setDeckOffset] = useState<number>(0);
  const [lastFilters, setLastFilters] = useState<RoomFilters | null>(null);
  
  const [scores, setScores] = useState<Record<string, number>>({});
  const [superLikes, setSuperLikes] = useState<Record<string, number>>({});
  const [unanimous, setUnanimous] = useState<string[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [disconnectToast, setDisconnectToast] = useState<string | null>(null);

  // Auto-join routing when scanned from QR code
  useEffect(() => {
    const pathSegments = window.location.pathname.split('/');
    if (pathSegments.length >= 3 && pathSegments[1] === 'join') {
      const codeFromUrl = pathSegments[2].toUpperCase();
      if (codeFromUrl && appState === 'ENTRY') {
        handleJoinRoom(codeFromUrl);
        window.history.replaceState({}, '', '/');
      }
    }
  }, []);

  useEffect(() => {
    if (roomCode) {
      localStorage.setItem('FOM_ROOM_CODE', roomCode);
      localStorage.setItem('FOM_IS_HOST', isHost ? 'true' : 'false');
    } else {
      localStorage.removeItem('FOM_ROOM_CODE');
      localStorage.removeItem('FOM_IS_HOST');
    }
  }, [roomCode, isHost]);

  const socketUrl = roomCode ? `${WS_URL}/${roomCode}/${CLIENT_ID}` : null;
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: () => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  const isConnected = readyState === ReadyState.OPEN;
  const isReconnecting = roomCode !== '' && !isConnected;

  useEffect(() => {
    if (lastJsonMessage) {
      const data = lastJsonMessage as any;
      if (data.type === 'player_joined') {
        setPlayerCount(data.count);
      } else if (data.type === 'player_left') {
        setPlayerCount(data.count);
        const remaining = data.count;
        setDisconnectToast(`A player disconnected. ${remaining} player${remaining !== 1 ? 's' : ''} remaining.`);
        setTimeout(() => setDisconnectToast(null), 4000);
      } else if (data.type === 'room_expired') {
        setRoomCode('');
        setAppState('ENTRY');
        localStorage.removeItem('FOM_ROOM_CODE');
        localStorage.removeItem('FOM_IS_HOST');
        alert("This room has expired or the server restarted.");
      } else if (data.type === 'error') {
        alert(data.message || 'Failed to start the movie deck.');
        setAppState(isHost ? 'SETTINGS' : 'LOBBY');
      } else if (data.type === 'game_started') {
        localStorage.setItem('FOM_SWIPE_INDEX', '0');
        setDeck(data.deck);
        setAppState('SWIPING');
      } else if (data.type === 'game_state_sync') {
        if (data.is_new_player) {
          localStorage.setItem('FOM_SWIPE_INDEX', '0');
        }
        setDeck(data.deck);
        setAppState('SWIPING');
      } else if (data.type === 'game_over') {
        setScores(data.scores || {});
        setSuperLikes(data.super_likes || {});
        setUnanimous(data.unanimous || []);
        setAppState('COUNTDOWN');
      }
    }
  }, [lastJsonMessage, isHost]);

  const handleJoinRoom = async (code: string) => {
    try {
      const res = await fetch(`${API_URL}/${code}`);
      if (res.ok) {
        setRoomCode(code);
        setIsHost(false);
        setAppState(code === '000000' ? 'SWIPING' : 'LOBBY');
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
    setDeckOffset(0);
    setLastFilters(filters);
    setAppState('LOADING_DECK');
    localStorage.setItem('FOM_SWIPE_INDEX', '0');
    sendJsonMessage({ action: 'start_game', filters: { ...filters, offset: 0 } });
  };

  const handlePlayerFinished = () => {
    sendJsonMessage({ action: 'player_finished' });
  };

  const handleCountdownFinish = () => {
    setAppState('RESULTS');
  };

  const handleReroll = () => {
    if (lastFilters && deckOffset === 0) {
      const nextOffset = 10;
      setScores({});
      setDeckOffset(nextOffset);
      setAppState('LOADING_DECK');
      localStorage.setItem('FOM_SWIPE_INDEX', '0');
      sendJsonMessage({ action: 'start_game', filters: { ...lastFilters, offset: nextOffset } });
    } else {
      handleAdjustSettings();
    }
  };

  const handleAdjustSettings = () => {
    setScores({});
    setDeckOffset(0);
    localStorage.setItem('FOM_SWIPE_INDEX', '0');
    setAppState(isHost ? 'SETTINGS' : 'LOBBY');
  };

  const handleServerSwipe = (movieId: string, voteType: 'like' | 'dislike' | 'super_like' | 'seen_it') => {
    const actionMap: Record<string, string> = {
      like: 'swipe_right',
      dislike: 'swipe_left',
      super_like: 'super_like',
      seen_it: 'seen_it',
    };
    sendJsonMessage({ action: actionMap[voteType], movie_id: movieId });
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans overflow-hidden selection:bg-rose-500/30">

      {/* Reconnecting banner — appears when WebSocket drops mid-session */}
      <AnimatePresence>
        {isReconnecting && (
          <motion.div
            initial={{ y: -48, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -48, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed top-0 inset-x-0 z-[200] flex items-center justify-center gap-2 bg-amber-500/90 backdrop-blur-md text-black text-sm font-semibold py-2.5 px-4 shadow-lg"
          >
            <motion.span
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ repeat: Infinity, duration: 1.2 }}
              className="w-2 h-2 rounded-full bg-black/50 inline-block"
            />
            Connection lost — reconnecting…
          </motion.div>
        )}
      </AnimatePresence>

      {/* Player-left toast */}
      <AnimatePresence>
        {disconnectToast && (
          <motion.div
            initial={{ y: 80, opacity: 0, scale: 0.95 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 80, opacity: 0, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 300, damping: 28 }}
            className="fixed bottom-28 inset-x-0 z-[200] flex justify-center pointer-events-none"
          >
            <div className="bg-neutral-800/95 backdrop-blur-md border border-neutral-700 text-neutral-200 text-sm font-medium px-4 py-3 rounded-2xl shadow-2xl max-w-sm mx-4 text-center">
              {disconnectToast}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
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
      {appState === 'LOADING_DECK' && (
        <DeckLoadingScreen />
      )}
      {appState === 'SWIPING' && (
        <SwipeScreen 
           roomCode={roomCode}
           movies={deck} 
           onPlayerFinished={handlePlayerFinished} 
           onSwipeServer={handleServerSwipe} 
           onEmptyDeck={handleAdjustSettings}
        />
      )}
      {appState === 'COUNTDOWN' && (
        <CountdownScreen onFinish={handleCountdownFinish} />
      )}
      {appState === 'RESULTS' && (
        <ResultsScreen 
          movies={deck} 
          scores={scores}
          superLikes={superLikes}
          unanimous={unanimous}
          onReroll={handleReroll} 
          onAdjustSettings={handleAdjustSettings}
          canReroll={isHost && deckOffset === 0}
          isHost={isHost}
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
