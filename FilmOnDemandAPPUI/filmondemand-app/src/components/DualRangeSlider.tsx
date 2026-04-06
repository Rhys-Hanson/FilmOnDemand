import { useEffect, useRef, useState, type KeyboardEvent, type PointerEvent as ReactPointerEvent } from 'react';
import { motion } from 'motion/react';

interface DualRangeSliderProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
}

export function DualRangeSlider({ min, max, value, onChange }: DualRangeSliderProps) {
  const [localValue, setLocalValue] = useState(value);
  const trackRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef<'left' | 'right' | null>(null);

  const [leftInput, setLeftInput] = useState(value[0].toString());
  const [rightInput, setRightInput] = useState(value[1].toString());

  // Keep local values and inputs in sync with parent when parent changes
  useEffect(() => {
    if (!isDragging.current) {
      setLocalValue(value);
      setLeftInput(value[0].toString());
      setRightInput(value[1].toString());
    }
  }, [value]);

  const handlePointerDown = (e: ReactPointerEvent<HTMLDivElement>, thumb: 'left' | 'right') => {
    e.stopPropagation();
    e.preventDefault(); // prevent selection
    isDragging.current = thumb;
    document.addEventListener('pointermove', handlePointerMove);
    document.addEventListener('pointerup', handlePointerUp);
  };

  const handlePointerMove = (e: PointerEvent) => {
    if (!trackRef.current || !isDragging.current) return;
    
    // Prevent default pointer behavior while dragging
    e.preventDefault();

    const rect = trackRef.current.getBoundingClientRect();
    let percentage = (e.clientX - rect.left) / rect.width;
    percentage = Math.max(0, Math.min(1, percentage));
    
    const newValue = Math.round(percentage * (max - min) + min);
    
    setLocalValue(prev => {
      const result: [number, number] = isDragging.current === 'left' 
        ? [Math.min(newValue, prev[1]), prev[1]]
        : [prev[0], Math.max(newValue, prev[0])];
      
      // Sync inputs live
      if (isDragging.current === 'left') setLeftInput(result[0].toString());
      if (isDragging.current === 'right') setRightInput(result[1].toString());
      
      return result;
    });
  };

  const handlePointerUp = () => {
    document.removeEventListener('pointermove', handlePointerMove);
    document.removeEventListener('pointerup', handlePointerUp);
    
    setLocalValue(current => {
      onChange(current);
      return current;
    });
    
    // Small delay to allow react to finish before unsetting ref
    setTimeout(() => {
      isDragging.current = null;
    }, 0);
  };

  const handleLeftBlur = () => {
    let parsed = parseInt(leftInput, 10);
    if (isNaN(parsed)) parsed = min;
    parsed = Math.max(min, Math.min(parsed, localValue[1]));
    setLeftInput(parsed.toString());
    setLocalValue([parsed, localValue[1]]);
    onChange([parsed, localValue[1]]);
  };

  const handleRightBlur = () => {
    let parsed = parseInt(rightInput, 10);
    if (isNaN(parsed)) parsed = max;
    parsed = Math.max(localValue[0], Math.min(parsed, max));
    setRightInput(parsed.toString());
    setLocalValue([localValue[0], parsed]);
    onChange([localValue[0], parsed]);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  const leftPercent = ((localValue[0] - min) / (max - min)) * 100;
  const rightPercent = ((localValue[1] - min) / (max - min)) * 100;

  return (
    <div className="py-2 w-full select-none relative z-0">
      <div className="flex justify-between items-center text-white font-medium mb-10">
        <div className="relative group z-10">
          <label className="absolute -top-6 left-2 text-[11px] uppercase font-bold text-neutral-400 tracking-widest drop-shadow-md">From</label>
          <input 
            type="text"
            value={leftInput}
            onChange={(e) => setLeftInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
            onBlur={handleLeftBlur}
            onKeyDown={handleKeyDown}
            className="bg-neutral-900/60 border border-white/10 px-4 py-2 rounded-xl text-center text-sm font-black shadow-lg backdrop-blur-xl w-24 focus:outline-none focus:border-rose-500/80 focus:ring-2 focus:ring-rose-500/20 transition-all hover:bg-neutral-800/80 focus:bg-neutral-900"
          />
        </div>
        
        <div className="flex-1 flex items-center justify-center px-4 relative">
           <div className="w-16 h-[2px] bg-neutral-800/50 rounded-full" />
        </div>

        <div className="relative group z-10">
          <label className="absolute -top-6 right-2 text-[11px] uppercase font-bold text-neutral-400 tracking-widest drop-shadow-md text-right">To</label>
          <input 
            type="text"
            value={rightInput}
            onChange={(e) => setRightInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
            onBlur={handleRightBlur}
            onKeyDown={handleKeyDown}
            className="bg-neutral-900/60 border border-white/10 px-4 py-2 rounded-xl text-center text-sm font-black shadow-lg backdrop-blur-xl w-24 focus:outline-none focus:border-orange-500/80 focus:ring-2 focus:ring-orange-500/20 transition-all hover:bg-neutral-800/80 focus:bg-neutral-900"
          />
        </div>
      </div>
      
      <div className="relative h-3 bg-neutral-950 border border-white/5 rounded-full shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)] cursor-pointer" ref={trackRef}>
        {/* Total Track Gradient Background (faint) */}
        <div className="absolute inset-0 rounded-full bg-neutral-800/20 overflow-hidden" />
        
        {/* Active Track */}
        <motion.div 
          className="absolute top-0 bottom-0 bg-gradient-to-r from-rose-500 to-orange-500 rounded-full shadow-[0_0_24px_rgba(244,63,94,0.4)]"
          animate={{
            left: `${leftPercent}%`,
            width: `${rightPercent - leftPercent}%`
          }}
          transition={{ type: "spring", stiffness: 400, damping: 30, mass: 0.8 }}
        />
        
        {/* Left Thumb */}
        <motion.div
          animate={{ left: `${leftPercent}%` }}
          transition={{ type: "spring", stiffness: 400, damping: 30, mass: 0.8 }}
          onPointerDown={(e) => handlePointerDown(e, 'left')}
          whileHover={{ scale: 1.25 }}
          whileTap={{ scale: 0.9 }}
          className="absolute top-1/2 -translate-y-1/2 -ml-3.5 w-7 h-7 bg-white rounded-full shadow-[0_4px_16px_rgba(0,0,0,0.8)] border-[4px] border-neutral-950 cursor-grab active:cursor-grabbing z-10 flex items-center justify-center touch-none group hover:border-rose-500 transition-colors"
        >
          <div className="w-1.5 h-1.5 bg-rose-500 rounded-full group-hover:scale-125 transition-transform" />
        </motion.div>
        
        {/* Right Thumb */}
        <motion.div
          animate={{ left: `${rightPercent}%` }}
          transition={{ type: "spring", stiffness: 400, damping: 30, mass: 0.8 }}
          onPointerDown={(e) => handlePointerDown(e, 'right')}
          whileHover={{ scale: 1.25 }}
          whileTap={{ scale: 0.9 }}
          className="absolute top-1/2 -translate-y-1/2 -ml-3.5 w-7 h-7 bg-white rounded-full shadow-[0_4px_16px_rgba(0,0,0,0.8)] border-[4px] border-neutral-950 cursor-grab active:cursor-grabbing z-20 flex items-center justify-center touch-none group hover:border-orange-500 transition-colors"
        >
          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full group-hover:scale-125 transition-transform" />
        </motion.div>
      </div>
    </div>
  );
}
