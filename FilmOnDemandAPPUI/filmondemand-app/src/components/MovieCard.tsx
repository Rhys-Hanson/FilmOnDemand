import React, { useState } from 'react';
import { motion, useMotionValue, useTransform, useAnimation, PanInfo, AnimatePresence } from 'motion/react';
import { Movie } from '../data/movies';
import { Info, Star, Heart, X, EyeOff } from 'lucide-react';
import { cn } from '../lib/utils';
import { MovieDetailOverlay } from './MovieDetailOverlay';

interface MovieCardProps {
  movie: Movie;
  onSwipe: (direction: 'left' | 'right' | 'up', movie: Movie) => void;
  isFront: boolean;
}

export function MovieCard({ movie, onSwipe, isFront }: MovieCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const controls = useAnimation();

  // Rotate based on x position
  const rotate = useTransform(x, [-200, 200], [-15, 15]);
  
  // Opacity for overlays
  const nopeOpacity = useTransform(x, [-50, -150], [0, 1]);
  const likeOpacity = useTransform(x, [50, 150], [0, 1]);
  const seenOpacity = useTransform(y, [-50, -150], [0, 1]);

  const handleDragEnd = async (e: any, info: PanInfo) => {
    // Prevent swipe if details are open
    if (showDetails) return;

    const threshold = 100;
    const velocity = info.velocity;

    if (info.offset.x > threshold || velocity.x > 500) {
      await controls.start({ x: 500, transition: { duration: 0.3 } });
      onSwipe('right', movie);
    } else if (info.offset.x < -threshold || velocity.x < -500) {
      await controls.start({ x: -500, transition: { duration: 0.3 } });
      onSwipe('left', movie);
    } else if (info.offset.y < -threshold || velocity.y < -500) {
      await controls.start({ y: -500, transition: { duration: 0.3 } });
      onSwipe('up', movie);
    } else {
      controls.start({ x: 0, y: 0, transition: { type: 'spring', stiffness: 300, damping: 20 } });
    }
  };

  return (
    <>
      <motion.div
        className="absolute inset-0 w-full h-full rounded-[32px] overflow-hidden shadow-2xl bg-neutral-900"
        style={{
          x,
          y,
          rotate,
          zIndex: isFront ? 10 : 0,
        }}
        drag={isFront && !showDetails ? true : false}
        dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
        onDragEnd={handleDragEnd}
        animate={controls}
        whileTap={{ scale: 0.98 }}
      >
        {/* Poster Image */}
        <img 
          src={movie.posterUrl} 
          alt={movie.title}
          className="w-full h-full object-cover pointer-events-none"
          referrerPolicy="no-referrer"
        />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent pointer-events-none" />

        {/* Overlays (NOPE, LIKE, SEEN IT) */}
        <motion.div style={{ opacity: nopeOpacity }} className="absolute top-12 right-8 border-4 border-rose-500 text-rose-500 text-4xl font-black px-4 py-2 rounded-xl rotate-12 pointer-events-none">
          NOPE
        </motion.div>
        <motion.div style={{ opacity: likeOpacity }} className="absolute top-12 left-8 border-4 border-emerald-500 text-emerald-500 text-4xl font-black px-4 py-2 rounded-xl -rotate-12 pointer-events-none">
          LIKE
        </motion.div>
        <motion.div style={{ opacity: seenOpacity }} className="absolute bottom-32 left-1/2 -translate-x-1/2 border-4 border-blue-500 text-blue-500 text-4xl font-black px-4 py-2 rounded-xl pointer-events-none">
          SEEN IT
        </motion.div>

        {/* Info Content */}
        <div className="absolute bottom-0 left-0 right-0 p-6 flex flex-col gap-2">
          <div className="flex items-end justify-between">
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-white drop-shadow-md">{movie.title}</h2>
              <p className="text-neutral-300 font-medium">{movie.year} • {movie.genre.join(', ')}</p>
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setShowDetails(true);
              }}
              className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white border border-white/30 active:scale-95 transition-transform"
            >
              <Info className="w-5 h-5" />
            </button>
          </div>
        </div>
      </motion.div>

      <AnimatePresence>
        {showDetails && (
          <MovieDetailOverlay 
            movie={movie} 
            onClose={() => setShowDetails(false)} 
          />
        )}
      </AnimatePresence>
    </>
  );
}
