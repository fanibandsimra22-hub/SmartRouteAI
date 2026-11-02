/**
 * TrafficPanel.jsx
 * 
 * Traffic Information & Congestion Analytics Section
 * 
 * Displays traffic condition status, color-coded congestion legend, sample corridor
 * conditions, and clear notice indicating preparation for TomTom Traffic API integration.
 */

import React, { useState } from 'react';
import { 
  Activity, 
  Info, 
  ChevronDown, 
  ChevronUp
} from 'lucide-react';

export default function TrafficPanel({ routeData }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const trafficLevel = routeData?.trafficLevel || 'low';
  const isStraightLine = routeData?.isStraightLine || false;

  // Determine current active status
  let statusBadgeColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  let statusText = 'Low Traffic (Free Flow)';
  let delayMinutes = '+1 to 2 mins delay';

  if (trafficLevel === 'moderate') {
    statusBadgeColor = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    statusText = 'Moderate Congestion';
    delayMinutes = '+4 to 6 mins delay';
  } else if (trafficLevel === 'heavy') {
    statusBadgeColor = 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    statusText = 'Heavy Peak Congestion';
    delayMinutes = '+10 to 15 mins delay';
  } else if (isStraightLine) {
    statusBadgeColor = 'bg-sky-500/20 text-sky-300 border-sky-500/40';
    statusText = 'Map Vector (No Road Data)';
    delayMinutes = 'Straight-line estimate';
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-md space-y-3">
      {/* Header with expand toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/60">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>Traffic Information</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded font-mono bg-slate-800 text-slate-400 border border-slate-700">
                Sample Data
              </span>
            </h3>
            <p className="text-[10px] text-slate-400">
              Corridor congestion & flow preview
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1 px-2 py-1 rounded-md bg-slate-800/60 hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <span>{isExpanded ? 'Less' : 'Details'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Traffic Status Summary Bar */}
      <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="relative flex h-2.5 w-2.5 shrink-0">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              trafficLevel === 'low' ? 'bg-emerald-400' : trafficLevel === 'moderate' ? 'bg-amber-400' : 'bg-rose-400'
            }`}></span>
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
              trafficLevel === 'low' ? 'bg-emerald-500' : trafficLevel === 'moderate' ? 'bg-amber-500' : 'bg-rose-500'
            }`}></span>
          </span>
          <div className="truncate">
            <div className="text-xs font-bold text-slate-200 truncate">{statusText}</div>
            <div className="text-[10px] text-slate-400">{delayMinutes}</div>
          </div>
        </div>

        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border shrink-0 ${statusBadgeColor}`}>
          {isStraightLine ? 'Vector' : trafficLevel.toUpperCase()}
        </span>
      </div>

      {/* Traffic Legend (Requirement 8) */}
      <div className="grid grid-cols-3 gap-2 pt-1 text-center">
        <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/60 flex flex-col items-center">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/20"></span>
            <span className="text-[11px] font-bold text-emerald-400">Low</span>
          </div>
          <span className="text-[10px] text-slate-400">&gt; 35 km/h</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/60 flex flex-col items-center">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-amber-500/20"></span>
            <span className="text-[11px] font-bold text-amber-400">Moderate</span>
          </div>
          <span className="text-[10px] text-slate-400">20-35 km/h</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/60 flex flex-col items-center">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/20"></span>
            <span className="text-[11px] font-bold text-rose-400">Heavy</span>
          </div>
          <span className="text-[10px] text-slate-400">&lt; 20 km/h</span>
        </div>
      </div>

      {/* Expanded Details: Sample Corridor Insights & Future API Note */}
      {isExpanded && (
        <div className="pt-2 border-t border-slate-800 space-y-2.5 text-xs text-slate-300">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Sample Corridor Observations
            </span>
            <div className="space-y-1.5 text-[11px]">
              <div className="flex items-start gap-2 p-1.5 rounded-md bg-slate-950/50">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></span>
                <span><strong>Mandovi Riverfront / DB Marg:</strong> Free-flowing coastal corridor with unobstructed traffic signal coordination.</span>
              </div>
              <div className="flex items-start gap-2 p-1.5 rounded-md bg-slate-950/50">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></span>
                <span><strong>St. Inez Junction:</strong> Minor local congestion during standard peak morning/evening university commute hours.</span>
              </div>
            </div>
          </div>

          {/* Official API Disclaimer Notice (Requirement 8) */}
          <div className="p-2.5 rounded-xl bg-slate-950/80 border border-cyan-900/50 text-[11px] text-cyan-200/90 flex items-start gap-2">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-cyan-300">Live Traffic Architecture Note:</span>
              <p className="mt-0.5 text-[10px] text-slate-400 leading-snug">
                Live traffic integration is currently in prototype mode. In Phase 2, this section will automatically stream live vehicle speed matrices from the <strong>TomTom Traffic Flow & Incident API</strong> directly to the backend route weighting graph.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
