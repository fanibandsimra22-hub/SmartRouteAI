/**
 * Header.jsx
 * 
 * Main Navigation Header & BTech Project Architecture Showcase
 * 
 * Displays:
 * - SmartRoute AI logo and branding
 * - System status indicators
 * - Architecture & AI pipeline modal showing future integration:
 *   FastAPI, OSMnx, NetworkX, AI search algorithms (A*, BFS, UCS, Greedy), TomTom Traffic API, MongoDB Atlas
 */

import React, { useState } from 'react';
import { 
  Navigation, 
  Cpu, 
  Database, 
  Network, 
  X,
  CheckCircle2,
  Bookmark
} from 'lucide-react';

export default function Header({ onOpenSavedRoutes }) {
  const [showArchModal, setShowArchModal] = useState(false);

  return (
    <>
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50 px-4 lg:px-8 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          {/* Brand & Logo */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
              <Navigation className="h-5 w-5 transform -rotate-45" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  SmartRoute <span className="text-cyan-400">AI</span>
                </span>
                <span className="hidden sm:inline-block text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
                  Goa Region
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                AI-Powered Real-World City Navigation System
              </p>
            </div>
          </div>

          {/* Right side status indicators & Architecture Info Button */}
          <div className="flex items-center gap-2.5">
            {onOpenSavedRoutes && (
              <button
                type="button"
                onClick={onOpenSavedRoutes}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold transition-all cursor-pointer shadow-sm"
                title="Open Saved Routes and Query History from MongoDB Atlas"
              >
                <Bookmark className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Saved & History</span>
                <span className="sm:hidden">Saved</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowArchModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/70 hover:bg-cyan-900/80 text-cyan-300 hover:text-white border border-cyan-800/60 text-xs font-semibold transition-all cursor-pointer shadow-sm shadow-cyan-950/30"
              title="View BTech Project Architecture & AI Pipeline"
            >
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden sm:inline">Project Architecture</span>
              <span className="sm:hidden">Info</span>
            </button>

            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-medium text-emerald-300">AI Engine Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* BTech Project Architecture & Backend Pipeline Modal */}
      {showArchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700/90 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto custom-scrollbar">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">SmartRoute AI &bull; System Architecture</h3>
                  <p className="text-xs text-slate-400">B.Tech Final Year Engineering Project Roadmap</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowArchModal(false)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Architecture Flow Breakdown */}
            <div className="space-y-4 text-xs text-slate-300">
              {/* Frontend Layer (Current) */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-cyan-900/50 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-300 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    Layer 1: Interactive Frontend (Current State)
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">COMPLETE</span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  Built with React 19, Vite, Tailwind CSS v4, and Leaflet.js. Features full Goa landmark autocomplete, map click location selection, draggable starting & destination pins, Haversine formula distance calculation, and simulated route previews.
                </p>
              </div>

              {/* Backend Layer (Upcoming) */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <Network className="w-3.5 h-3.5 text-blue-400" />
                    Layer 2: Python FastAPI & AI Graph Traversal (Phase 2)
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono">READY TO CONNECT</span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  The frontend services (<code className="text-cyan-300">routeService.js</code> and <code className="text-cyan-300">locationService.js</code>) are prepared to call FastAPI REST endpoints. The backend will load real road graphs via <strong>OSMnx</strong> and <strong>NetworkX</strong>.
                </p>
                <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="font-semibold text-slate-200 block mb-0.5">Automated AI Algorithms:</span>
                    <span className="text-slate-400">A* Search (default), UCS, Greedy Best First Search, BFS, and Hill Climbing. (Selected automatically by backend based on preference).</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="font-semibold text-slate-200 block mb-0.5">Real Traffic Integration:</span>
                    <span className="text-slate-400">TomTom Traffic Flow API streaming real-time edge travel times into NetworkX graph weights.</span>
                  </div>
                </div>
              </div>

              {/* Database Layer */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-purple-400" />
                    Layer 3: MongoDB Atlas Spatial Cache
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono">PHASE 2</span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  Stores user query history, precomputed landmark graph subnets, and cached traffic profiles with 2dsphere geographic indexes for fast query resolution.
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-800 mt-5 pt-3.5 flex justify-end">
              <button
                type="button"
                onClick={() => setShowArchModal(false)}
                className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors cursor-pointer"
              >
                Close Architecture Overview
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
