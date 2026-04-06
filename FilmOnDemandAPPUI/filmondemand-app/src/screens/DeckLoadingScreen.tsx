import React, { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Clapperboard } from 'lucide-react';

const LOADING_MESSAGES = [
  'Finding the best results for you',
  'Loading top picks',
  'Compiling results',
  'Matching your filters',
  'Building tonight\'s lineup',
];

export function DeckLoadingScreen() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((current) => (current + 1) % LOADING_MESSAGES.length);
    }, 1800);

    return () => clearInterval(interval);
  }, []);

  const activeMessage = useMemo(() => LOADING_MESSAGES[messageIndex], [messageIndex]);

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-neutral-950 selection:bg-rose-500/30">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(244,63,94,0.18),transparent_45%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_90%,rgba(249,115,22,0.14),transparent_42%)]" />
      </div>

      <div className="relative z-10 w-full max-w-md rounded-[32px] border border-white/10 bg-neutral-900/70 p-8 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col items-center text-center gap-6">
          <motion.div
            animate={{ rotate: [0, 4, -4, 0], scale: [1, 1.04, 1] }}
            transition={{ repeat: Infinity, duration: 2.4, ease: 'easeInOut' }}
            className="flex h-24 w-24 items-center justify-center rounded-[28px] border border-rose-400/20 bg-gradient-to-br from-rose-500/20 to-orange-500/20"
          >
            <Clapperboard className="h-10 w-10 text-rose-400" />
          </motion.div>

          <div className="space-y-3">
            <h1 className="text-3xl font-bold tracking-tight text-white">Preparing your deck</h1>
            <AnimatePresence mode="wait">
              <motion.p
                key={activeMessage}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="text-neutral-300 text-lg"
              >
                {activeMessage}
              </motion.p>
            </AnimatePresence>
          </div>

          <div className="flex items-center gap-3 pt-2">
            {[0, 1, 2].map((dot) => (
              <motion.div
                key={dot}
                animate={{ opacity: [0.25, 1, 0.25], y: [0, -6, 0] }}
                transition={{ repeat: Infinity, duration: 1.1, delay: dot * 0.15 }}
                className="h-3 w-3 rounded-full bg-gradient-to-r from-rose-400 to-orange-400"
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
