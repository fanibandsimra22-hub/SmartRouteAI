/**
 * SavedRoutesModal.jsx
 * 
 * Interactive Saved Routes & History Modal for SmartRoute AI
 * Connects to MongoDB Atlas via FastAPI endpoints:
 * - GET /api/routes/saved
 * - DELETE /api/routes/saved/{id}
 * - GET /api/routes/history
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bookmark, 
  History, 
  Trash2, 
  ArrowRight, 
  Clock, 
  Milestone, 
  X, 
  RefreshCw,
  Database,
  ExternalLink
} from 'lucide-react';
import { 
  fetchSavedRoutesFromBackend, 
  deleteSavedRouteFromBackend, 
  fetchRouteHistoryFromBackend 
} from '../services/routeService';

export default function SavedRoutesModal({ isOpen, onClose, onLoadRoute }) {
  const [activeTab, setActiveTab] = useState('saved'); // 'saved' | 'history'
  const [savedRoutes, setSavedRoutes] = useState([]);
  const [historyRoutes, setHistoryRoutes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      if (activeTab === 'saved') {
        const data = await fetchSavedRoutesFromBackend();
        setSavedRoutes(Array.isArray(data) ? data : []);
      } else {
        const data = await fetchRouteHistoryFromBackend();
        setHistoryRoutes(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.warn('Could not load saved routes/history:', err.message);
      setErrorMsg('Could not connect to MongoDB Atlas backend. Ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    if (isOpen) {
      const t = setTimeout(() => {
        loadData();
      }, 0);
      return () => clearTimeout(t);
    }
  }, [isOpen, loadData]);

  const handleDelete = async (routeId, e) => {
    e.stopPropagation();
    try {
      await deleteSavedRouteFromBackend(routeId);
      setSavedRoutes((prev) => prev.filter((r) => r.id !== routeId));
    } catch (err) {
      alert(`Could not delete route: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-700/90 rounded-2xl max-w-xl w-full p-5 shadow-2xl relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>Saved Routes & History</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  MongoDB Atlas
                </span>
              </h3>
              <p className="text-[11px] text-slate-400">Manage bookmarks and review past navigation searches</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Toggle */}
        <div className="flex gap-2 mb-3 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            type="button"
            onClick={() => setActiveTab('saved')}
            className={`flex-1 py-1.5 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
              activeTab === 'saved'
                ? 'bg-cyan-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>Bookmarked Routes ({savedRoutes.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('history')}
            className={`flex-1 py-1.5 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
              activeTab === 'history'
                ? 'bg-cyan-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Search History ({historyRoutes.length})</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
          {isLoading ? (
            <div className="py-12 text-center text-slate-400 flex flex-col items-center gap-2">
              <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
              <span className="text-xs">Connecting to MongoDB Atlas...</span>
            </div>
          ) : errorMsg ? (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300 text-center">
              <p>{errorMsg}</p>
              <button
                type="button"
                onClick={loadData}
                className="mt-2 px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-semibold text-white transition-all cursor-pointer"
              >
                Retry Connection
              </button>
            </div>
          ) : activeTab === 'saved' ? (
            savedRoutes.length === 0 ? (
              <div className="py-10 text-center text-slate-400 space-y-1">
                <Bookmark className="w-8 h-8 mx-auto text-slate-600 mb-1" />
                <p className="text-xs font-medium text-slate-300">No bookmarked routes yet.</p>
                <p className="text-[11px] text-slate-500">Calculate a route and click "Save Route" to bookmark it to MongoDB.</p>
              </div>
            ) : (
              savedRoutes.map((route) => (
                <div
                  key={route.id}
                  onClick={() => {
                    onLoadRoute(route);
                    onClose();
                  }}
                  className="p-3 rounded-xl bg-slate-950/70 hover:bg-slate-800/70 border border-slate-800 hover:border-cyan-500/50 transition-all cursor-pointer group flex items-center justify-between gap-3"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-1">
                      <span className="truncate">{route.origin_name}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span className="truncate">{route.destination_name}</span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <Milestone className="w-3 h-3 text-blue-400" />
                        <span>{route.distance_km} km</span>
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-cyan-400" />
                        <span>{route.estimated_time_min} mins</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 uppercase font-mono">
                        {route.preference || 'fastest'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-[11px] font-semibold text-cyan-400 group-hover:underline flex items-center gap-0.5 mr-1">
                      <span>Load</span>
                      <ExternalLink className="w-3 h-3" />
                    </span>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(route.id, e)}
                      title="Delete bookmark"
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )
          ) : historyRoutes.length === 0 ? (
            <div className="py-10 text-center text-slate-400 space-y-1">
              <History className="w-8 h-8 mx-auto text-slate-600 mb-1" />
              <p className="text-xs font-medium text-slate-300">No search history recorded yet.</p>
              <p className="text-[11px] text-slate-500">Every route calculated via the backend is automatically logged here.</p>
            </div>
          ) : (
            historyRoutes.map((h, i) => (
              <div
                key={h._id || i}
                onClick={() => {
                  onLoadRoute({
                    origin_name: h.origin_name,
                    origin_coords: h.origin_coords,
                    destination_name: h.destination_name,
                    destination_coords: h.destination_coords,
                    preference: h.preference
                  });
                  onClose();
                }}
                className="p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/60 border border-slate-800/80 transition-all cursor-pointer flex items-center justify-between gap-3 text-xs"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5 font-semibold text-slate-200 truncate">
                    <span className="truncate">{h.origin_name || 'Origin'}</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                    <span className="truncate">{h.destination_name || 'Destination'}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-slate-400 mt-0.5">
                    <span>{h.distance_km} km</span>
                    <span>&bull;</span>
                    <span>{h.estimated_time_min} mins</span>
                    <span>&bull;</span>
                    <span className="text-cyan-400 font-mono">{h.algorithm_used || 'A*'}</span>
                  </div>
                </div>
                <span className="text-[10px] text-cyan-400 font-semibold shrink-0">
                  Reload
                </span>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-800 pt-3 mt-3 flex items-center justify-between text-[11px] text-slate-500">
          <span>Active mode: Single-user / Guest session</span>
          <button
            type="button"
            onClick={loadData}
            className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </div>
  );
}
