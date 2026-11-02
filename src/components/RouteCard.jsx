/**
 * RouteCard.jsx
 * 
 * Interactive Route Option Comparison Card
 * 
 * Allows users to visually compare and toggle between "Fastest Route" and "Shortest Route".
 * Displays estimated time, distance, fuel savings, and traffic condition tags.
 */

import React from 'react';
import { Zap, Ruler, Fuel, CheckCircle2 } from 'lucide-react';

export default function RouteCard({
  route,
  isSelected,
  onSelect
}) {
  if (!route) return null;

  const {
    preference,
    preferenceName,
    distanceKm,
    estimatedTimeMin,
    estimatedFuelLiters,
    isStraightLine,
    trafficLevel
  } = route;

  const isFastest = preference === 'fastest';

  return (
    <div
      onClick={onSelect}
      className={`relative p-3.5 rounded-xl border transition-all cursor-pointer text-left select-none ${
        isSelected
          ? isFastest
            ? 'bg-cyan-950/40 border-cyan-500 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-500/50'
            : 'bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-950/40 ring-1 ring-blue-500/50'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/90'
      }`}
    >
      {/* Top Row: Badge & Active Indicator */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <div
            className={`p-1 rounded-md ${
              isFastest
                ? 'bg-cyan-500/20 text-cyan-400'
                : 'bg-blue-500/20 text-blue-400'
            }`}
          >
            {isFastest ? <Zap className="w-3.5 h-3.5" /> : <Ruler className="w-3.5 h-3.5" />}
          </div>
          <span className="text-xs font-bold text-white tracking-tight">
            {preferenceName}
          </span>
        </div>

        {isSelected ? (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5" /> Selected
          </span>
        ) : (
          <span className="text-[10px] text-slate-500 font-medium">Click to select</span>
        )}
      </div>

      {/* Main Metrics: Time & Distance */}
      <div className="flex items-baseline justify-between gap-2 my-1.5">
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-extrabold text-white tracking-tight">
            {estimatedTimeMin}
          </span>
          <span className="text-xs font-semibold text-slate-400">mins</span>
        </div>

        <div className="text-right">
          <span className="text-sm font-bold text-slate-200">
            {distanceKm}
          </span>
        </div>
      </div>

      {/* Subtext info / Traffic preview badge */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1">
          <Fuel className="w-3 h-3 text-emerald-400" />
          <span>~{estimatedFuelLiters}</span>
        </span>

        {isStraightLine ? (
          <span className="text-[10px] text-sky-400 font-mono">Haversine Vector</span>
        ) : trafficLevel === 'low' ? (
          <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Free Flow
          </span>
        ) : (
          <span className="text-[10px] text-amber-400 font-medium flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span> Moderate
          </span>
        )}
      </div>
    </div>
  );
}
