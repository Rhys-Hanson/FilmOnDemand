import React, { useState } from 'react';
import { AnimatePresence } from 'motion/react';
import { EntryScreen } from './screens/EntryScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { SwipeScreen } from './screens/SwipeScreen';
import { CountdownScreen } from './screens/CountdownScreen';
import { ResultsScreen } from './screens/ResultsScreen';
import { MovieDetailOverlay } from './components/MovieDetailOverlay';
import { MOVIE_DATA, Movie } from './data/movies';

export type AppState = 'ENTRY' | 'SETTINGS' | 'SWIPING' | 'COUNTDOWN' | 'RESULTS';

export default function App() {
  const [appState, setAppState] = useState<AppState>('ENTRY');
  const [scores, setScores] = useState<Record<string, number>>({});
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  
  const handleJoinRoom = (code: string) => {
    // In a real app, validate code and connect to websocket
    setAppState('SWIPING');
  };

  const handleCreateRoom = () => {
    setAppState('SETTINGS');
  };

  const handleStartSwiping = () => {
    setAppState('SWIPING');
  };

  const handleFinishSwiping = (finalScores: Record<string, number>) => {
    setScores(finalScores);
    setAppState('COUNTDOWN');
  };

  const handleCountdownFinish = () => {
    setAppState('RESULTS');
  };

  const handleReroll = () => {
    setScores({});
    setAppState('SETTINGS');
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans overflow-hidden selection:bg-rose-500/30">
      {appState === 'ENTRY' && (
        <EntryScreen onJoin={handleJoinRoom} onCreate={handleCreateRoom} />
      )}
      {appState === 'SETTINGS' && (
        <SettingsScreen onStart={handleStartSwiping} />
      )}
      {appState === 'SWIPING' && (
        <SwipeScreen movies={MOVIE_DATA} onFinish={handleFinishSwiping} />
      )}
      {appState === 'COUNTDOWN' && (
        <CountdownScreen onFinish={handleCountdownFinish} />
      )}
      {appState === 'RESULTS' && (
        <ResultsScreen 
          movies={MOVIE_DATA} 
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
