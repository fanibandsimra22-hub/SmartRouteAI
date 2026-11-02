/**
 * MapPlaceholder.jsx
 * 
 * Interactive Navigation Map Canvas (Leaflet.js + OpenStreetMap)
 * 
 * Features:
 * - Real interactive OpenStreetMap tiles with dark/standard mode
 * - Draggable Starting Marker (A, green) and Destination Marker (B, red)
 * - Map point selection by clicking anywhere on the map with active mode banner
 * - Cancel selection button
 * - Return to Default Goa regional map view (Requirement 4)
 * - Auto-fit route bounds on marker/coordinate change
 * - Straight-line dashed preview for arbitrary coordinates vs simulated corridor polyline
 * - MapControls component integration
 */

import React, { useEffect, useState } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  Marker, 
  Popup, 
  Polyline, 
  useMap,
  useMapEvents 
} from 'react-leaflet';
import L from 'leaflet';
import { 
  MousePointerClick,
  X,
  Move
} from 'lucide-react';
import MapControls from './MapControls';
import { DEFAULT_GOA_CENTER, DEFAULT_GOA_ZOOM } from '../data/goaLandmarks';

// Custom Leaflet DivIcon for Starting Location (Green Pin "A")
const originIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div class="custom-marker-pin-origin cursor-grab active:cursor-grabbing" title="Drag to adjust Starting Location (A)">A</div>`,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
  popupAnchor: [0, -20],
});

// Custom Leaflet DivIcon for Destination (Red Pin "B")
const destinationIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div class="custom-marker-pin-destination cursor-grab active:cursor-grabbing" title="Drag to adjust Destination Point (B)">B</div>`,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
  popupAnchor: [0, -20],
});

// Custom Leaflet DivIcon for User's Real-time GPS Location
const userLocationIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div class="relative flex items-center justify-center">
    <div class="w-4 h-4 bg-cyan-400 rounded-full border-2 border-white shadow-lg ring-4 ring-cyan-500/30"></div>
    <div class="absolute w-8 h-8 bg-cyan-400 rounded-full animate-ping opacity-40"></div>
  </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -16],
});

/**
 * Handles map click events when in location selection mode
 */
function MapClickHandler({ selectionMode, onMapClick }) {
  useMapEvents({
    click: (e) => {
      if (selectionMode) {
        onMapClick([e.latlng.lat, e.latlng.lng]);
      }
    },
  });
  return null;
}

/**
 * Helper component that interacts with the Leaflet map instance.
 * Handles auto-fit bounds, zoom controls, recenter, and reset to default Goa view.
 */
function MapController({ 
  originCoords, 
  destinationCoords, 
  pathCoordinates, 
  triggerRecenter, 
  triggerResetGoa,
  triggerZoomIn, 
  triggerZoomOut 
}) {
  const map = useMap();

  // Auto-fit route bounds whenever the path coordinates or markers update
  useEffect(() => {
    if (pathCoordinates && pathCoordinates.length > 1) {
      const bounds = L.latLngBounds(pathCoordinates);
      map.fitBounds(bounds, {
        padding: [60, 60],
        maxZoom: 15,
        animate: true,
      });
    } else if (originCoords && destinationCoords) {
      const bounds = L.latLngBounds([originCoords, destinationCoords]);
      map.fitBounds(bounds, {
        padding: [60, 60],
        maxZoom: 15,
        animate: true,
      });
    } else if (originCoords) {
      map.setView(originCoords, 13);
    }
  }, [map, pathCoordinates, originCoords, destinationCoords]);

  // Handle external recenter trigger (fits current route)
  useEffect(() => {
    if (triggerRecenter > 0) {
      if (pathCoordinates && pathCoordinates.length > 1) {
        const bounds = L.latLngBounds(pathCoordinates);
        map.fitBounds(bounds, { padding: [60, 60], animate: true });
      } else if (originCoords && destinationCoords) {
        const bounds = L.latLngBounds([originCoords, destinationCoords]);
        map.fitBounds(bounds, { padding: [60, 60], animate: true });
      } else if (originCoords) {
        map.setView(originCoords, 13);
      }
    }
  }, [map, triggerRecenter, pathCoordinates, originCoords, destinationCoords]);

  // Handle Return to Default Goa Regional Map View (Requirement 4)
  useEffect(() => {
    if (triggerResetGoa > 0) {
      map.setView(DEFAULT_GOA_CENTER, DEFAULT_GOA_ZOOM, {
        animate: true,
        duration: 0.8
      });
    }
  }, [map, triggerResetGoa]);

  // Handle external zoom controls
  useEffect(() => {
    if (triggerZoomIn > 0) map.zoomIn();
  }, [map, triggerZoomIn]);

  useEffect(() => {
    if (triggerZoomOut > 0) map.zoomOut();
  }, [map, triggerZoomOut]);

  return null;
}

export default function MapPlaceholder({ 
  origin = 'Panaji', 
  destination = 'Goa University', 
  originCoords = [15.4989, 73.8278],
  destinationCoords = [15.4578, 73.8335],
  preference = 'fastest', 
  hasCalculated = true,
  routeData = null,
  selectionMode = null, // null | 'origin' | 'destination'
  onSetSelectionMode,
  onMapClickPoint,
  onMarkerDragOrigin,
  onMarkerDragDestination,
  userLocation = null
}) {
  const activeRoute = routeData;
  const pathCoordinates = activeRoute?.pathCoordinates || [];
  const isStraightLine = activeRoute?.isStraightLine || false;

  // Initial center point between origin and destination
  const initialMapCenter = originCoords && destinationCoords
    ? [(originCoords[0] + destinationCoords[0]) / 2, (originCoords[1] + destinationCoords[1]) / 2]
    : DEFAULT_GOA_CENTER;

  // Tile Layer State (Standard OpenStreetMap vs Voyager Dark)
  const [tileMode, setTileMode] = useState('osm'); // 'osm' | 'dark'

  // Traffic flow visualization toggle
  const [showTrafficOverlay, setShowTrafficOverlay] = useState(false);

  // Trigger counters for Leaflet MapController actions
  const [recenterCount, setRecenterCount] = useState(0);
  const [resetGoaCount, setResetGoaCount] = useState(0);
  const [zoomInCount, setZoomInCount] = useState(0);
  const [zoomOutCount, setZoomOutCount] = useState(0);

  return (
    <div className="relative w-full h-[540px] lg:h-full min-h-[500px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl flex flex-col justify-between">
      {/* Real Interactive Leaflet Map Canvas */}
      <div className={`absolute inset-0 z-0 ${selectionMode ? 'cursor-crosshair' : ''}`}>
        <MapContainer
          center={initialMapCenter}
          zoom={DEFAULT_GOA_ZOOM}
          scrollWheelZoom={true}
          dragging={true}
          zoomControl={false}
          className="w-full h-full"
        >
          {/* Map Click Listener for placing markers */}
          <MapClickHandler
            selectionMode={selectionMode}
            onMapClick={onMapClickPoint}
          />

          {/* Map Controller for programmatic movement and recentering */}
          <MapController
            originCoords={originCoords}
            destinationCoords={destinationCoords}
            pathCoordinates={hasCalculated ? pathCoordinates : []}
            triggerRecenter={recenterCount}
            triggerResetGoa={resetGoaCount}
            triggerZoomIn={zoomInCount}
            triggerZoomOut={zoomOutCount}
          />

          {/* Real OpenStreetMap TileLayer with official attribution */}
          {tileMode === 'osm' ? (
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />
          ) : (
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              maxZoom={19}
            />
          )}

          {/* User's Real-time GPS Location Indicator */}
          {userLocation && (
            <Marker position={userLocation} icon={userLocationIcon}>
              <Popup>
                <div className="text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                    <span>Your Current GPS Location</span>
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    GPS: {userLocation[0].toFixed(5)}° N, {userLocation[1].toFixed(5)}° E
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Starting Location Marker (A) - DRAGGABLE */}
          {originCoords && (
            <Marker 
              position={originCoords} 
              icon={originIcon}
              draggable={true}
              eventHandlers={{
                dragend: (e) => {
                  const latlng = e.target.getLatLng();
                  if (onMarkerDragOrigin) {
                    onMarkerDragOrigin([latlng.lat, latlng.lng]);
                  }
                }
              }}
            >
              <Popup>
                <div className="text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span>Origin (Start Point)</span>
                  </div>
                  <div className="font-semibold text-slate-100">{origin || 'Selected Origin'}</div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    GPS: {originCoords[0].toFixed(4)}° N, {originCoords[1].toFixed(4)}° E
                  </div>
                  <div className="text-[10px] text-emerald-300 font-medium pt-1 border-t border-slate-800 flex items-center gap-1">
                    <Move className="w-3 h-3 text-emerald-400" />
                    <span>Draggable: Hold & move anywhere!</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Destination Marker (B) - DRAGGABLE */}
          {destinationCoords && (
            <Marker 
              position={destinationCoords} 
              icon={destinationIcon}
              draggable={true}
              eventHandlers={{
                dragend: (e) => {
                  const latlng = e.target.getLatLng();
                  if (onMarkerDragDestination) {
                    onMarkerDragDestination([latlng.lat, latlng.lng]);
                  }
                }
              }}
            >
              <Popup>
                <div className="text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-rose-400">
                    <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                    <span>Destination Point</span>
                  </div>
                  <div className="font-semibold text-slate-100">{destination || 'Selected Destination'}</div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    GPS: {destinationCoords[0].toFixed(4)}° N, {destinationCoords[1].toFixed(4)}° E
                  </div>
                  <div className="text-[10px] text-rose-300 font-medium pt-1 border-t border-slate-800 flex items-center gap-1">
                    <Move className="w-3 h-3 text-rose-400" />
                    <span>Draggable: Hold & move anywhere!</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Route Polyline (Either simulated corridor or straight-line preview) */}
          {hasCalculated && pathCoordinates.length > 0 && activeRoute && (
            <Polyline
              positions={pathCoordinates}
              pathOptions={{
                color: showTrafficOverlay
                  ? activeRoute.trafficLevel === 'low' ? '#10b981' : activeRoute.trafficLevel === 'moderate' ? '#f59e0b' : '#ef4444'
                  : activeRoute.routeColor || (preference === 'fastest' ? '#06b6d4' : '#3b82f6'),
                weight: isStraightLine ? 4 : 5,
                opacity: 0.9,
                dashArray: isStraightLine ? '8, 8' : undefined,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            >
              <Popup>
                <div className="text-xs space-y-1">
                  <div className="font-bold text-cyan-400">{activeRoute.preferenceName}</div>
                  <div className="text-slate-200">Distance: {activeRoute.distanceKm}</div>
                  <div className="text-slate-200">Est. Time: {activeRoute.estimatedTimeMin} mins</div>
                  <div className="text-[10px] text-amber-300 font-medium">
                    {isStraightLine 
                      ? 'Straight-Line Direct Preview (Haversine Formula)'
                      : `Simulated demo polyline (${origin} ➔ ${destination})`}
                  </div>
                </div>
              </Popup>
            </Polyline>
          )}
        </MapContainer>
      </div>

      {/* Top Map Toolbar: Selection Controls & Layer Switches */}
      <div className="relative z-20 p-3 sm:p-4 flex flex-col gap-2.5 pointer-events-none">
        <div className="flex flex-wrap items-center justify-between gap-2.5">
          {/* Map Click Selection Buttons (Requirement 1 & 6) */}
          <div className="pointer-events-auto flex items-center gap-1.5 bg-slate-900/95 border border-slate-700/80 backdrop-blur-md p-1.5 rounded-xl shadow-xl">
            {/* Select Starting Point Button */}
            <button
              type="button"
              onClick={() => onSetSelectionMode(selectionMode === 'origin' ? null : 'origin')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                selectionMode === 'origin'
                  ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/30 ring-2 ring-emerald-400'
                  : 'bg-slate-800/80 text-emerald-400 hover:bg-slate-700/90 hover:text-white'
              }`}
              title="Click here, then click map to set Starting Location"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Select Starting Point</span>
            </button>

            {/* Select Destination Button */}
            <button
              type="button"
              onClick={() => onSetSelectionMode(selectionMode === 'destination' ? null : 'destination')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                selectionMode === 'destination'
                  ? 'bg-rose-500 text-white shadow-md shadow-rose-500/30 ring-2 ring-rose-400'
                  : 'bg-slate-800/80 text-rose-400 hover:bg-slate-700/90 hover:text-white'
              }`}
              title="Click here, then click map to set Destination Point"
            >
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse"></span>
              <span>Select Destination</span>
            </button>
          </div>

          {/* Map Tile Layer Selector */}
          <div className="pointer-events-auto flex items-center gap-1 bg-slate-900/90 border border-slate-700/80 backdrop-blur-md p-1 rounded-xl shadow-xl text-xs">
            <button
              type="button"
              onClick={() => setTileMode('osm')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                tileMode === 'osm'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              OSM Standard
            </button>
            <button
              type="button"
              onClick={() => setTileMode('dark')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                tileMode === 'dark'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              OSM Voyager
            </button>
          </div>
        </div>

        {/* Active Selection Mode Banner with Cancel button (Requirements 6, 10 & 11) */}
        {selectionMode && (
          <div className="pointer-events-auto flex items-center justify-between gap-3 bg-cyan-950/95 border-2 border-cyan-400 px-4 py-2.5 rounded-xl shadow-2xl backdrop-blur-md animate-pulse">
            <div className="flex items-center gap-2 text-xs text-white">
              <MousePointerClick className="w-4 h-4 text-cyan-300 animate-bounce" />
              <span>
                <strong>Selection Mode Active:</strong> Click or tap anywhere on the map to set{' '}
                <span className={selectionMode === 'origin' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                  {selectionMode === 'origin' ? 'Starting Point (Marker A)' : 'Destination Point (Marker B)'}
                </span>
              </span>
            </div>
            <button
              type="button"
              onClick={() => onSetSelectionMode(null)}
              className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-semibold flex items-center gap-1 border border-slate-600 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Cancel</span>
            </button>
          </div>
        )}
      </div>

      {/* Bottom Map Controls & Legend Overlay */}
      <div className="relative z-20 p-4 flex items-end justify-between pointer-events-none">
        {/* Map Legend */}
        <div className="pointer-events-auto bg-slate-900/95 border border-slate-800 backdrop-blur-md px-3.5 py-2.5 rounded-xl text-[11px] space-y-1.5 shadow-2xl hidden sm:block max-w-xs">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center justify-between gap-4">
            <span>Route Map Legend</span>
            <span className="text-emerald-400 font-mono text-[9px]">DRAGGABLE PINS</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300 truncate">
            <span className="w-3 h-3 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold text-[8px] shrink-0">A</span>
            <span className="truncate">Start: {origin || 'Point A'}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300 truncate">
            <span className="w-3 h-3 rounded-full bg-rose-500 text-white flex items-center justify-center font-bold text-[8px] shrink-0">B</span>
            <span className="truncate">End: {destination || 'Point B'}</span>
          </div>
          {activeRoute && (
            <div className="flex items-center gap-2 text-slate-300 pt-0.5 border-t border-slate-800">
              <span 
                className={`w-4 h-1 rounded shrink-0 ${isStraightLine ? 'border-t-2 border-dashed border-cyan-400' : ''}`}
                style={{ backgroundColor: isStraightLine ? 'transparent' : (activeRoute.routeColor || '#06b6d4') }}
              ></span>
              <span className="truncate">
                {isStraightLine 
                  ? `Straight-Line Preview (${activeRoute.distanceKm})` 
                  : `${activeRoute.preferenceName} (${activeRoute.distanceKm})`}
              </span>
            </div>
          )}
        </div>

        {/* Floating Custom Map Controls Component */}
        <MapControls
          onZoomIn={() => setZoomInCount((c) => c + 1)}
          onZoomOut={() => setZoomOutCount((c) => c + 1)}
          onRecenterRoute={() => setRecenterCount((c) => c + 1)}
          onResetToGoaView={() => setResetGoaCount((c) => c + 1)}
          tileMode={tileMode}
          onSetTileMode={setTileMode}
          showTrafficOverlay={showTrafficOverlay}
          onToggleTrafficOverlay={() => setShowTrafficOverlay(!showTrafficOverlay)}
        />
      </div>
    </div>
  );
}
