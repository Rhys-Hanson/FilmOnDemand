import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, X, Plus } from 'lucide-react';
import { cn } from '../lib/utils';

interface SearchableChipInputProps {
  placeholder: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  icon?: React.ReactNode;
  suggestions?: string[];
}

export function SearchableChipInput({ placeholder, options, selected, onChange, icon, suggestions }: SearchableChipInputProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredOptions = query.trim().length > 0
    ? options.filter(o =>
        o.toLowerCase().includes(query.toLowerCase()) && !selected.includes(o)
      )
    : [];

  // Close dropdown on click outside the entire component
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAdd = (option: string) => {
    if (!selected.includes(option)) {
      onChange([...selected, option]);
    }
    setQuery('');
    setIsOpen(false);
    // Return focus to input so user can keep typing
    inputRef.current?.focus();
  };

  const handleRemove = (option: string) => {
    onChange(selected.filter(s => s !== option));
  };

  const availableSuggestions = suggestions?.filter(s => !selected.includes(s)) || [];

  return (
    <div className="space-y-3" ref={containerRef}>
      <div className="relative">
        <div className={cn(
          "flex items-center bg-neutral-900/60 border rounded-2xl px-4 py-3.5 transition-all backdrop-blur-xl shadow-inner",
          isOpen ? "border-rose-500/50 ring-2 ring-rose-500/20 bg-neutral-900/80" : "border-neutral-800/80 hover:border-neutral-700"
        )}>
          {icon || <Search className="w-5 h-5 text-neutral-500 mr-3 shrink-0" />}
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setIsOpen(e.target.value.trim().length > 0);
            }}
            onFocus={() => {
              if (query.trim().length > 0) setIsOpen(true);
            }}
            // No onBlur here — the click-outside handler manages closing cleanly
            placeholder={placeholder}
            className="bg-transparent border-none outline-none text-white w-full placeholder:text-neutral-600 font-medium"
          />
          {query.length > 0 && (
            <button
              onClick={() => { setQuery(''); setIsOpen(false); inputRef.current?.focus(); }}
              className="ml-2 text-neutral-500 hover:text-white transition-colors shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <AnimatePresence>
          {isOpen && filteredOptions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="absolute top-full left-0 right-0 mt-2 bg-neutral-900/95 backdrop-blur-2xl border border-neutral-800 rounded-2xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.5)] max-h-56 overflow-y-auto z-[60]"
            >
              {filteredOptions.map((option) => (
                <button
                  key={option}
                  // Use onMouseDown to fire before any potential focus events,
                  // but now we don't need preventDefault since there's no onBlur race.
                  onMouseDown={() => handleAdd(option)}
                  className="w-full text-left px-5 py-3.5 text-neutral-300 hover:bg-white/5 hover:text-white transition-colors flex items-center justify-between border-b border-white/5 last:border-0"
                >
                  <span className="font-medium">{option}</span>
                  <Plus className="w-4 h-4 text-neutral-500" />
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex flex-col gap-3">
        {selected.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <AnimatePresence>
              {selected.map(item => (
                <motion.div
                  layout
                  key={item}
                  initial={{ opacity: 0, scale: 0.8, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, width: 0, margin: 0, padding: 0 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  className="flex items-center gap-1.5 bg-white/10 border border-white/10 text-white px-3.5 py-1.5 rounded-full text-sm font-medium backdrop-blur-md shadow-sm"
                >
                  {item}
                  <button 
                    onClick={() => handleRemove(item)} 
                    className="p-0.5 hover:bg-white/20 rounded-full transition-colors ml-1"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {availableSuggestions.length > 0 && (
          <div className="pt-1">
            <p className="text-[11px] text-neutral-500 font-bold mb-2 uppercase tracking-wider">Quick Select</p>
            <div className="flex flex-wrap gap-2">
              {availableSuggestions.map(suggestion => (
                <button
                  key={suggestion}
                  onClick={() => handleAdd(suggestion)}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium border border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-600 hover:bg-neutral-800 transition-colors"
                >
                  <Plus className="w-3 h-3" />
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
