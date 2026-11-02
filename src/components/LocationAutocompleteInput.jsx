/**
 * LocationAutocompleteInput.jsx
 * 
 * Location Autocomplete Input Component
 * Combines online OpenStreetMap Nominatim geocoding via FastAPI backend
 * with local curated Goa landmarks for instant, resilient location search.
 */

import React, { useState, useRef, useEffect } from 'react';
import { MapPin, Check, AlertCircle, X, ChevronDown, Loader2, Globe } from 'lucide-react';
import { GOA_LANDMARKS } from '../data/goaLandmarks';
import { searchLocationsApi, filterGoaLandmarks } from '../services/locationService';

export default function LocationAutocompleteInput({
  id,
  label,
  value,
  onChange,
  onSelect,
  placeholder,
  dotColor = 'emerald', // 'emerald' | 'rose'
  isInvalid = false,
  errorMessage = '',
  isMapLocation = false
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [suggestions, setSuggestions] = useState(() => filterGoaLandmarks(value || ''));
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef(null);

  // Debounced online geocoding lookup
  useEffect(() => {
    let isMounted = true;
    const timer = setTimeout(async () => {
      if (!value || value.trim().length < 2) {
        if (isMounted) setSuggestions(filterGoaLandmarks(value || ''));
        return;
      }
      setIsSearching(true);
      try {
        const results = await searchLocationsApi(value);
        if (isMounted) {
          setSuggestions(results);
        }
      } catch {
        if (isMounted) {
          setSuggestions(filterGoaLandmarks(value));
        }
      } finally {
        if (isMounted) setIsSearching(false);
      }
    }, 250);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [value]);

  const hasExactMatch = GOA_LANDMARKS.some(
    (loc) =>
      loc.name.toLowerCase() === (value || '').trim().toLowerCase() ||
      (Array.isArray(loc.aliases) &&
        loc.aliases.some((a) => a.toLowerCase() === (value || '').trim().toLowerCase()))
  );

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  const handleSelectLandmark = (item) => {
    onSelect(item);
    setIsOpen(false);
    setActiveIndex(-1);
  };

  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => 
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => 
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && activeIndex < suggestions.length) {
        handleSelectLandmark(suggestions[activeIndex]);
      } else if (suggestions.length > 0) {
        handleSelectLandmark(suggestions[0]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      {/* Input Label (if provided) */}
      {label && (
        <label 
          htmlFor={id} 
          className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between"
        >
          <span className="flex items-center gap-1.5">
            <span 
              className={`w-2 h-2 rounded-full ${
                dotColor === 'emerald' 
                  ? 'bg-emerald-400 ring-2 ring-emerald-500/20' 
                  : 'bg-rose-400 ring-2 ring-rose-500/20'
              }`}
            ></span>
            {label}
          </span>
          <span className="text-[10px] text-slate-500 font-normal">Goa / Nominatim</span>
        </label>
      )}

      {/* Input Field Container */}
      <div className="relative">
        <input
          id={id}
          type="text"
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoComplete="off"
          className={`w-full bg-slate-950/90 border rounded-xl pl-3.5 pr-16 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all ${
            isInvalid
              ? 'border-rose-500/80 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
              : isMapLocation
              ? dotColor === 'emerald'
                ? 'border-emerald-500/70 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-500/20 bg-emerald-950/20'
                : 'border-rose-500/70 focus:border-rose-400 focus:ring-2 focus:ring-rose-500/20 bg-rose-950/20'
              : hasExactMatch
              ? 'border-emerald-500/60 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20'
              : 'border-slate-700/80 hover:border-slate-600 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20'
          }`}
        />

        {/* Action icons right side */}
        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isSearching && (
            <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin mr-1" />
          )}

          {value && (
            <button
              type="button"
              onClick={() => {
                onChange('');
                setIsOpen(true);
              }}
              title="Clear input"
              className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          <div 
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 text-slate-400 hover:text-slate-200 cursor-pointer"
          >
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-180 text-cyan-400' : ''}`} />
          </div>
        </div>
      </div>

      {/* Unmatched / Invalid Message below input */}
      {isInvalid && errorMessage && (
        <p className="mt-1.5 text-[11px] text-rose-400 flex items-center gap-1 font-medium">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{errorMessage}</span>
        </p>
      )}

      {/* Autocomplete Dropdown Menu */}
      {isOpen && (
        <div 
          className="absolute left-0 right-0 top-full mt-1.5 z-50 bg-slate-900 border border-slate-700/90 rounded-xl shadow-2xl shadow-black/80 backdrop-blur-xl overflow-hidden max-h-64 overflow-y-auto custom-scrollbar"
        >
          {/* Dropdown Header */}
          <div className="px-3 py-1.5 bg-slate-950/70 border-b border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
            <span className="font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1">
              <Globe className="w-3 h-3 text-cyan-400" />
              <span>Goa Locations & Landmarks</span>
            </span>
            <span>{suggestions.length} results</span>
          </div>

          {/* Suggestions List */}
          {suggestions.length > 0 ? (
            <div className="py-1">
              {suggestions.map((item, index) => {
                const isSelected = value.trim().toLowerCase() === item.name.toLowerCase();
                const isHighlighted = activeIndex === index;

                return (
                  <button
                    key={item.id || index}
                    type="button"
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleSelectLandmark(item);
                    }}
                    onMouseEnter={() => setActiveIndex(index)}
                    className={`w-full text-left px-3.5 py-2.5 flex items-center justify-between gap-3 transition-colors cursor-pointer ${
                      isHighlighted
                        ? 'bg-slate-800/90 text-white'
                        : isSelected
                        ? 'bg-cyan-950/40 text-cyan-200'
                        : 'text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <div className="flex items-start gap-2.5 min-w-0">
                      <div className="mt-0.5 p-1 rounded-md bg-slate-800 text-cyan-400 shrink-0">
                        <MapPin className="w-3.5 h-3.5" />
                      </div>
                      <div className="truncate">
                        <div className="font-semibold text-xs text-slate-100 flex items-center gap-1.5">
                          <span className="truncate">{item.name}</span>
                          {isSelected && (
                            <Check className="w-3 h-3 text-emerald-400 shrink-0" />
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400 truncate">
                          {item.displayName || item.area || 'Goa, India'}
                        </div>
                      </div>
                    </div>

                    {/* Category pill */}
                    <div className="text-[10px] text-slate-400 shrink-0 bg-slate-950/70 px-2 py-0.5 rounded border border-slate-800 hidden sm:block">
                      {item.category || 'Location'}
                    </div>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="p-3.5 text-center">
              <div className="flex items-center justify-center gap-1.5 text-amber-400 text-xs font-bold mb-1">
                <AlertCircle className="w-4 h-4" />
                <span>No matching locations found</span>
              </div>
              <p className="text-[11px] text-slate-300 leading-snug">
                Could not find "<span className="text-amber-200 font-semibold">{value}</span>" in Goa.
              </p>
              <p className="text-[10px] text-slate-400 mt-1.5">
                Try selecting a point directly on the map or choose a popular landmark below:
              </p>
              <div className="flex flex-wrap gap-1 mt-2 justify-center">
                {GOA_LANDMARKS.slice(0, 5).map((loc) => (
                  <button
                    key={loc.id}
                    type="button"
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleSelectLandmark(loc);
                    }}
                    className="text-[10px] px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 cursor-pointer"
                  >
                    {loc.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
