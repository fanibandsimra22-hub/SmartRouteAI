import React, { useState } from 'react';
import { 
  Navigation2, 
  ArrowUpDown, 
  Zap, 
  Ruler, 
  Search, 
  RotateCcw,
  AlertTriangle,
  MapPin,
  Crosshair,
  LocateFixed,
  Loader2
} from 'lucide-react';
import { GOA_LANDMARKS } from '../data/goaLandmarks';
import { findGoaLandmark } from '../services/locationService';
import LocationAutocompleteInput from './LocationAutocompleteInput';

export default function RouteSearchForm({
  origin,
  setOrigin,
  originLandmark,
  originCoords,
  onSelectOrigin,
  destination,
  setDestination,
  destinationLandmark,
  destinationCoords,
  onSelectDestination,
  preference,
  setPreference,
  onFindRoute,
  isLoading,
  onReset,
  validationError,
  selectionMode,
  onSetSelectionMode
}) {
  const [isLocating, setIsLocating] = useState(false);

  const handleCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false);
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const coords = [lat, lng];
        const label = 'My Current Location';
        setOrigin(label);
        onSelectOrigin(null, coords);
      },
      (err) => {
        setIsLocating(false);
        alert(`Location acquisition failed: ${err.message}. You can select your starting point on the map or enter a landmark.`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };
  const handleSwap = () => {
    const tempText = origin;
    const tempLandmark = originLandmark;
    const tempCoords = originCoords;

    setOrigin(destination);
    onSelectOrigin(destinationLandmark, destinationCoords);
    setDestination(tempText);
    onSelectDestination(tempLandmark, tempCoords);
  };

  const handleQuickSelectOrigin = (loc) => {
    setOrigin(loc.name);
    onSelectOrigin(loc, loc.coordinates);
  };

  const handleQuickSelectDest = (loc) => {
    setDestination(loc.name);
    onSelectDestination(loc, loc.coordinates);
  };

  const isOriginCustomMap = Boolean(
    originCoords && !originLandmark && (
      origin?.startsWith('Selected Map Location') ||
      origin?.startsWith('My Current Location') ||
      origin?.startsWith('Current GPS Location')
    )
  );
  const isDestCustomMap = Boolean(
    destinationCoords && !destinationLandmark && (
      destination?.startsWith('Selected Map Location') ||
      destination?.startsWith('My Current Location') ||
      destination?.startsWith('Current GPS Location')
    )
  );

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-5 shadow-xl shadow-black/40 backdrop-blur-md">
      {/* Title */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Navigation2 className="w-4 h-4 text-cyan-400" />
          Plan Your Route
        </h2>
        <span className="text-[11px] font-semibold text-cyan-300 bg-cyan-950/80 px-2.5 py-0.5 rounded-md border border-cyan-800/60">
          Goa Region Database
        </span>
      </div>

      <form 
        onSubmit={(e) => {
          e.preventDefault();
          onFindRoute();
        }}
        className="space-y-4"
      >
        {/* Validation Warning Banner if input is invalid */}
        {validationError && (
          <div className="p-3 rounded-xl bg-rose-950/50 border border-rose-500/50 text-xs text-rose-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Selection Error</div>
              <div className="text-[11px] text-rose-200 mt-0.5">{validationError}</div>
            </div>
          </div>
        )}

        {/* Origin & Destination with Autocomplete */}
        <div className="relative space-y-3">
          {/* Starting Location Autocomplete */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-emerald-500/20"></span>
                <span>Starting Location (Origin)</span>
              </span>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={handleCurrentLocation}
                  disabled={isLocating}
                  className="text-[11px] px-2 py-0.5 rounded-md flex items-center gap-1 font-medium bg-slate-800 text-cyan-400 hover:bg-slate-750 hover:text-white border border-slate-700 transition-all cursor-pointer disabled:opacity-50"
                  title="Use current GPS location"
                >
                  {isLocating ? (
                    <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />
                  ) : (
                    <LocateFixed className="w-3 h-3" />
                  )}
                  <span>{isLocating ? 'Locating...' : 'GPS'}</span>
                </button>
                {onSetSelectionMode && (
                  <button
                    type="button"
                    onClick={() => onSetSelectionMode(selectionMode === 'origin' ? null : 'origin')}
                    className={`text-[11px] px-2 py-0.5 rounded-md flex items-center gap-1 font-medium transition-all cursor-pointer ${
                      selectionMode === 'origin'
                        ? 'bg-emerald-500 text-slate-950 font-bold ring-2 ring-emerald-400'
                        : 'bg-slate-800 text-emerald-400 hover:bg-slate-750 hover:text-white border border-slate-700'
                    }`}
                    title="Click to select starting point by clicking the map"
                  >
                    <Crosshair className="w-3 h-3" />
                    <span>{selectionMode === 'origin' ? 'Click Map...' : 'Pick on Map'}</span>
                  </button>
                )}
              </div>
            </div>

            <LocationAutocompleteInput
              id="origin-input"
              value={origin}
              onChange={(val) => {
                setOrigin(val);
                // Check if typed value matches a landmark or alias
                const match = findGoaLandmark(val);
                onSelectOrigin(match || null, match ? match.coordinates : null);
              }}
              onSelect={(landmark) => {
                setOrigin(landmark.name);
                onSelectOrigin(landmark, landmark.coordinates);
              }}
              placeholder="Search Goa landmark (e.g. PCCE, Panaji)"
              dotColor="emerald"
              isInvalid={Boolean(origin && !originLandmark && !isOriginCustomMap)}
              errorMessage="Location not found in demo database"
              isMapLocation={isOriginCustomMap}
            />

            {isOriginCustomMap && (
              <div className="mt-1 flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
                <MapPin className="w-3 h-3 text-emerald-400 shrink-0" />
                <span>GPS: [{originCoords[0].toFixed(4)}°, {originCoords[1].toFixed(4)}°] (Draggable on map)</span>
              </div>
            )}
          </div>

          {/* Swap Button Divider */}
          <div className="flex justify-end pr-2 -my-1 relative z-10">
            <button
              type="button"
              onClick={handleSwap}
              title="Swap Origin & Destination"
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-cyan-300 border border-slate-700 hover:border-slate-600 shadow-sm transition-all cursor-pointer"
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Destination Autocomplete */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-rose-400 ring-2 ring-rose-500/20"></span>
                <span>Destination Point</span>
              </span>
              {onSetSelectionMode && (
                <button
                  type="button"
                  onClick={() => onSetSelectionMode(selectionMode === 'destination' ? null : 'destination')}
                  className={`text-[11px] px-2 py-0.5 rounded-md flex items-center gap-1 font-medium transition-all cursor-pointer ${
                    selectionMode === 'destination'
                      ? 'bg-rose-500 text-white font-bold ring-2 ring-rose-400'
                      : 'bg-slate-800 text-rose-400 hover:bg-slate-750 hover:text-white border border-slate-700'
                  }`}
                  title="Click to select destination point by clicking the map"
                >
                  <Crosshair className="w-3 h-3" />
                  <span>{selectionMode === 'destination' ? 'Click Map...' : 'Pick on Map'}</span>
                </button>
              )}
            </div>

            <LocationAutocompleteInput
              id="destination-input"
              value={destination}
              onChange={(val) => {
                setDestination(val);
                // Check if typed value matches a landmark or alias
                const match = findGoaLandmark(val);
                onSelectDestination(match || null, match ? match.coordinates : null);
              }}
              onSelect={(landmark) => {
                setDestination(landmark.name);
                onSelectDestination(landmark, landmark.coordinates);
              }}
              placeholder="Search Goa destination (e.g. PCCE, Goa University)"
              dotColor="rose"
              isInvalid={Boolean(destination && !destinationLandmark && !isDestCustomMap)}
              errorMessage="Destination not found in demo database"
              isMapLocation={isDestCustomMap}
            />

            {isDestCustomMap && (
              <div className="mt-1 flex items-center gap-1 text-[11px] text-rose-400 font-mono">
                <MapPin className="w-3 h-3 text-rose-400 shrink-0" />
                <span>GPS: [{destinationCoords[0].toFixed(4)}°, {destinationCoords[1].toFixed(4)}°] (Draggable on map)</span>
              </div>
            )}
          </div>
        </div>

        {/* Quick Location Presets for Easy Demo Testing */}
        <div className="pt-1">
          <p className="text-[11px] font-medium text-slate-400 mb-1.5 flex items-center justify-between">
            <span>Quick Goa landmarks:</span>
            <span className="text-[10px] text-slate-500 font-mono">10 locations available</span>
          </p>
          <div className="flex flex-wrap gap-1.5">
            {GOA_LANDMARKS.slice(0, 5).map((loc) => (
              <button
                key={loc.id}
                type="button"
                onClick={() => {
                  if (!origin || !originLandmark) handleQuickSelectOrigin(loc);
                  else handleQuickSelectDest(loc);
                }}
                className="text-[11px] px-2 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/90 text-slate-300 hover:text-white border border-slate-700/50 transition-colors cursor-pointer"
              >
                + {loc.name}
              </button>
            ))}
          </div>
        </div>

        {/* Route Preference (Fastest vs Shortest) */}
        <div className="pt-2">
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Routing Preference:
          </label>
          <div className="grid grid-cols-2 gap-2.5">
            {/* Fastest Route Option */}
            <button
              type="button"
              onClick={() => setPreference('fastest')}
              className={`p-3 rounded-xl border text-left transition-all relative cursor-pointer ${
                preference === 'fastest'
                  ? 'bg-cyan-950/40 border-cyan-500/80 text-white shadow-md shadow-cyan-950/30 ring-1 ring-cyan-500/40'
                  : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className={`p-1 rounded-md ${preference === 'fastest' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>
                  <Zap className="w-3.5 h-3.5" />
                </div>
                <span className="text-xs font-bold">Fastest Route</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Prioritizes less travel time & open bypasses.
              </p>
            </button>

            {/* Shortest Route Option */}
            <button
              type="button"
              onClick={() => setPreference('shortest')}
              className={`p-3 rounded-xl border text-left transition-all relative cursor-pointer ${
                preference === 'shortest'
                  ? 'bg-blue-950/40 border-blue-500/80 text-white shadow-md shadow-blue-950/30 ring-1 ring-blue-500/40'
                  : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className={`p-1 rounded-md ${preference === 'shortest' ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-400'}`}>
                  <Ruler className="w-3.5 h-3.5" />
                </div>
                <span className="text-xs font-bold">Shortest Route</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Prioritizes minimum physical distance.
              </p>
            </button>
          </div>
        </div>

        {/* Action Buttons: Find Route & Reset */}
        <div className="flex items-center gap-2.5 pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold py-2.5 px-4 rounded-xl shadow-lg shadow-cyan-500/25 active:scale-[0.98] transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                <span>Computing Route...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Find Route</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={onReset}
            title="Reset Form"
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700/80 transition-all cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
