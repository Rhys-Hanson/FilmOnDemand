import React, { useState, useRef, useEffect } from 'react';
import { motion, useMotionValue, useTransform } from 'motion/react';

interface DualRangeSliderProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
}

export function DualRangeSlider({ min, max, value, onChange }: DualRangeSliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [trackWidth, setTrackWidth] = useState(0);

  const [leftInput, setLeftInput] = useState(value[0].toString());
  const [rightInput, setRightInput] = useState(value[1].toString());

  useEffect(() => {
    setLeftInput(value[0].toString());
    setRightInput(value[1].toString());
  }, [value]);

  useEffect(() => {
    if (trackRef.current) {
      setTrackWidth(trackRef.current.offsetWidth);
    }
    const observer = new ResizeObserver(entries => {
      setTrackWidth(entries[0].contentRect.width);
    });
    if (trackRef.current) observer.observe(trackRef.current);
    return () => observer.disconnect();
  }, []);

  const leftX = useMotionValue(0);
  const rightX = useMotionValue(0);

  useEffect(() => {
    if (trackWidth > 0) {
      leftX.set(((value[0] - min) / (max - min)) * trackWidth);
      rightX.set(((value[1] - min) / (max - min)) * trackWidth);
    }
  }, [value, min, max, trackWidth, leftX, rightX]);

  const handleLeftDrag = (e: any, info: any) => {
    const newX = leftX.get() + info.delta.x;
    const clampedX = Math.max(0, Math.min(newX, rightX.get() - 24));
    leftX.set(clampedX);
    const newVal = Math.round((clampedX / trackWidth) * (max - min) + min);
    if (newVal !== value[0]) {
      onChange([newVal, value[1]]);
    }
  };

  const handleRightDrag = (e: any, info: any) => {
    const newX = rightX.get() + info.delta.x;
    const clampedX = Math.max(leftX.get() + 24, Math.min(newX, trackWidth));
    rightX.set(clampedX);
    const newVal = Math.round((clampedX / trackWidth) * (max - min) + min);
    if (newVal !== value[1]) {
      onChange([value[0], newVal]);
    }
  };

  const handleLeftBlur = () => {
    let parsed = parseInt(leftInput, 10);
    if (isNaN(parsed)) parsed = min;
    parsed = Math.max(min, Math.min(parsed, value[1]));
    setLeftInput(parsed.toString());
    onChange([parsed, value[1]]);
  };

  const handleRightBlur = () => {
    let parsed = parseInt(rightInput, 10);
    if (isNaN(parsed)) parsed = max;
    parsed = Math.max(value[0], Math.min(parsed, max));
    setRightInput(parsed.toString());
    onChange([value[0], parsed]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  const activeWidth = useTransform(() => Math.max(0, rightX.get() - leftX.get()));

  return (
    <div className="py-2">
      <div className="flex justify-between text-white font-medium mb-6">
        <input 
          type="text"
          value={leftInput}
          onChange={(e) => setLeftInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
          onBlur={handleLeftBlur}
          onKeyDown={handleKeyDown}
          className="bg-neutral-900/80 border border-neutral-800 px-3 py-1.5 rounded-xl text-sm font-semibold shadow-sm backdrop-blur-md w-16 text-center focus:outline-none focus:ring-2 focus:ring-rose-500/50 transition-all"
        />
        <input 
          type="text"
          value={rightInput}
          onChange={(e) => setRightInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
          onBlur={handleRightBlur}
          onKeyDown={handleKeyDown}
          className="bg-neutral-900/80 border border-neutral-800 px-3 py-1.5 rounded-xl text-sm font-semibold shadow-sm backdrop-blur-md w-16 text-center focus:outline-none focus:ring-2 focus:ring-rose-500/50 transition-all"
        />
      </div>
      
      <div className="relative h-2.5 bg-neutral-900 border border-neutral-800 rounded-full shadow-inner" ref={trackRef}>
        {/* Active Track */}
        <motion.div 
          className="absolute top-0 bottom-0 bg-gradient-to-r from-rose-500 to-orange-500 rounded-full shadow-[0_0_15px_rgba(244,63,94,0.4)]"
          style={{ left: leftX, width: activeWidth }}
        />
        
        {/* Left Thumb */}
        <motion.div
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0}
          dragMomentum={false}
          onDrag={handleLeftDrag}
          style={{ x: leftX }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="absolute top-1/2 -translate-y-1/2 -ml-3.5 w-7 h-7 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.5)] border-[3px] border-neutral-950 cursor-grab active:cursor-grabbing z-10 flex items-center justify-center"
        >
          <div className="w-1.5 h-1.5 bg-rose-500 rounded-full" />
        </motion.div>
        
        {/* Right Thumb */}
        <motion.div
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0}
          dragMomentum={false}
          onDrag={handleRightDrag}
          style={{ x: rightX }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="absolute top-1/2 -translate-y-1/2 -ml-3.5 w-7 h-7 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.5)] border-[3px] border-neutral-950 cursor-grab active:cursor-grabbing z-10 flex items-center justify-center"
        >
          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full" />
        </motion.div>
      </div>
    </div>
  );
}
