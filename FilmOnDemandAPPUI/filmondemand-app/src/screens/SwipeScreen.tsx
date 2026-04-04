import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MovieCard } from '../components/MovieCard';
import { Movie } from '../data/movies';
import { Heart, X, EyeOff, Star } from 'lucide-react';
import { cn } from '../lib/utils';

interface SwipeScreenProps {
  movies: Movie[];
  onPlayerFinished: () => void;
  onSwipeServer: (movieId: string, liked: boolean) => void;
}

export function SwipeScreen({ movies, onPlayerFinished, onSwipeServer }: SwipeScreenProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [superLikesLeft, setSuperLikesLeft] = useState(1);
  const [isWaiting, setIsWaiting] = useState(false);

  const handleSwipe = (direction: 'left' | 'right' | 'up', movie: Movie) => {
    let scoreChange = 0;
    if (direction === 'left') {
       scoreChange = -1;
    }
    if (direction === 'right') {
       scoreChange = 1;
       onSwipeServer(movie.id, true);
    }
    if (direction === 'up') scoreChange = -2;

    setScores(prev => ({
      ...prev,
      [movie.id]: (prev[movie.id] || 0) + scoreChange
    }));

    nextMovie();
  };

  const handleSuperLike = () => {
    if (superLikesLeft > 0 && currentIndex < movies.length) {
      const movie = movies[currentIndex];
      setScores(prev => ({
        ...prev,
        [movie.id]: (prev[movie.id] || 0) + 2
      }));
      setSuperLikesLeft(prev => prev - 1);
      onSwipeServer(movie.id, true);
      nextMovie();
    }
  };

  const nextMovie = () => {
    if (currentIndex < movies.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setIsWaiting(true);
      onPlayerFinished();
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col p-6 overflow-hidden relative">
      {/* Waiting Overlay */}
      <AnimatePresence>
        {isWaiting && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-50 bg-neutral-950/90 backdrop-blur-md flex flex-col items-center justify-center p-6"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              className="text-center space-y-6 max-w-sm"
            >
              <h2 className="text-3xl font-bold tracking-tight text-white">Waiting for others...</h2>
              <p className="text-neutral-400 font-medium">Hang tight! The results will appear automatically as soon as everyone finishes swiping.</p>
              
              <div className="flex items-center justify-center gap-3 mt-8 text-rose-500/80">
                <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1.5 }} className="w-2.5 h-2.5 rounded-full bg-current" />
                <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }} className="w-2.5 h-2.5 rounded-full bg-current" />
                <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }} className="w-2.5 h-2.5 rounded-full bg-current" />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex items-center justify-between mb-6 z-10">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-rose-500/20 flex items-center justify-center border border-rose-500/30">
            <Heart className="w-5 h-5 text-rose-500 fill-rose-500" />
          </div>
          <span className="text-white font-bold">{superLikesLeft} left</span>
        </div>
        <div className="text-neutral-400 font-mono font-medium tracking-widest">
          {currentIndex + 1} / {movies.length}
        </div>
      </div>

      {/* Card Deck */}
      <div className="flex-1 relative w-full max-w-md mx-auto">
        <AnimatePresence>
          {movies.slice(currentIndex, currentIndex + 2).reverse().map((movie, index, array) => {
            const isFront = index === array.length - 1;
            return (
              <motion.div
                key={movie.id}
                initial={{ scale: 0.95, y: 20, opacity: 0 }}
                animate={{ scale: isFront ? 1 : 0.95, y: isFront ? 0 : 20, opacity: 1 }}
                exit={{ scale: 1.05, opacity: 0, transition: { duration: 0.2 } }}
                className="absolute inset-0"
                style={{ zIndex: isFront ? 10 : 0 }}
              >
                <MovieCard 
                  movie={movie} 
                  onSwipe={handleSwipe} 
                  isFront={isFront} 
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center items-center gap-6 mt-8 mb-4 z-10">
        <button 
          onClick={() => handleSwipe('left', movies[currentIndex])}
          className="w-16 h-16 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center text-rose-500 shadow-xl shadow-rose-500/10 hover:bg-neutral-800 active:scale-90 transition-all"
        >
          <X className="w-8 h-8" />
        </button>
        
        <button 
          onClick={handleSuperLike}
          disabled={superLikesLeft === 0}
          className={cn(
            "w-14 h-14 rounded-full flex items-center justify-center shadow-xl transition-all active:scale-90",
            superLikesLeft > 0 
              ? "bg-gradient-to-tr from-rose-500 to-orange-400 text-white shadow-rose-500/30" 
              : "bg-neutral-900 border border-neutral-800 text-neutral-600 opacity-50 cursor-not-allowed"
          )}
        >
          <Star className="w-6 h-6 fill-current" />
        </button>

        <button 
          onClick={() => handleSwipe('right', movies[currentIndex])}
          className="w-16 h-16 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center text-emerald-500 shadow-xl shadow-emerald-500/10 hover:bg-neutral-800 active:scale-90 transition-all"
        >
          <Heart className="w-8 h-8 fill-current" />
        </button>
      </div>
      
      <div className="flex justify-center z-10">
        <button 
          onClick={() => handleSwipe('up', movies[currentIndex])}
          className="text-neutral-500 hover:text-neutral-400 font-medium text-sm flex items-center gap-2 transition-colors"
        >
          <EyeOff className="w-4 h-4" />
          Already seen it
        </button>
      </div>
    </div>
  );
}
