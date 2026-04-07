import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'motion/react';
import { Play, Search, Users, Sparkles, Tv, Film, Filter } from 'lucide-react';
import QRCode from 'react-qr-code';
import { cn } from '../lib/utils';
import { SearchableChipInput } from '../components/SearchableChipInput';

export interface RoomFilters {
  genres: string[];
  services: string[];
  actors: string[];
  movies?: string[];
  ai_prompt?: string;
}

interface SettingsScreenProps {
  roomCode: string;
  playerCount: number;
  onStart: (filters: RoomFilters) => void;
}

const FALLBACK_GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Animation', 'Documentary', 'Fantasy'];
const POPULAR_GENRES = ['Action', 'Comedy', 'Horror', 'Romance'];

const POPULAR_SERVICES = ['Netflix', 'Prime Video', 'Max', 'Hulu'];

const ACTORS = ['Timothée Chalamet', 'Zendaya', 'Leonardo DiCaprio', 'Tom Cruise', 'Michelle Yeoh', 'Robert Pattinson', 'Florence Pugh', 'Cillian Murphy', 'Anya Taylor-Joy', 'Oscar Isaac'];

const MOVIES = ['Inception', 'The Dark Knight', 'Interstellar', 'Dune', 'Spider-Man', 'Pulp Fiction', 'The Matrix', 'Avatar', 'Everything Everywhere All at Once', 'Parasite'];
const hostIP = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
const API_BASE_URL = `http://${hostIP}:8000/api`;

export function SettingsScreen({ roomCode, playerCount, onStart }: SettingsScreenProps) {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [selectedActors, setSelectedActors] = useState<string[]>([]);
  const [selectedMovies, setSelectedMovies] = useState<string[]>([]);
  const [filterMode, setFilterMode] = useState<'genre' | 'actor' | 'movie'>('genre');
  const [isAiMode, setIsAiMode] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiInputStrategy, setAiInputStrategy] = useState<'parameters' | 'text'>('text');
  const [genreOptions, setGenreOptions] = useState<string[]>(FALLBACK_GENRES);
  const [serviceOptions, setServiceOptions] = useState<string[]>([]);
  const [actorOptions, setActorOptions] = useState<string[]>([]);
  const [isActorSearchLoading, setIsActorSearchLoading] = useState(false);
  const [movieOptions, setMovieOptions] = useState<string[]>(MOVIES);
  const [isMovieSearchLoading, setIsMovieSearchLoading] = useState(false);

  const handleGenresChange = (newSelection: string[]) => {
    if (isAiMode || newSelection.length <= 3) setSelectedGenres(newSelection);
  };

  const handleActorsChange = (newSelection: string[]) => {
    if (isAiMode || newSelection.length <= 1) setSelectedActors(newSelection);
  };

  const handleMoviesChange = (newSelection: string[]) => {
    if (isAiMode || newSelection.length <= 3) setSelectedMovies(newSelection);
  };

  const hasSelectedParameter = isAiMode 
    ? (aiInputStrategy === 'text' ? aiPrompt.trim().length > 0 : (selectedGenres.length > 0 || selectedActors.length > 0 || selectedMovies.length > 0))
    : (filterMode === 'genre' && selectedGenres.length > 0) ||
      (filterMode === 'actor' && selectedActors.length > 0) ||
      (filterMode === 'movie' && selectedMovies.length > 0);

  useEffect(() => {
    let cancelled = false;

    const loadFilterData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/options/filter-data`);
        if (!response.ok) {
          throw new Error('Failed to fetch filter data');
        }

        const data = await response.json();
        if (!cancelled) {
          setGenreOptions(Array.isArray(data.genres) ? data.genres : FALLBACK_GENRES);
          setServiceOptions(Array.isArray(data.services) ? data.services : []);
        }
      } catch {
        if (!cancelled) {
          setGenreOptions(FALLBACK_GENRES);
          setServiceOptions(POPULAR_SERVICES);
        }
      }
    };

    loadFilterData();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleActorQueryChange = async (query: string) => {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < 2) {
      setActorOptions([]);
      setIsActorSearchLoading(false);
      return;
    }

    setIsActorSearchLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/options/actors?q=${encodeURIComponent(trimmedQuery)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch actor suggestions');
      }

      const data = await response.json();
      setActorOptions(Array.isArray(data.actors) ? data.actors : []);
    } catch {
      setActorOptions([]);
    } finally {
      setIsActorSearchLoading(false);
    }
  };

  const handleMovieQueryChange = async (query: string) => {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < 2) {
      setMovieOptions(MOVIES);
      setIsMovieSearchLoading(false);
      return;
    }

    setIsMovieSearchLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/options/movies?q=${encodeURIComponent(trimmedQuery)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch movie suggestions');
      }

      const data = await response.json();
      setMovieOptions(Array.isArray(data.movies) && data.movies.length > 0 ? data.movies : MOVIES);
    } catch {
      setMovieOptions(MOVIES);
    } finally {
      setIsMovieSearchLoading(false);
    }
  };

  const popularGenreSuggestions = useMemo(() => {
    const availableGenres = new Set(genreOptions);
    return POPULAR_GENRES.filter((genre) => availableGenres.has(genre));
  }, [genreOptions]);

  const popularServiceSuggestions = useMemo(() => {
    const availableServices = new Set(serviceOptions);
    return POPULAR_SERVICES.filter((service) => availableServices.has(service));
  }, [serviceOptions]);

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
          <button 
            onClick={() => setIsAiMode(!isAiMode)}
            className={cn(
              "w-12 h-12 rounded-2xl flex items-center justify-center border shadow-inner transition-all duration-300 relative group",
              isAiMode 
                ? "bg-rose-500/20 border-rose-500/50 shadow-[0_0_20px_rgba(244,63,94,0.15)]" 
                : "bg-neutral-900 border-neutral-800 hover:border-neutral-700"
            )}
          >
            {isAiMode && (
              <motion.div 
                layoutId="ai-glow"
                className="absolute inset-0 rounded-2xl bg-rose-500/10 blur-xl px-4"
                animate={{ opacity: [0.5, 0.8, 0.5] }}
                transition={{ repeat: Infinity, duration: 2 }}
              />
            )}
            <Sparkles className={cn("w-6 h-6 transition-all relative z-10", isAiMode ? "text-rose-400 scale-110 drop-shadow-[0_0_8px_rgba(251,113,133,0.5)]" : "text-neutral-400 group-hover:text-neutral-300")} />
          </button>
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
            options={serviceOptions} 
            selected={selectedServices} 
            onChange={setSelectedServices}
            icon={<Tv className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
            suggestions={popularServiceSuggestions}
          />
        </div>

        {/* AI Input Strategy Selector (Always pinned here in AI Mode) */}
        {isAiMode && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center gap-2 text-white font-semibold text-lg">
              <span className="text-xl">✨</span>
              <h2>AI Input Strategy</h2>
            </div>
            
            <div className="flex gap-2 bg-neutral-900 p-1.5 rounded-[16px] border border-white/5">
              <button 
                onClick={() => setAiInputStrategy('text')}
                className={cn("flex-1 py-2.5 text-sm rounded-xl font-bold transition-all duration-300", aiInputStrategy === 'text' ? "bg-white/10 text-white shadow-sm" : "text-neutral-500 hover:text-white hover:bg-white/5")}
              >
                Custom Prompt
              </button>
              <button 
                onClick={() => setAiInputStrategy('parameters')}
                className={cn("flex-1 py-2.5 text-sm rounded-xl font-bold transition-all duration-300", aiInputStrategy === 'parameters' ? "bg-white/10 text-white shadow-sm" : "text-neutral-500 hover:text-white hover:bg-white/5")}
              >
                Use Parameters
              </button>
            </div>

            {aiInputStrategy === 'text' && (
              <textarea
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Describe the movies you want to watch... e.g. 'Sci-fi movies about time travel but not Interstellar'"
                className="w-full h-32 mt-4 bg-neutral-900 border border-white/10 rounded-2xl p-4 text-white placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-rose-500/50 resize-none animate-in fade-in zoom-in-95 duration-200"
              />
            )}
          </div>
        )}

        {/* Core Filters / Parameters Section */}
        {(!isAiMode || aiInputStrategy === 'parameters') && (
          <div className="space-y-8">
            {!isAiMode && (
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
            )}

            {/* Dynamic Filter Inputs */}
            {((!isAiMode && filterMode === 'genre') || (isAiMode && aiInputStrategy === 'parameters')) && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center gap-2 text-white font-semibold text-lg">
                  <Film className="w-5 h-5 text-rose-400" />
                  <h2>Genres {isAiMode ? "(No Limit)" : "(Max 3)"}</h2>
                </div>
                <SearchableChipInput 
                  placeholder="Search genres..." 
                  options={genreOptions} 
                  selected={selectedGenres} 
                  onChange={handleGenresChange}
                  icon={<Film className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
                  suggestions={popularGenreSuggestions}
                />
              </div>
            )}

            {((!isAiMode && filterMode === 'actor') || (isAiMode && aiInputStrategy === 'parameters')) && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center gap-2 text-white font-semibold text-lg">
                  <Users className="w-5 h-5 text-rose-400" />
                  <h2>Actor & Director {isAiMode ? "(No Limit)" : "(Max 1)"}</h2>
                </div>
                <SearchableChipInput 
                  placeholder="Search talent..." 
                  options={actorOptions} 
                  selected={selectedActors} 
                  onChange={handleActorsChange}
                  onQueryChange={handleActorQueryChange}
                  loading={isActorSearchLoading}
                  icon={<Search className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
                />
              </div>
            )}

            {((!isAiMode && filterMode === 'movie') || (isAiMode && aiInputStrategy === 'parameters')) && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center gap-2 text-white font-semibold text-lg">
                  <Play className="w-5 h-5 text-rose-400" />
                  <h2>Similar Movies {isAiMode ? "(No Limit)" : "(Max 3)"}</h2>
                </div>
                <SearchableChipInput 
                  placeholder="Search movies..." 
                  options={movieOptions} 
                  selected={selectedMovies} 
                  onChange={handleMoviesChange}
                  onQueryChange={handleMovieQueryChange}
                  loading={isMovieSearchLoading}
                  icon={<Search className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
                />
              </div>
            )}
          </div>
        )}

      </motion.div>

      {/* Fixed Bottom Button */}
      <div className="fixed bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-neutral-950 via-neutral-950 to-transparent z-[100] pointer-events-none">
        <div className="max-w-md mx-auto pointer-events-auto">
          <motion.button 
            onClick={() => {
              if (hasSelectedParameter) {
                let computedAiPrompt = undefined;
                if (isAiMode) {
                  if (aiInputStrategy === 'text') {
                    computedAiPrompt = aiPrompt.trim();
                  } else {
                    const conditions = [];
                    if (selectedGenres.length > 0) conditions.push(`Genres: ${selectedGenres.join(", ")}`);
                    if (selectedActors.length > 0) conditions.push(`Actors/Directors: ${selectedActors.join(", ")}`);
                    if (selectedMovies.length > 0) conditions.push(`Similar to: ${selectedMovies.join(", ")}`);
                    computedAiPrompt = `Recommend movies with the following parameters: ${conditions.join(" | ")}. Please consider all provided conditions together.`;
                  }
                }

                onStart({ 
                  services: selectedServices, 
                  genres: (!isAiMode && filterMode === 'genre') ? selectedGenres : [],
                  actors: (!isAiMode && filterMode === 'actor') ? selectedActors : [],
                  movies: (!isAiMode && filterMode === 'movie') ? selectedMovies : [],
                  ai_prompt: computedAiPrompt
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
