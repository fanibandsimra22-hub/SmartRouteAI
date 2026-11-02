/**
 * locationService.js
 * 
 * Location Abstraction & Landmark Search Service for SmartRoute AI
 * 
 * Manages location autocomplete, online Nominatim search, landmark lookups,
 * and reverse geocoding with instant local fallback.
 */

import { GOA_LANDMARKS } from '../data/goaLandmarks';
import { calculateHaversineDistanceKm, formatMapLocationLabel } from '../utils/geoUtils';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get all available verified Goa landmarks
 */
export function getGoaLandmarks() {
  return GOA_LANDMARKS;
}

/**
 * Find exact or closest matching landmark by name, ID, or alias (case-insensitive)
 */
export function findGoaLandmark(nameOrQuery) {
  if (!nameOrQuery || typeof nameOrQuery !== 'string') return null;
  const clean = nameOrQuery.trim().toLowerCase();
  
  return GOA_LANDMARKS.find((loc) => 
    loc.name.toLowerCase() === clean || 
    loc.id.toLowerCase() === clean ||
    (Array.isArray(loc.aliases) && loc.aliases.some((alias) => alias.toLowerCase() === clean))
  ) || null;
}

/**
 * Filter landmarks matching search query for live autocomplete suggestions
 */
export function filterGoaLandmarks(query) {
  if (!query || typeof query !== 'string') return GOA_LANDMARKS;
  const clean = query.trim().toLowerCase();
  
  return GOA_LANDMARKS.filter((loc) => 
    loc.name.toLowerCase().includes(clean) || 
    loc.area.toLowerCase().includes(clean) ||
    loc.category.toLowerCase().includes(clean) ||
    (Array.isArray(loc.aliases) && loc.aliases.some((alias) => alias.toLowerCase().includes(clean)))
  );
}

/**
 * Search locations via backend Nominatim API with automatic local fallback
 */
export async function searchLocationsApi(query) {
  if (!query || query.trim().length < 2) return [];

  try {
    const res = await fetch(`${API_BASE_URL}/api/locations/search?q=${encodeURIComponent(query)}&limit=8`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        return data.map((item) => ({
          id: item.id || `loc-${item.lat}-${item.lon}`,
          name: item.name,
          displayName: item.display_name,
          coordinates: [Number(item.lat), Number(item.lon)],
          category: item.category || 'Location',
          area: item.display_name ? item.display_name.split(',').slice(1, 3).join(',').trim() : 'Goa',
          isOnlineResult: true
        }));
      }
    }
  } catch (err) {
    console.warn('Online location search failed, falling back to local database:', err.message);
  }

  // Fallback to local curated Goa landmarks
  return filterGoaLandmarks(query).map((loc) => ({
    ...loc,
    displayName: `${loc.name}, ${loc.area}`,
    isOnlineResult: false
  }));
}

/**
 * Reverse geocode a latitude & longitude pair:
 * If the coordinates are very close (<= 1.2 km) to a known Goa landmark, returns that landmark name.
 * Otherwise, returns a clean formatted coordinate label.
 */
export function reverseGeocodeLocal(lat, lng) {
  const coords = [lat, lng];
  let closestLandmark = null;
  let minDistance = Infinity;

  for (const landmark of GOA_LANDMARKS) {
    const dist = calculateHaversineDistanceKm(coords, landmark.coordinates);
    if (dist < minDistance) {
      minDistance = dist;
      closestLandmark = landmark;
    }
  }

  // If within 1.2 km of a known landmark, reference it
  if (closestLandmark && minDistance <= 1.2) {
    return {
      name: `Near ${closestLandmark.name}`,
      landmark: closestLandmark,
      isExactLandmark: minDistance < 0.2,
      distanceFromLandmarkKm: minDistance.toFixed(2),
      formattedLabel: formatMapLocationLabel(lat, lng, `Near ${closestLandmark.name}`)
    };
  }

  // Otherwise, return pure map coordinates
  return {
    name: formatMapLocationLabel(lat, lng),
    landmark: null,
    isExactLandmark: false,
    distanceFromLandmarkKm: null,
    formattedLabel: formatMapLocationLabel(lat, lng)
  };
}

/**
 * Validates if an input string is a valid location or map point
 */
export function isLocationValid(inputText, landmark, coords) {
  if (!inputText || !inputText.trim()) return false;
  if (landmark) return true;
  if (coords && coords.length === 2 && inputText.startsWith('Selected Map Location')) return true;
  return false;
}
