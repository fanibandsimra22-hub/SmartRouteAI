/**
 * RouteResults.jsx
 * 
 * Complete Route Results & Information Panel for SmartRoute AI
 * 
 * Features:
 * - Side-by-side or stacked interactive RouteCards for Fastest vs Shortest route comparison
 * - Route Information Panel displaying real-world road network verification badge
 * - Turn-by-Turn itinerary preview from genuine OSM road network
 * - Embedded Traffic Information section (TrafficPanel)
 * - Save Route bookmarking to MongoDB Atlas
 */

import React, { useState } from 'react';
import { 
  Clock, 
  Milestone, 
  Gauge, 
  Fuel, 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  Ruler, 
  Layers, 
  ListOrdered,
  Bookmark
} from 'lucide-react';
import RouteCard from './RouteCard';
import TrafficPanel from './TrafficPanel';
import { saveRouteToBackend } from '../services/routeService';

export default function RouteResults({ 
  routeOptions, // { fastest, shortest, active, activePreference }
  origin, 
  destination, 
  preference, 
  onSelectPreference 
}) {
  const [isSaved, setIsSaved] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  if (!routeOptions || !routeOptions.active) {
    return (
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center text-slate-400">
        <Info className="w-8 h-8 mx-auto mb-2 text-slate-500" />
        <p className="text-sm font-medium">Select locations and click "Find Route" to calculate path.</p>
        <p className="text-xs text-slate-500 mt-1">Ready to render real-world road routing metrics.</p>
      </div>
    );
  }

  const { fastest, shortest, active } = routeOptions;
  const isStraightLine = active.isStraightLine || false;
  const isRealRoad = active.routeType === 'road_network' && !active.isSimulated && !isStraightLine;

  const handleSaveRoute = async () => {
    setSaveLoading(true);
    setSaveMessage('');
    try {
      await saveRouteToBackend({
        originName: origin,
        originCoords: active.originCoords,
        destinationName: destination,
        destinationCoords: active.destinationCoords,
        preference: active.preference,
        distanceKm: active.numericDistanceKm,
        estimatedTimeMin: active.estimatedTimeMin
      });
      setIsSaved(true);
      setSaveMessage('Saved to MongoDB Atlas!');
      setTimeout(() => setSaveMessage(''), 3500);
    } catch (err) {
      alert(`Could not save route: ${err.message}`);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Route Options Comparison Cards */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Select Route Option:</span>
          </label>
          <span className="text-[10px] text-slate-500 font-medium">
            Click card to switch map path
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          <RouteCard
            route={fastest}
            isSelected={preference === 'fastest'}
            onSelect={() => onSelectPreference('fastest')}
          />
          <RouteCard
            route={shortest}
            isSelected={preference === 'shortest'}
            onSelect={() => onSelectPreference('shortest')}
          />
        </div>
      </div>

      {/* Main Route Information Panel */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-md space-y-3.5">
        {/* Status Notice / Verification Badge */}
        {isRealRoad ? (
          <div className="rounded-xl px-3.5 py-2.5 flex items-start gap-2.5 border bg-emerald-500/10 border-emerald-500/30 text-emerald-200">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-emerald-300">
                  REAL OPENSTREETMAP DRIVING NETWORK
                </span>
                <span className="text-[10px] px-1.5 py-0.2 rounded font-semibold bg-emerald-400/20 text-emerald-200 font-mono">
                  {active.algorithmUsed || 'A*'}
                </span>
              </div>
              <p className="text-[11px] mt-0.5 leading-snug opacity-90">
                Connected via <strong>{active.pathCoordinates?.length || 0} road-network coordinate points</strong>.
                Traversing genuine Goa urban highways and street networks. Distances and travel times are derived from actual road edges.
              </p>
            </div>
          </div>
        ) : (
          <div className={`rounded-xl px-3.5 py-2.5 flex items-start gap-2.5 border ${
            isStraightLine
              ? 'bg-sky-500/10 border-sky-500/30 text-sky-200'
              : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
          }`}>
            {isStraightLine ? (
              <Ruler className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold ${isStraightLine ? 'text-sky-300' : 'text-amber-300'}`}>
                  {isStraightLine ? 'STRAIGHT-LINE DIRECT PREVIEW' : 'SIMULATED DEMO CORRIDOR (GOA)'}
                </span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                  isStraightLine ? 'bg-sky-400/20 text-sky-200' : 'bg-amber-400/20 text-amber-200'
                }`}>
                  {isStraightLine ? 'Haversine Metric' : 'Simulation Only'}
                </span>
              </div>
              <p className="text-[11px] mt-0.5 leading-snug opacity-90">
                {isStraightLine ? (
                  <>
                    Custom map coordinates are active between <strong>{origin}</strong> and <strong>{destination}</strong>. The distance shown is <strong>direct straight-line distance</strong> (Haversine formula).
                  </>
                ) : (
                  <>
                    This route is a verified simulated corridor connecting <strong>{origin}</strong> and <strong>{destination}</strong>. Start FastAPI backend to compute live OSMnx graph paths.
                  </>
                )}
              </p>
            </div>
          </div>
        )}

        {/* Route Header Info with Save Route Bookmark Button */}
        <div className="border-b border-slate-800 pb-3 flex items-center justify-between gap-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white truncate">{active.preferenceName}</h3>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 shrink-0">
                {preference === 'fastest' ? '⚡ Speed Priority' : '📏 Distance Priority'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 truncate">
              {origin} <span className="text-cyan-400 font-bold">➔</span> {destination}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {/* Save Route Bookmark Button (MongoDB Atlas) */}
            <button
              type="button"
              onClick={handleSaveRoute}
              disabled={saveLoading || isSaved}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all cursor-pointer ${
                isSaved
                  ? 'bg-emerald-950/70 border-emerald-500/80 text-emerald-300'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200 hover:text-white'
              }`}
              title="Bookmark this route in MongoDB Atlas"
            >
              <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-emerald-400 text-emerald-400' : 'text-cyan-400'}`} />
              <span>{isSaved ? 'Saved in Atlas' : saveLoading ? 'Saving...' : 'Save Route'}</span>
            </button>
          </div>
        </div>

        {saveMessage && (
          <div className="p-2 rounded-lg bg-emerald-950/60 border border-emerald-500/50 text-xs text-emerald-300 text-center font-medium">
            {saveMessage}
          </div>
        )}

        {/* Primary Metrics: Time & Distance */}
        <div className="grid grid-cols-2 gap-3">
          {/* Estimated Travel Time */}
          <div className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-3">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Estimated Time</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-extrabold text-white tracking-tight">
                {active.estimatedTimeMin}
              </span>
              <span className="text-xs font-semibold text-slate-400">mins</span>
            </div>
            <span className="text-[10px] text-cyan-400 font-medium truncate block">
              {active.trafficStatusText || 'Standard road traffic'}
            </span>
          </div>

          {/* Distance */}
          <div className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-3">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <Milestone className="w-3.5 h-3.5 text-blue-400" />
              <span>Total Distance</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-extrabold text-white tracking-tight truncate">
                {active.distanceKm}
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-medium">
              {isRealRoad ? 'Road network length' : 'Calculated corridor length'}
            </span>
          </div>
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
            <Gauge className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-slate-400">Avg Speed</div>
              <div className="font-semibold text-slate-200 truncate">{active.avgSpeedKmh}</div>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
            <Fuel className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-slate-400">Est. Fuel Consumption</div>
              <div className="font-semibold text-slate-200">{active.estimatedFuelLiters}</div>
            </div>
          </div>
        </div>

        {/* Route Strategy Description */}
        <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/50 text-[11px] text-slate-300 leading-relaxed">
          <span className="text-cyan-400 font-semibold">Route Strategy: </span>
          {active.routeTypeDescription}
        </div>

        {/* Turn-by-Turn Waypoint Steps Preview */}
        <div>
          <h4 className="text-xs font-bold text-slate-300 mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <ListOrdered className="w-3.5 h-3.5 text-cyan-400" />
              <span>Turn-by-Turn Navigation ({active.itinerarySteps?.length || 0} steps)</span>
            </span>
            <span className="text-[10px] text-slate-500 font-normal">
              {active.algorithmUsed || 'A*'} guidance
            </span>
          </h4>
          <div className="space-y-1.5 max-h-56 overflow-y-auto custom-scrollbar pr-1">
            {active.itinerarySteps?.map((step, idx) => (
              <div 
                key={step.id || idx}
                className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-950/60 border border-slate-800/70 text-xs"
              >
                <span className="h-5 w-5 rounded-full bg-slate-800 text-slate-300 font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5 border border-slate-700">
                  {idx + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-slate-200 font-medium leading-snug">{step.instruction}</p>
                  <div className="flex items-center gap-2 mt-0.5 text-[10px] text-slate-400 font-mono">
                    <span>{step.distance}</span>
                    {step.time && step.time !== 'Arrival' && (
                      <>
                        <span>&bull;</span>
                        <span>{step.time}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Traffic Information Panel Section */}
      <TrafficPanel routeData={active} />
    </div>
  );
}
