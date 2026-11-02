/**
 * App.jsx
 * 
 * Main Application Dashboard for SmartRoute AI
 * 
 * Orchestrates:
 * - Real-world AI navigation powered by Python FastAPI backend (A*, Dijkstra)
 * - Location search & landmark autocomplete (Nominatim + Curated Goa Index)
 * - Map location selection mode, GPS current location, and draggable pins
 * - Side-by-side comparison between Fastest and Shortest routes
 * - MongoDB Atlas saved route bookmarks and calculation history
 * - Interactive Leaflet map canvas with OpenStreetMap tiles & real road curves
 * - Responsive desktop & mobile layouts
 */

import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import RouteSearchForm from './components/RouteSearchForm';
import RouteResults from './components/RouteResults';
import MapPlaceholder from './components/MapPlaceholder';
import SavedRoutesModal from './components/SavedRoutesModal';
import { 
  findGoaLandmark, 
  reverseGeocodeLocal 
} from './services/locationService';
import { 
  calculateAllRouteOptions 
} from './services/routeService';
import { areCoordinatesEqual } from './utils/geoUtils';
import { SlidersHorizontal, Map, Info, X } from 'lucide-react';

export default function App() {
  // Default demo locations: Panaji Church Square and Goa University
  const defaultOriginLandmark = findGoaLandmark('Panaji');
  const defaultDestLandmark = findGoaLandmark('Goa University');

  // Input text & landmark state
  const [origin, setOrigin] = useState('Panaji');
  const [destination, setDestination] = useState('Goa University');
  const [originLandmark, setOriginLandmark] = useState(defaultOriginLandmark);
  const [destinationLandmark, setDestinationLandmark] = useState(defaultDestLandmark);

  // Exact GPS Coordinates state [latitude, longitude]
  const [originCoords, setOriginCoords] = useState(
    defaultOriginLandmark ? defaultOriginLandmark.coordinates : [15.4989, 73.8278]
  );
  const [destinationCoords, setDestinationCoords] = useState(
    defaultDestLandmark ? defaultDestLandmark.coordinates : [15.4578, 73.8335]
  );

  // Real-time GPS user position state
  const [userLocation, setUserLocation] = useState(null);
  const [geoNotice, setGeoNotice] = useState('');

  // Map selection mode: null | 'origin' | 'destination'
  const [selectionMode, setSelectionMode] = useState(null);

  // Routing preferences and computation state
  const [preference, setPreference] = useState('fastest'); // 'fastest' | 'shortest'
  const [isLoading, setIsLoading] = useState(false);
  const [hasCalculated, setHasCalculated] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [routeOptions, setRouteOptions] = useState(null);

  // Saved Routes Modal state
  const [showSavedModal, setShowSavedModal] = useState(false);
  
  // Mobile tab state: 'planner' or 'map'
  const [mobileTab, setMobileTab] = useState('planner');

  /**
   * Core route calculation function contacting the backend API
   */
  const computeRoute = useCallback(async (oCoords, dCoords, oName, dName, pref) => {
    if (!oCoords || !dCoords) return;
    setIsLoading(true);
    setValidationError('');
    try {
      const result = await calculateAllRouteOptions({
        originCoords: oCoords,
        destinationCoords: dCoords,
        originName: oName,
        destinationName: dName,
        activePreference: pref
      });
      setRouteOptions(result);
      setHasCalculated(true);
    } catch (err) {
      console.error('Route calculation error:', err);
      setValidationError(err.message || 'Could not calculate road route.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // On application startup, attempt automatic geolocation detection while loading baseline route
  useEffect(() => {
    let isCancelled = false;

    // Immediately compute initial baseline demo route so UI renders without delay
    computeRoute(originCoords, destinationCoords, origin, destination, preference);

    // Request user GPS permission via browser Geolocation API
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          if (isCancelled) return;
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          const userCoords = [lat, lng];

          setUserLocation(userCoords);
          setOrigin('My Current Location');
          setOriginCoords(userCoords);
          setOriginLandmark(null);
          setGeoNotice('Current GPS location detected. Starting point automatically set to "My Current Location".');

          computeRoute(userCoords, destinationCoords, 'My Current Location', destination, preference);
        },
        (err) => {
          if (isCancelled) return;
          console.info('Geolocation access not granted or unavailable:', err.message);
          setGeoNotice('Location access not granted. Defaulted starting point to Panaji. You can enter any location or pick on the map.');
        },
        { timeout: 8000, enableHighAccuracy: true, maximumAge: 60000 }
      );
    } else {
      setGeoNotice('Geolocation is not supported by your browser. Defaulted starting point to Panaji.');
    }

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Enter or exit map selection mode ('origin' or 'destination' or null).
   */
  const handleSetSelectionMode = (mode) => {
    setSelectionMode(mode);
    if (mode && mobileTab !== 'map') {
      setMobileTab('map');
    }
  };

  /**
   * Triggered when user clicks anywhere on map during selection mode
   */
  const handleMapClickPoint = (coords) => {
    const [lat, lng] = coords;
    const geocode = reverseGeocodeLocal(lat, lng);
    const label = geocode.formattedLabel;

    let newOriginCoords = originCoords;
    let newDestCoords = destinationCoords;
    let newOriginName = origin;
    let newDestName = destination;

    if (selectionMode === 'origin') {
      newOriginCoords = coords;
      newOriginName = label;
      setOriginCoords(coords);
      setOriginLandmark(geocode.isExactLandmark ? geocode.landmark : null);
      setOrigin(label);
    } else if (selectionMode === 'destination') {
      newDestCoords = coords;
      newDestName = label;
      setDestinationCoords(coords);
      setDestinationLandmark(geocode.isExactLandmark ? geocode.landmark : null);
      setDestination(label);
    }

    setSelectionMode(null);
    if (validationError) setValidationError('');
    computeRoute(newOriginCoords, newDestCoords, newOriginName, newDestName, preference);
  };

  /**
   * Triggered when user drags the green Starting Marker (A)
   */
  const handleMarkerDragOrigin = (coords) => {
    const [lat, lng] = coords;
    const geocode = reverseGeocodeLocal(lat, lng);
    const label = geocode.formattedLabel;
    setOriginCoords(coords);
    setOriginLandmark(geocode.isExactLandmark ? geocode.landmark : null);
    setOrigin(label);
    if (validationError) setValidationError('');
    computeRoute(coords, destinationCoords, label, destination, preference);
  };

  /**
   * Triggered when user drags the red Destination Marker (B)
   */
  const handleMarkerDragDestination = (coords) => {
    const [lat, lng] = coords;
    const geocode = reverseGeocodeLocal(lat, lng);
    const label = geocode.formattedLabel;
    setDestinationCoords(coords);
    setDestinationLandmark(geocode.isExactLandmark ? geocode.landmark : null);
    setDestination(label);
    if (validationError) setValidationError('');
    computeRoute(originCoords, coords, origin, label, preference);
  };

  /**
   * Triggered when a landmark is picked via Autocomplete or Quick preset
   */
  const handleSelectOrigin = (landmark, coords) => {
    setOriginLandmark(landmark);
    const newCoords = landmark ? landmark.coordinates : coords;
    if (newCoords) {
      setOriginCoords(newCoords);
    }
    if (validationError) setValidationError('');
    if (newCoords && destinationCoords) {
      computeRoute(newCoords, destinationCoords, landmark ? landmark.name : origin, destination, preference);
    }
  };

  const handleSelectDestination = (landmark, coords) => {
    setDestinationLandmark(landmark);
    const newCoords = landmark ? landmark.coordinates : coords;
    if (newCoords) {
      setDestinationCoords(newCoords);
    }
    if (validationError) setValidationError('');
    if (originCoords && newCoords) {
      computeRoute(originCoords, newCoords, origin, landmark ? landmark.name : destination, preference);
    }
  };

  /**
   * Switch route preference (Fastest vs Shortest)
   */
  const handleSelectPreference = (newPref) => {
    setPreference(newPref);
    if (routeOptions && routeOptions.fastest && routeOptions.shortest) {
      const activeObj = newPref === 'shortest' ? routeOptions.shortest : routeOptions.fastest;
      setRouteOptions({
        ...routeOptions,
        active: activeObj,
        activePreference: newPref
      });
    } else {
      computeRoute(originCoords, destinationCoords, origin, destination, newPref);
    }
  };

  /**
   * Validate inputs and recalculate route
   */
  const handleFindRoute = () => {
    if (!origin.trim() || !originCoords) {
      setValidationError('Please enter a Starting Location, choose from suggestions, or select a point on the map.');
      return;
    }

    if (!destination.trim() || !destinationCoords) {
      setValidationError('Please enter a Destination point, choose from suggestions, or select a point on the map.');
      return;
    }

    if (originLandmark && destinationLandmark && originLandmark.id === destinationLandmark.id) {
      setValidationError('Starting location and destination cannot be identical. Please pick two different locations.');
      return;
    }
    if (areCoordinatesEqual(originCoords, destinationCoords, 4)) {
      setValidationError('Starting point and destination cannot be at the exact same position on the map.');
      return;
    }

    setValidationError('');
    computeRoute(originCoords, destinationCoords, origin, destination, preference);
  };

  /**
   * Reset form and map back to default demo state
   */
  const handleReset = () => {
    const panaji = findGoaLandmark('Panaji');
    const gu = findGoaLandmark('Goa University');
    const pCoords = panaji ? panaji.coordinates : [15.4989, 73.8278];
    const guCoords = gu ? gu.coordinates : [15.4578, 73.8335];

    setOrigin('Panaji');
    setDestination('Goa University');
    setOriginLandmark(panaji);
    setDestinationLandmark(gu);
    setOriginCoords(pCoords);
    setDestinationCoords(guCoords);
    setPreference('fastest');
    setValidationError('');
    setSelectionMode(null);

    computeRoute(pCoords, guCoords, 'Panaji', 'Goa University', 'fastest');
  };

  /**
   * Loads a bookmarked route from MongoDB Atlas
   */
  const handleLoadSavedRoute = (savedRoute) => {
    const oName = savedRoute.origin_name || 'Origin';
    const dName = savedRoute.destination_name || 'Destination';
    const oCoords = savedRoute.origin_coords;
    const dCoords = savedRoute.destination_coords;
    const pref = savedRoute.preference || 'fastest';

    setOrigin(oName);
    setDestination(dName);
    setOriginCoords(oCoords);
    setDestinationCoords(dCoords);
    setPreference(pref);
    setOriginLandmark(null);
    setDestinationLandmark(null);
    setValidationError('');

    computeRoute(oCoords, dCoords, oName, dName, pref);
  };

  const currentRouteData = routeOptions ? routeOptions.active : null;

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Navigation Bar with Architecture & Saved Routes modal openers */}
      <Header onOpenSavedRoutes={() => setShowSavedModal(true)} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col gap-6">
        {/* Mobile View Toggle Bar */}
        <div className="lg:hidden flex rounded-xl bg-slate-900 border border-slate-800 p-1">
          <button
            type="button"
            onClick={() => setMobileTab('planner')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer ${
              mobileTab === 'planner'
                ? 'bg-cyan-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Route Planner & Details</span>
          </button>
          <button
            type="button"
            onClick={() => setMobileTab('map')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer ${
              mobileTab === 'map'
                ? 'bg-cyan-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Map className="w-3.5 h-3.5" />
            <span>Map Canvas</span>
            {selectionMode && (
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            )}
          </button>
        </div>

        {/* Geolocation Status Notice Banner */}
        {geoNotice && (
          <div className="flex items-center justify-between gap-3 p-3 rounded-xl bg-cyan-950/40 border border-cyan-800/60 text-cyan-200 text-xs shadow-md">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>{geoNotice}</span>
            </div>
            <button
              type="button"
              onClick={() => setGeoNotice('')}
              className="p-1 rounded-lg hover:bg-cyan-900/50 text-cyan-400 hover:text-white transition-colors cursor-pointer"
              title="Dismiss notice"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Core Layout Grid: Left Sidebar + Right Map */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-start">
          {/* Left Column: Form & Route Results */}
          <div
            className={`lg:col-span-5 xl:col-span-4 space-y-6 flex flex-col ${
              mobileTab === 'planner' ? 'block' : 'hidden lg:block'
            }`}
          >
            <RouteSearchForm
              origin={origin}
              setOrigin={setOrigin}
              originLandmark={originLandmark}
              originCoords={originCoords}
              onSelectOrigin={handleSelectOrigin}
              destination={destination}
              setDestination={setDestination}
              destinationLandmark={destinationLandmark}
              destinationCoords={destinationCoords}
              onSelectDestination={handleSelectDestination}
              preference={preference}
              setPreference={handleSelectPreference}
              onFindRoute={handleFindRoute}
              isLoading={isLoading}
              onReset={handleReset}
              validationError={validationError}
              selectionMode={selectionMode}
              onSetSelectionMode={handleSetSelectionMode}
            />

            <RouteResults
              routeOptions={routeOptions}
              origin={origin}
              destination={destination}
              preference={preference}
              onSelectPreference={handleSelectPreference}
            />
          </div>

          {/* Right Column: Interactive Map with Real Road Network Geometry */}
          <div
            className={`lg:col-span-7 xl:col-span-8 h-full flex flex-col min-h-[500px] ${
              mobileTab === 'map' ? 'block' : 'hidden lg:block'
            }`}
          >
            <MapPlaceholder
              origin={origin}
              destination={destination}
              originCoords={originCoords}
              destinationCoords={destinationCoords}
              preference={preference}
              hasCalculated={hasCalculated && Boolean(originCoords && destinationCoords)}
              routeData={currentRouteData}
              selectionMode={selectionMode}
              onSetSelectionMode={handleSetSelectionMode}
              onMapClickPoint={handleMapClickPoint}
              onMarkerDragOrigin={handleMarkerDragOrigin}
              onMarkerDragDestination={handleMarkerDragDestination}
              userLocation={userLocation}
            />
          </div>
        </div>
      </main>

      {/* Saved Routes & History Modal (MongoDB Atlas) */}
      <SavedRoutesModal
        isOpen={showSavedModal}
        onClose={() => setShowSavedModal(false)}
        onLoadRoute={handleLoadSavedRoute}
      />

      {/* Bottom Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>
            SmartRoute AI &bull; B.Tech Final Year Engineering Project
          </p>
          <div className="flex items-center gap-4 text-slate-400 text-[11px]">
            <span>FastAPI + NetworkX 3.7 + OSMnx 2.1.1</span>
            <span>&bull;</span>
            <span className="text-emerald-400 font-medium">MongoDB Atlas Connected</span>
            <span>&bull;</span>
            <span>React 19 + Tailwind CSS</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
