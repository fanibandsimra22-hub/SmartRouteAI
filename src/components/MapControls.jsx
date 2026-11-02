/**
 * MapControls.jsx
 * 
 * Floating Interactive Map Controls for SmartRoute AI
 * 
 * Provides:
 * - Zoom in / Zoom out buttons
 * - Recenter map to route bounds
 * - Return to Default Goa regional map view (Requirement 4)
 * - Map Tile Layer toggle (OSM Standard vs Dark Voyager)
 * - Simulated traffic layer toggle
 */

import React from 'react';
import { 
  Plus, 
  Minus, 
  LocateFixed, 
  Compass, 
  Layers,
  Activity 
} from 'lucide-react';

export default function MapControls({
  onZoomIn,
  onZoomOut,
  onRecenterRoute,
  onResetToGoaView,
  tileMode,
  onSetTileMode,
  showTrafficOverlay,
  onToggleTrafficOverlay
}) {
  return (
    <div className="pointer-events-auto flex flex-col gap-2">
      {/* Zoom and Navigation Controls Card */}
      <div className="bg-slate-900/95 border border-slate-700/80 backdrop-blur-md rounded-xl p-1 shadow-2xl flex flex-col gap-1">
        {/* Zoom In */}
        <button
          type="button"
          onClick={onZoomIn}
          title="Zoom In"
          aria-label="Zoom in on map"
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
        </button>

        <div className="h-[1px] bg-slate-800 mx-1"></div>

        {/* Zoom Out */}
        <button
          type="button"
          onClick={onZoomOut}
          title="Zoom Out"
          aria-label="Zoom out of map"
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
        >
          <Minus className="w-4 h-4" />
        </button>
      </div>

      {/* Recenter, Reset to Goa, & Layer Mode Buttons */}
      <div className="bg-slate-900/95 border border-slate-700/80 backdrop-blur-md rounded-xl p-1 shadow-2xl flex flex-col gap-1">
        {/* Recenter on Route */}
        <button
          type="button"
          onClick={onRecenterRoute}
          title="Recenter Map to Fit Selected Route"
          aria-label="Fit route within map view"
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-cyan-400 transition-all cursor-pointer"
        >
          <LocateFixed className="w-4 h-4" />
        </button>

        <div className="h-[1px] bg-slate-800 mx-1"></div>

        {/* Return to Default Goa Map View (Requirement 4) */}
        <button
          type="button"
          onClick={onResetToGoaView}
          title="Return to Default Goa Regional View"
          aria-label="Reset map to default Goa view"
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-emerald-400 transition-all cursor-pointer flex items-center justify-center group relative"
        >
          <Compass className="w-4 h-4 group-hover:rotate-45 transition-transform" />
        </button>

        {onSetTileMode && (
          <>
            <div className="h-[1px] bg-slate-800 mx-1"></div>
            {/* Tile Layer Style Toggle */}
            <button
              type="button"
              onClick={() => onSetTileMode(tileMode === 'osm' ? 'dark' : 'osm')}
              title={tileMode === 'osm' ? "Switch to Dark Voyager Map" : "Switch to OSM Standard Map"}
              aria-label="Toggle map style"
              className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-cyan-400 transition-all cursor-pointer"
            >
              <Layers className="w-4 h-4" />
            </button>
          </>
        )}
      </div>

      {/* Traffic Flow Overlay Toggle */}
      {onToggleTrafficOverlay && (
        <button
          type="button"
          onClick={onToggleTrafficOverlay}
          title={showTrafficOverlay ? "Hide Traffic Flow Overlay" : "Show Traffic Flow Overlay"}
          aria-label="Toggle simulated traffic overlay"
          className={`p-2 rounded-xl border backdrop-blur-md shadow-2xl transition-all cursor-pointer flex items-center justify-center ${
            showTrafficOverlay
              ? 'bg-amber-950/80 border-amber-500/80 text-amber-300 ring-1 ring-amber-500/40'
              : 'bg-slate-900/95 border-slate-700/80 text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Activity className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
