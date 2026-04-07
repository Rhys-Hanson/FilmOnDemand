import React from 'react';
import { motion, PanInfo } from 'motion/react';
import { Movie } from '../data/movies';
import { ArrowLeft, Clock, Calendar, Film, Trophy, DollarSign, Clapperboard, PenLine } from 'lucide-react';

interface MovieDetailOverlayProps {
  movie: Movie;
  onClose: () => void;
}

export function MovieDetailOverlay({ movie, onClose }: MovieDetailOverlayProps) {
  const handleDragEnd = (e: any, info: PanInfo) => {
    // Dismiss if swiped down significantly
    if (info.offset.y > 100 || info.velocity.y > 500) {
      onClose();
    }
  };

  return (
    <motion.div
      initial={{ y: '100%', opacity: 0 }}
      animate={{ y: '0%', opacity: 1 }}
      exit={{ y: '100%', opacity: 0 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      drag="y"
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={{ top: 0, bottom: 1 }}
      onDragEnd={handleDragEnd}
      className="fixed inset-0 z-[100] flex flex-col bg-neutral-950/80 backdrop-blur-2xl overflow-hidden"
    >
      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto pb-24">
        {/* Header Trailer Section */}
        <div className="relative w-full aspect-video bg-black">
          {/* Back Button */}
          <button
            onClick={onClose}
            className="absolute top-6 left-4 z-10 w-10 h-10 rounded-full bg-black/40 backdrop-blur-md flex items-center justify-center text-white border border-white/20 active:scale-95 transition-transform"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          {/* YouTube Embed Placeholder */}
          <iframe
            className="w-full h-full"
            src={`https://www.youtube.com/embed/${movie.youtubeId}?autoplay=0&controls=1&rel=0`}
            title={`${movie.title} Trailer`}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>

        {/* Content Container */}
        <div className="px-6 py-8 space-y-8">
          {/* Title Card & Hero Assets */}
          <div className="flex gap-6">
            <div className="w-1/3 shrink-0">
              <img
                src={movie.posterUrl}
                alt={movie.title}
                className="w-full aspect-[2/3] object-cover rounded-2xl shadow-2xl shadow-black/50 border border-white/10"
                referrerPolicy="no-referrer"
              />
            </div>
            <div className="flex-1 flex flex-col justify-center">
              <h1 className="text-3xl font-black text-white leading-tight mb-4">
                {movie.title}
              </h1>
              
              {/* Metadata Row */}
              <div className="flex flex-wrap gap-y-2 gap-x-4 text-sm font-medium text-neutral-400">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  {movie.year}
                </div>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4" />
                  {movie.runtime}
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-neutral-800 border border-neutral-700 text-xs font-bold text-neutral-300">
                    {movie.maturityRating}
                  </span>
                </div>
              </div>
              
              <div className="mt-3 flex flex-wrap gap-2">
                {movie.genre.map(g => (
                  <span key={g} className="px-2.5 py-1 rounded-full bg-white/10 text-xs font-medium text-neutral-300">
                    {g}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* The Hook (Ratings) */}
          <div className="grid grid-cols-3 gap-3">
            {/* IMDb */}
            <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-neutral-900/50 border border-neutral-800">
              <span className="font-black tracking-tighter text-base text-yellow-400 leading-none mb-1">IMDb</span>
              <span className="text-xl font-bold text-white">{movie.imdbScore}</span>
              {movie.imdbVotes && (
                <span className="text-[10px] text-neutral-500 mt-0.5 leading-none">{movie.imdbVotes} votes</span>
              )}
            </div>
            {/* Rotten Tomatoes */}
            <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-neutral-900/50 border border-neutral-800">
              <div className="mb-1">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/5b/Rotten_Tomatoes.svg" alt="RT" className="w-5 h-5 object-contain" />
              </div>
              <span className="text-xl font-bold text-white">{movie.rtScore > 0 ? `${movie.rtScore}%` : 'N/A'}</span>
              <span className="text-[10px] text-neutral-500 mt-0.5 leading-none">Tomatometer</span>
            </div>
            {/* Metacritic */}
            <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-neutral-900/50 border border-neutral-800">
              <div className="w-5 h-5 bg-emerald-500 flex items-center justify-center rounded-sm mb-1">
                <span className="text-white text-[10px] font-black leading-none">M</span>
              </div>
              <span className="text-xl font-bold text-white">{movie.metacriticScore > 0 ? movie.metacriticScore : 'N/A'}</span>
              <span className="text-[10px] text-neutral-500 mt-0.5 leading-none">Metascore</span>
            </div>
          </div>

          {/* Streaming Services */}
          {movie.streamingServices && movie.streamingServices.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-neutral-400 uppercase tracking-wider">Available On</h3>
              <div className="flex flex-wrap gap-2">
                {movie.streamingServices.map(service => (
                  <div key={service} className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm font-medium text-white flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    {service}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* The Story (Description) */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Film className="w-5 h-5 text-rose-500" />
              Synopsis
            </h3>
            <p className="text-neutral-300 leading-relaxed text-[15px]">
              {movie.description}
            </p>
          </div>

          {/* Filmmakers (Director / Writer) */}
          {(movie.director || movie.writer) && (
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Clapperboard className="w-5 h-5 text-violet-400" />
                Filmmakers
              </h3>
              <div className="space-y-2">
                {movie.director && (
                  <div className="flex items-start gap-3">
                    <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider w-16 pt-0.5 shrink-0">Director</span>
                    <span className="text-sm text-neutral-200 leading-snug">{movie.director}</span>
                  </div>
                )}
                {movie.writer && (
                  <div className="flex items-start gap-3">
                    <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider w-16 pt-0.5 shrink-0">Writer</span>
                    <span className="text-sm text-neutral-200 leading-snug">{movie.writer}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Awards & Box Office */}
          {(movie.awards || movie.boxOffice) && (
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                Awards & Box Office
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {movie.awards && (
                  <div className="flex flex-col gap-2 p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20 shadow-inner">
                    <div className="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center">
                      <Trophy className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="space-y-0.5">
                      <span className="text-[10px] font-bold text-amber-500/60 uppercase tracking-widest">Awards</span>
                      <p className="text-sm font-semibold text-amber-100 leading-snug line-clamp-3">{movie.awards}</p>
                    </div>
                  </div>
                )}
                {movie.boxOffice && (
                  <div className="flex flex-col gap-2 p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 shadow-inner">
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="space-y-0.5">
                      <span className="text-[10px] font-bold text-emerald-500/60 uppercase tracking-widest">Box Office</span>
                      <p className="text-sm font-bold text-emerald-300">{movie.boxOffice}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* The Talent (Cast Section) */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white">Top Billed Cast</h3>
            <div className="flex overflow-x-auto pb-4 -mx-6 px-6 gap-4 snap-x hide-scrollbar">
              {movie.castList.map((actor, idx) => (
                <div key={idx} className="flex flex-col items-center w-24 shrink-0 snap-start">
                  <div className="w-20 h-20 rounded-full overflow-hidden mb-3 border-2 border-neutral-800 shadow-lg bg-neutral-900">
                    <img
                      src={actor.imageUrl}
                      alt={actor.name}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                      onError={(e) => {
                        // Fallback if image fails to load
                        (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${encodeURIComponent(actor.name)}&background=random&color=fff`;
                      }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-white text-center leading-tight mb-1 line-clamp-2">
                    {actor.name}
                  </span>
                  <span className="text-xs text-neutral-500 text-center leading-tight line-clamp-2">
                    {actor.character}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Drag Handle Indicator */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 w-12 h-1.5 rounded-full bg-white/20 pointer-events-none" />
    </motion.div>
  );
}
