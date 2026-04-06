import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { QrCode, Play, Plus, Clapperboard, Info } from 'lucide-react';

interface EntryScreenProps {
  onJoin: (code: string) => void;
  onCreate: () => void;
}

export function EntryScreen({ onJoin, onCreate }: EntryScreenProps) {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const qrInputRef = useRef<HTMLInputElement | null>(null);
  const [showQrToast, setShowQrToast] = useState(false);

  const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);

  const handleScanQr = () => {
    if (isMobile) {
      // On mobile, trigger the hidden file input which opens the native camera
      qrInputRef.current?.click();
    } else {
      // On desktop, show a helpful hint
      setShowQrToast(true);
      setTimeout(() => setShowQrToast(false), 3500);
    }
  };

  const fullCode = code.join('');

  const handleJoin = (e: React.FormEvent) => {
    e.preventDefault();
    if (fullCode.length === 6) {
      onJoin(fullCode);
    }
  };

  const handleChange = (index: number, value: string) => {
    if (!/^[a-zA-Z0-9]*$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value.slice(-1).toUpperCase();
    setCode(newCode);

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
    if (pastedData) {
      const newCode = [...code];
      for (let i = 0; i < pastedData.length; i++) {
        newCode[i] = pastedData[i];
      }
      setCode(newCode);
      const focusIndex = Math.min(pastedData.length, 5);
      inputRefs.current[focusIndex]?.focus();
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden bg-neutral-950 selection:bg-rose-500/30">
      {/* Cinematic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(244,63,94,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_100%,rgba(249,115,22,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-sm z-10 space-y-12"
      >
        {/* Logo Section */}
        <div className="text-center space-y-4">
          <motion.div 
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-24 h-24 mx-auto bg-gradient-to-br from-rose-500 to-orange-500 rounded-[32px] flex items-center justify-center shadow-[0_0_40px_rgba(244,63,94,0.4)] border border-white/10"
          >
            <Clapperboard className="w-12 h-12 text-white" strokeWidth={1.5} />
          </motion.div>
          <motion.div
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <h1 className="text-4xl font-black text-white tracking-tight">FilmOnDemand</h1>
            <p className="text-neutral-400 mt-2 font-medium">Swipe together. Watch tonight.</p>
          </motion.div>
        </div>

        {/* Join Form */}
        <motion.form 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          onSubmit={handleJoin} 
          className="space-y-4"
        >
          <div className="flex justify-between gap-2">
            {code.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (inputRefs.current[index] = el)}
                type="text"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                className="w-12 h-14 sm:w-14 sm:h-16 bg-neutral-900/60 border border-neutral-800/80 rounded-xl text-center text-2xl font-mono font-bold text-white focus:outline-none focus:ring-2 focus:ring-rose-500/50 focus:border-rose-500/50 transition-all backdrop-blur-xl shadow-inner uppercase"
              />
            ))}
          </div>

          <AnimatePresence>
            {fullCode.length === 6 && (
              <motion.button
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                type="submit"
                className="w-full bg-white text-black font-bold text-lg rounded-[20px] py-4 flex items-center justify-center gap-2 shadow-[0_8px_32px_rgba(255,255,255,0.2)] hover:scale-[1.02] active:scale-[0.98] transition-all overflow-hidden"
              >
                <Play className="w-5 h-5 fill-current" />
                Join Room
              </motion.button>
            )}
          </AnimatePresence>

          {/* Hidden camera input — triggers native QR scanner on mobile */}
          <input
            ref={qrInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            // Reading the QR image is handled by the OS camera app itself;
            // it will parse the URL and open the browser to /join/:code directly.
            onChange={() => {}}
          />

          <button
            type="button"
            onClick={handleScanQr}
            className="w-full bg-neutral-900/40 border border-neutral-800/80 text-white font-semibold rounded-[20px] py-4 flex items-center justify-center gap-2 hover:bg-neutral-800/60 transition-colors backdrop-blur-md mt-4 relative"
          >
            <QrCode className="w-5 h-5 text-neutral-400" />
            Scan QR Code
          </button>

          {/* Desktop hint toast */}
          <AnimatePresence>
            {showQrToast && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 8 }}
                className="flex items-start gap-3 bg-neutral-800/90 backdrop-blur-md border border-neutral-700 rounded-2xl p-4 text-sm text-neutral-300"
              >
                <Info className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>Open your phone's camera app and point it at the QR code on the host's screen — it'll join automatically.</span>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.form>

        {/* Divider */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="flex items-center gap-4 text-neutral-600"
        >
          <div className="flex-1 h-px bg-neutral-800" />
          <span className="text-sm font-medium uppercase tracking-wider">Or</span>
          <div className="flex-1 h-px bg-neutral-800" />
        </motion.div>

        {/* Create Room */}
        <motion.button
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          onClick={onCreate}
          className="w-full bg-gradient-to-r from-rose-500 to-orange-500 text-white font-bold text-lg rounded-[20px] py-5 flex items-center justify-center gap-2 shadow-[0_8px_32px_rgba(244,63,94,0.3)] hover:shadow-[0_8px_40px_rgba(244,63,94,0.4)] border border-white/10 transition-all active:scale-[0.98]"
        >
          <Plus className="w-6 h-6" />
          Create New Room
        </motion.button>
      </motion.div>
    </div>
  );
}
