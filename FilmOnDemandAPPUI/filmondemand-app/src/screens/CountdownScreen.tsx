import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface CountdownScreenProps {
  onFinish: () => void;
}

export function CountdownScreen({ onFinish }: CountdownScreenProps) {
  const [count, setCount] = useState(3);

  useEffect(() => {
    if (count > 0) {
      const timer = setTimeout(() => setCount(count - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(() => onFinish(), 500);
      return () => clearTimeout(timer);
    }
  }, [count, onFinish]);

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-br from-rose-500/20 to-orange-500/20 blur-[100px]" />
      
      <AnimatePresence mode="wait">
        {count > 0 ? (
          <motion.div
            key={count}
            initial={{ scale: 0.5, opacity: 0, rotate: -15 }}
            animate={{ scale: 1, opacity: 1, rotate: 0 }}
            exit={{ scale: 1.5, opacity: 0, filter: 'blur(10px)' }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            className="text-[12rem] font-black text-transparent bg-clip-text bg-gradient-to-br from-rose-500 to-orange-400 drop-shadow-[0_0_30px_rgba(244,63,94,0.5)]"
          >
            {count}
          </motion.div>
        ) : (
          <motion.div
            key="go"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.5, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-emerald-400 to-teal-400 drop-shadow-[0_0_30px_rgba(52,211,153,0.5)]"
          >
            GO!
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
