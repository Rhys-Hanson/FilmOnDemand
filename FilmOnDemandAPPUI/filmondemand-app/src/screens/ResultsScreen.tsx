import React, { useEffect } from 'react';
import { motion } from 'motion/react';
import confetti from 'canvas-confetti';
import { Movie } from '../data/movies';
import { RotateCcw, Trophy, Star, Heart } from 'lucide-react';
import { cn } from '../lib/utils';

interface ResultsScreenProps {
  movies: Movie[];
  scores: Record<string, number>;
  superLikes: Record<string, number>;
  unanimous: string[];
  onReroll: () => void;
  onMovieClick: (movie: Movie) => void;
}

export function ResultsScreen({ movies, scores, superLikes, unanimous, onReroll, onMovieClick }: ResultsScreenProps) {
  // Sort movies by score descending
  const sortedMovies = [...movies].sort((a, b) => {
    const scoreA = scores[a.id] || 0;
    const scoreB = scores[b.id] || 0;
    return scoreB - scoreA;
  });

  // Find the movie with the most super likes (if any were cast)
  const mostSuperLikedId = Object.keys(superLikes).length > 0
    ? Object.entries(superLikes).reduce((best, [id, count]) =>
        count > (superLikes[best] || 0) ? id : best
      , Object.keys(superLikes)[0])
    : null;

  const top3 = sortedMovies.slice(0, 3);
  const others = sortedMovies.slice(3, 10);

  useEffect(() => {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    const randomInRange = (min: number, max: number) => Math.random() * (max - min) + min;

    const interval: any = setInterval(function() {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);
      confetti({
        ...defaults, particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      });
      confetti({
        ...defaults, particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      });
    }, 250);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 p-6 pb-32 overflow-y-auto">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-12 pt-8">
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-rose-500 to-orange-400 drop-shadow-md mb-2">
            The Results Are In!
          </h1>
          <p className="text-neutral-400">Here's what the group wants to watch.</p>
        </div>

        {/* Podium */}
        <div className="flex items-end justify-center gap-2 mb-16 min-h-[400px]">
          {/* 2nd Place */}
          {top3[1] && (
            <motion.div 
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5, type: 'spring' }}
              className="flex flex-col items-center w-1/3 cursor-pointer group"
              onClick={() => onMovieClick(top3[1])}
            >
              {/* Badge Area Above Poster */}
              <div className="flex flex-col items-center gap-1 mb-2 min-h-[32px] justify-end">
                {mostSuperLikedId === top3[1].id && (
                  <div className="bg-gradient-to-r from-amber-400 to-rose-500 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Star className="w-2.5 h-2.5 text-white fill-white" />
                    <span className="text-white text-[9px] font-black uppercase tracking-tighter">Super Liked</span>
                  </div>
                )}
                {unanimous.includes(top3[1].id) && (
                  <div className="bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Heart className="w-2.5 h-2.5 text-white fill-white" />
                    <span className="text-white text-[9px] font-black uppercase tracking-tighter">Everyone Liked</span>
                  </div>
                )}
              </div>

              <div className="relative w-full aspect-[2/3] rounded-xl overflow-hidden mb-4 shadow-lg shadow-neutral-900 group-hover:ring-2 group-hover:ring-white/50 transition-all">
                <img src={top3[1].posterUrl} alt={top3[1].title} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end justify-center pb-2">
                  <span className="text-white font-bold text-sm text-center px-1 leading-tight">{top3[1].title}</span>
                </div>
              </div>
              <div className="w-full h-24 bg-gradient-to-t from-neutral-800 to-neutral-700 rounded-t-xl flex items-center justify-center border-t-4 border-neutral-400 relative">
                <span className="text-4xl font-black text-neutral-500">2</span>
                <div className="absolute -top-3 bg-neutral-800 px-3 py-1 rounded-full text-xs font-bold text-neutral-300 border border-neutral-700">
                  {scores[top3[1].id] || 0} pts
                </div>
              </div>
            </motion.div>
          )}

          {/* 1st Place */}
          {top3[0] && (
            <motion.div 
              initial={{ y: 150, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1, type: 'spring', bounce: 0.5 }}
              className="flex flex-col items-center w-1/3 z-10 cursor-pointer group"
              onClick={() => onMovieClick(top3[0])}
            >
              {/* Badge Area Above Poster */}
              <div className="flex flex-col items-center gap-1 mb-2 min-h-[44px] justify-end relative w-full">
                {mostSuperLikedId === top3[0].id && (
                  <div className="bg-gradient-to-r from-amber-400 to-rose-500 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Star className="w-3 h-3 text-white fill-white" />
                    <span className="text-white text-[10px] font-black uppercase tracking-tighter">Super Liked</span>
                  </div>
                )}
                {unanimous.includes(top3[0].id) && (
                  <div className="bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Heart className="w-3 h-3 text-white fill-white" />
                    <span className="text-white text-[10px] font-black uppercase tracking-tighter">Everyone Liked</span>
                  </div>
                )}
              </div>

              <div className="relative w-full aspect-[2/3] rounded-xl overflow-hidden mb-4 shadow-2xl shadow-rose-500/20 ring-4 ring-rose-500 group-hover:ring-rose-400 transition-all">
                <img src={top3[0].posterUrl} alt={top3[0].title} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end justify-center pb-2">
                  <span className="text-white font-bold text-sm text-center px-1 leading-tight">{top3[0].title}</span>
                </div>
                <div className="absolute top-2 right-2 bg-rose-500 rounded-full p-1.5 shadow-lg shadow-rose-950/50 ring-2 ring-rose-400/50">
                  <Trophy className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="w-full h-32 bg-gradient-to-t from-rose-900 to-rose-600 rounded-t-xl flex items-center justify-center border-t-4 border-rose-400 relative shadow-[0_0_30px_rgba(244,63,94,0.3)]">
                <span className="text-5xl font-black text-rose-200">1</span>
                <div className="absolute -top-3 bg-rose-500 px-3 py-1 rounded-full text-xs font-bold text-white shadow-lg">
                  {scores[top3[0].id] || 0} pts
                </div>
              </div>
            </motion.div>
          )}

          {/* 3rd Place */}
          {top3[2] && (
            <motion.div 
              initial={{ y: 80, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="flex flex-col items-center w-1/3 cursor-pointer group"
              onClick={() => onMovieClick(top3[2])}
            >
              {/* Badge Area Above Poster */}
              <div className="flex flex-col items-center gap-1 mb-2 min-h-[32px] justify-end">
                {mostSuperLikedId === top3[2].id && (
                  <div className="bg-gradient-to-r from-amber-400 to-rose-500 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Star className="w-2.5 h-2.5 text-white fill-white" />
                    <span className="text-white text-[9px] font-black uppercase tracking-tighter">Super Liked</span>
                  </div>
                )}
                {unanimous.includes(top3[2].id) && (
                  <div className="bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full px-2 py-0.5 flex items-center gap-1 shadow-lg">
                    <Heart className="w-2.5 h-2.5 text-white fill-white" />
                    <span className="text-white text-[9px] font-black uppercase tracking-tighter">Everyone Liked</span>
                  </div>
                )}
              </div>

              <div className="relative w-full aspect-[2/3] rounded-xl overflow-hidden mb-4 shadow-lg shadow-neutral-900 group-hover:ring-2 group-hover:ring-white/50 transition-all">
                <img src={top3[2].posterUrl} alt={top3[2].title} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end justify-center pb-2">
                  <span className="text-white font-bold text-sm text-center px-1 leading-tight">{top3[2].title}</span>
                </div>
              </div>
              <div className="w-full h-20 bg-gradient-to-t from-neutral-900 to-neutral-800 rounded-t-xl flex items-center justify-center border-t-4 border-amber-700/50 relative">
                <span className="text-3xl font-black text-neutral-600">3</span>
                <div className="absolute -top-3 bg-neutral-800 px-3 py-1 rounded-full text-xs font-bold text-neutral-400 border border-neutral-700">
                  {scores[top3[2].id] || 0} pts
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Honorable Mentions */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="space-y-4"
        >
          <h3 className="text-neutral-500 font-semibold uppercase tracking-wider text-sm mb-4">Honorable Mentions</h3>
          {others.map((movie, index) => (
            <div 
              key={movie.id} 
              onClick={() => onMovieClick(movie)}
              className="flex items-center gap-4 bg-neutral-900/50 p-3 rounded-2xl border border-neutral-800/50 cursor-pointer hover:bg-neutral-800/80 transition-colors"
            >
              <span className="text-neutral-500 font-mono font-bold w-6 text-center">{index + 4}</span>
              <img src={movie.posterUrl} alt={movie.title} className="w-12 h-16 rounded-lg object-cover" referrerPolicy="no-referrer" />
              <div className="flex-1">
                <h4 className="text-white font-medium line-clamp-1">{movie.title}</h4>
                <p className="text-neutral-400 text-sm">{movie.year}</p>
                {mostSuperLikedId === movie.id && (
                  <div className="flex items-center gap-1 mt-1">
                    <div className="flex items-center gap-1 bg-gradient-to-r from-amber-500/20 to-rose-500/20 border border-amber-500/30 rounded-full px-2 py-0.5">
                      <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                      <span className="text-amber-300 text-[10px] font-bold">Most Super Liked</span>
                    </div>
                  </div>
                )}
                {unanimous.includes(movie.id) && (
                  <div className="flex items-center gap-1 mt-1">
                    <div className="flex items-center gap-1 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 rounded-full px-2 py-0.5">
                      <Heart className="w-3 h-3 text-emerald-400 fill-emerald-400" />
                      <span className="text-emerald-300 text-[10px] font-bold">Everyone Liked This</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="bg-neutral-800 px-3 py-1 rounded-full text-sm font-medium text-neutral-300">
                {scores[movie.id] || 0} pts
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Fixed Bottom Button */}
      <motion.div 
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ delay: 2, type: 'spring' }}
        className="fixed bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-neutral-950 via-neutral-950 to-transparent z-50 pointer-events-none"
      >
        <button 
          onClick={onReroll}
          className="w-full max-w-md mx-auto bg-neutral-800 hover:bg-neutral-700 text-white font-bold text-lg rounded-2xl py-5 flex items-center justify-center gap-2 shadow-xl border border-neutral-700 transition-all active:scale-[0.98] pointer-events-auto"
        >
          <RotateCcw className="w-6 h-6" />
          Reroll Recommendations
        </button>
      </motion.div>
    </div>
  );
}
