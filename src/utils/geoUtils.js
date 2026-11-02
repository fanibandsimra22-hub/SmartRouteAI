/**
 * geoUtils.js
 * 
 * Geographic and Spatial Utilities for SmartRoute AI
 * 
 * Provides pure mathematical functions for Haversine distance calculations,
 * coordinates formatting, travel time estimation, and position equality.
 */

const EARTH_RADIUS_KM = 6371;

/**
 * Calculate the great-circle distance between two GPS coordinates using the Haversine formula.
 * @param {Array<number>} coords1 - [latitude, longitude]
 * @param {Array<number>} coords2 - [latitude, longitude]
 * @returns {number} distance in kilometers
 */
export function calculateHaversineDistanceKm(coords1, coords2) {
  if (!coords1 || !coords2 || coords1.length < 2 || coords2.length < 2) {
    return 0;
  }
  const [lat1, lon1] = coords1;
  const [lat2, lon2] = coords2;

  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS_KM * c;
}

/**
 * Format a coordinate pair into a user-friendly label
 * e.g. "Selected Map Location (15.4989, 73.8278)"
 */
export function formatMapLocationLabel(lat, lng, prefix = 'Selected Map Location') {
  if (lat == null || lng == null) return prefix;
  return `${prefix} (${Number(lat).toFixed(4)}, ${Number(lng).toFixed(4)})`;
}

/**
 * Format coordinates for compact display
 * e.g. "15.4989° N, 73.8278° E"
 */
export function formatCoordinatesDetailed(coords) {
  if (!coords || coords.length < 2) return 'Unknown Coordinates';
  const [lat, lng] = coords;
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lng).toFixed(4)}° ${lngDir}`;
}

/**
 * Check if two coordinate pairs are identical within a given precision
 */
export function areCoordinatesEqual(coords1, coords2, precision = 4) {
  if (!coords1 || !coords2) return false;
  const lat1 = Number(coords1[0]).toFixed(precision);
  const lng1 = Number(coords1[1]).toFixed(precision);
  const lat2 = Number(coords2[0]).toFixed(precision);
  const lng2 = Number(coords2[1]).toFixed(precision);
  return lat1 === lat2 && lng1 === lng2;
}

/**
 * Estimate travel time in minutes based on distance and average speed
 */
export function estimateTravelTimeMin(distanceKm, avgSpeedKmh = 30) {
  if (!distanceKm || distanceKm <= 0) return 1;
  return Math.max(2, Math.round((distanceKm / avgSpeedKmh) * 60));
}

/**
 * Format distance string clearly indicating whether it is straight-line or road distance
 */
export function formatDistanceDisplay(distanceKm, isStraightLine = false) {
  if (isStraightLine) {
    return `${Number(distanceKm).toFixed(2)} km (Straight-line)`;
  }
  return `${Number(distanceKm).toFixed(1)} km`;
}
