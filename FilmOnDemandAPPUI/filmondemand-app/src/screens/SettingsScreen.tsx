import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Play, Search, Users, Settings2, Tv, Calendar, Film, Filter } from 'lucide-react';
import QRCode from 'react-qr-code';
import { cn } from '../lib/utils';
import { SearchableChipInput } from '../components/SearchableChipInput';
import { DualRangeSlider } from '../components/DualRangeSlider';

export interface RoomFilters {
  genres: string[];
  services: string[];
  actors: string[];
  movies?: string[];
  yearRange: [number, number];
}

interface SettingsScreenProps {
  roomCode: string;
  playerCount: number;
  onStart: (filters: RoomFilters) => void;
}

const GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Animation', 'Documentary', 'Fantasy'];
const POPULAR_GENRES = ['Action', 'Comedy', 'Horror', 'Romance'];

const STREAMING_SERVICES = ['Netflix', 'Disney+', 'Max', 'Hulu', 'Prime Video', 'Apple TV+', 'Paramount+'];
const POPULAR_SERVICES = ['Netflix', 'Prime Video', 'Max', 'Hulu'];

const ACTORS = ['Timothée Chalamet', 'Zendaya', 'Leonardo DiCaprio', 'Tom Cruise', 'Michelle Yeoh', 'Robert Pattinson', 'Florence Pugh', 'Cillian Murphy', 'Anya Taylor-Joy', 'Oscar Isaac'];

const MOVIES = ['Inception', 'The Dark Knight', 'Interstellar', 'Dune', 'Spider-Man', 'Pulp Fiction', 'The Matrix', 'Avatar', 'Everything Everywhere All at Once', 'Parasite'];

export function SettingsScreen({ roomCode, playerCount, onStart }: SettingsScreenProps) {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [selectedActors, setSelectedActors] = useState<string[]>([]);
  const [selectedMovies, setSelectedMovies] = useState<string[]>([]);
  const [yearRange, setYearRange] = useState<[number, number]>([1990, 2024]);
  const [filterMode, setFilterMode] = useState<'genre' | 'actor' | 'movie'>('genre');

  const handleGenresChange = (newSelection: string[]) => {
    if (newSelection.length <= 3) setSelectedGenres(newSelection);
  };

  const handleActorsChange = (newSelection: string[]) => {
    if (newSelection.length <= 1) setSelectedActors(newSelection);
  };

  const handleMoviesChange = (newSelection: string[]) => {
    if (newSelection.length <= 3) setSelectedMovies(newSelection);
  };

  const hasSelectedParameter = 
    (filterMode === 'genre' && selectedGenres.length > 0) ||
    (filterMode === 'actor' && selectedActors.length > 0) ||
    (filterMode === 'movie' && selectedMovies.length > 0);

  return (
    <div className="min-h-screen bg-neutral-950 p-6 pb-40 overflow-y-auto selection:bg-rose-500/30">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md mx-auto space-y-10"
      >
        {/* Header */}
        <div className="flex items-center justify-between pt-4">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Room Settings</h1>
            <p className="text-neutral-400 mt-1 flex items-center gap-2 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
              {playerCount} {playerCount === 1 ? 'player' : 'players'} joined
            </p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-neutral-900 flex items-center justify-center border border-neutral-800 shadow-inner">
            <Settings2 className="w-6 h-6 text-neutral-400" />
          </div>
        </div>

        {/* Room Code */}
        <div className="glass-dark rounded-[24px] p-6 flex flex-col items-center justify-center border border-white/5 relative overflow-hidden shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-orange-500/5" />
          <div className="bg-white p-3 rounded-2xl mb-4 relative z-10 shadow-lg">
             <QRCode value={`http://${window.location.host}/join/${roomCode}`} size={120} />
          </div>
          <p className="text-neutral-400 text-sm font-semibold uppercase tracking-widest mb-1 relative z-10">Room Code</p>
          <div className="text-4xl font-mono font-black tracking-[0.2em] text-white relative z-10 drop-shadow-md">
            {roomCode}
          </div>
        </div>

        {/* Streaming Services */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold text-lg">
            <Tv className="w-5 h-5 text-rose-400" />
            <h2>Streaming Services</h2>
          </div>
          <SearchableChipInput 
            placeholder="Search providers..." 
            options={STREAMING_SERVICES} 
            selected={selectedServices} 
            onChange={setSelectedServices}
            icon={<Tv className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
            suggestions={POPULAR_SERVICES}
          />
        </div>

        {/* Filter Mode Selector */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold text-lg">
            <Filter className="w-5 h-5 text-rose-400" />
            <h2>Core Filter Strategy</h2>
          </div>
          <div className="flex gap-2 bg-neutral-900 p-1.5 rounded-[16px] border border-white/5">
            <button 
              onClick={() => setFilterMode('genre')} 
              className={cn("flex-1 py-2.5 text-sm rounded-xl font-bold transition-all duration-300", filterMode === 'genre' ? "bg-white/10 text-white shadow-sm" : "text-neutral-500 hover:text-white hover:bg-white/5")}
            >
              Genres
            </button>
            <button 
              onClick={() => setFilterMode('actor')} 
              className={cn("flex-1 py-2.5 text-sm rounded-xl font-bold transition-all duration-300", filterMode === 'actor' ? "bg-white/10 text-white shadow-sm" : "text-neutral-500 hover:text-white hover:bg-white/5")}
            >
              Actor
            </button>
            <button 
              onClick={() => setFilterMode('movie')} 
              className={cn("flex-1 py-2.5 text-sm rounded-xl font-bold transition-all duration-300", filterMode === 'movie' ? "bg-white/10 text-white shadow-sm" : "text-neutral-500 hover:text-white hover:bg-white/5")}
            >
              Movie
            </button>
          </div>
        </div>

        {/* Dynamic Filter Input */}
        {filterMode === 'genre' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center gap-2 text-white font-semibold text-lg">
              <Film className="w-5 h-5 text-rose-400" />
              <h2>Genres (Max 3)</h2>
            </div>
            <SearchableChipInput 
              placeholder="Search genres..." 
              options={GENRES} 
              selected={selectedGenres} 
              onChange={handleGenresChange}
              icon={<Film className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
              suggestions={POPULAR_GENRES}
            />
          </div>
        )}

        {filterMode === 'actor' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center gap-2 text-white font-semibold text-lg">
              <Users className="w-5 h-5 text-rose-400" />
              <h2>Actor & Director (Max 1)</h2>
            </div>
            <SearchableChipInput 
              placeholder="Search talent..." 
              options={ACTORS} 
              selected={selectedActors} 
              onChange={handleActorsChange}
              icon={<Search className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
            />
          </div>
        )}

        {filterMode === 'movie' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center gap-2 text-white font-semibold text-lg">
              <Play className="w-5 h-5 text-rose-400" />
              <h2>Similar Movies (Max 3)</h2>
            </div>
            <SearchableChipInput 
              placeholder="Search movies..." 
              options={MOVIES} 
              selected={selectedMovies} 
              onChange={handleMoviesChange}
              icon={<Search className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
            />
          </div>
        )}

        {/* Year Range */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-white font-semibold text-lg">
            <Calendar className="w-5 h-5 text-rose-400" />
            <h2>Release Year</h2>
          </div>
          <div className="px-2">
            <DualRangeSlider min={1950} max={2026} value={yearRange} onChange={setYearRange} />
          </div>
        </div>

      </motion.div>

      {/* Fixed Bottom Button */}
      <div className="fixed bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-neutral-950 via-neutral-950 to-transparent z-50 pointer-events-none">
        <div className="max-w-md mx-auto pointer-events-auto">
          <motion.button 
            onClick={() => {
              if (hasSelectedParameter) {
                onStart({ 
                  services: selectedServices, 
                  yearRange,
                  genres: filterMode === 'genre' ? selectedGenres : [],
                  actors: filterMode === 'actor' ? selectedActors : [],
                  movies: filterMode === 'movie' ? selectedMovies : []
                });
              }
            }}
            disabled={!hasSelectedParameter}
            whileTap={hasSelectedParameter ? { scale: 0.98 } : {}}
            className={cn(
              "relative w-full overflow-hidden font-bold text-lg rounded-[20px] py-5 flex items-center justify-center gap-2 border group transition-all",
              hasSelectedParameter 
                ? "bg-gradient-to-r from-rose-500 to-orange-500 text-white shadow-[0_8px_32px_rgba(244,63,94,0.3)] border-white/10"
                : "bg-neutral-800 text-neutral-500 border-neutral-700 cursor-not-allowed"
            )}
          >
            {/* Shimmer Effect */}
            {hasSelectedParameter && (
              <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12" />
            )}
            
            <Play className="w-6 h-6 fill-current relative z-10" />
            <span className="relative z-10">Start Swiping</span>
          </motion.button>
        </div>
      </div>
    </div>
  );
}
