import React from 'react';
import { motion } from 'motion/react';
import { Clapperboard, Users } from 'lucide-react';

interface LobbyScreenProps {
  roomCode: string;
  playerCount: number;
}

export function LobbyScreen({ roomCode, playerCount }: LobbyScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden bg-neutral-950 selection:bg-rose-500/30">
      {/* Cinematic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(244,63,94,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_100%,rgba(249,115,22,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-sm z-10 flex flex-col items-center gap-8"
      >
        <div className="w-24 h-24 bg-neutral-900 rounded-[32px] flex items-center justify-center border border-neutral-800 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <Clapperboard className="w-10 h-10 text-rose-500" />
        </div>

        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white">Waiting for Host...</h2>
          <p className="text-neutral-400">The host is selecting the movie filters.</p>
        </div>

        <div className="bg-neutral-900/60 backdrop-blur-xl border border-neutral-800 rounded-3xl p-6 w-full space-y-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <span className="text-neutral-400 font-medium">Room Code</span>
            <span className="text-2xl font-mono font-bold tracking-widest text-white">{roomCode}</span>
          </div>
          
          <div className="h-px bg-neutral-800" />
          
          <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-neutral-400" />
              <span className="text-neutral-300 font-medium">Players Joined</span>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-rose-400 to-orange-400 text-transparent bg-clip-text">
              {playerCount}
            </span>
          </div>
        </div>

        {/* Pulsing loading indicator */}
        <div className="flex items-center gap-2 mt-4 text-rose-500/80">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
            className="w-2 h-2 rounded-full bg-current"
          />
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }}
            className="w-2 h-2 rounded-full bg-current"
          />
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }}
            className="w-2 h-2 rounded-full bg-current"
          />
        </div>
      </motion.div>
    </div>
  );
}
