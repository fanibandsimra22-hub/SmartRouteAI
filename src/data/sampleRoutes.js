/**
 * sampleRoutes.js
 * 
 * Re-export module for backward compatibility across existing files.
 * Core implementations have been organized into:
 * - src/data/goaLandmarks.js
 * - src/services/locationService.js
 * - src/services/routeService.js
 * - src/utils/geoUtils.js
 */

export { GOA_LANDMARKS, GOA_LANDMARKS as SAMPLE_LOCATIONS, DEFAULT_GOA_CENTER, DEFAULT_GOA_ZOOM } from './goaLandmarks';
export { findGoaLandmark, filterGoaLandmarks, getGoaLandmarks, reverseGeocodeLocal } from '../services/locationService';
export { calculateDynamicRoute, calculateAllRouteOptions } from '../services/routeService';
export { calculateHaversineDistanceKm } from '../utils/geoUtils';

import { findGoaLandmark } from '../services/locationService';
import { calculateDynamicRoute } from '../services/routeService';

export const DEMO_ROUTE_DATA = {
  fastest: calculateDynamicRoute({
    originCoords: [15.4989, 73.8278],
    destinationCoords: [15.4578, 73.8335],
    originName: 'Panaji',
    destinationName: 'Goa University',
    originLandmark: findGoaLandmark('panaji'),
    destinationLandmark: findGoaLandmark('goa-university'),
    preference: 'fastest'
  }),
  shortest: calculateDynamicRoute({
    originCoords: [15.4989, 73.8278],
    destinationCoords: [15.4578, 73.8335],
    originName: 'Panaji',
    destinationName: 'Goa University',
    originLandmark: findGoaLandmark('panaji'),
    destinationLandmark: findGoaLandmark('goa-university'),
    preference: 'shortest'
  })
};
