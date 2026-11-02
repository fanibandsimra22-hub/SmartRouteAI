"""
geocoding_service.py

SmartRoute AI – Location Geocoding & Landmark Search Service
Provides fast, cached location search using OpenStreetMap Nominatim API,
augmented with a curated index of prominent Goa landmarks and educational institutions
for instant offline resilience.

Adheres strictly to Nominatim Usage Policy:
- Custom identifying User-Agent
- Caching of search results
- Viewbox prioritisation for the Goa region
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx

logger = logging.getLogger("smartroute.geocoding_service")

# Curated high-precision Goa Landmark Index (Instant offline & fallback availability)
CURATED_GOA_LANDMARKS = [
    {
        "id": "pcce-verna",
        "name": "Padre Conceicao College of Engineering (PCCE)",
        "display_name": "Padre Conceicao College of Engineering (PCCE), Agnel Ashram, Verna, Salcete, Goa 403722",
        "lat": 15.3562,
        "lon": 73.9317,
        "category": "Engineering College / Education",
        "aliases": ["pcce", "pcce verna", "padre conceicao", "padre conceicao college of engineering", "agnel verna", "verna engineering"],
        "source": "curated"
    },
    {
        "id": "panaji-church",
        "name": "Our Lady of the Immaculate Conception Church, Panaji",
        "display_name": "Our Lady of the Immaculate Conception Church, Church Square, Panaji, Goa",
        "lat": 15.4989,
        "lon": 73.8278,
        "category": "Heritage / Center",
        "aliases": ["panaji", "panjim", "church square", "panaji church"],
        "source": "curated"
    },
    {
        "id": "miramar-beach",
        "name": "Miramar Beach, Panaji",
        "display_name": "Miramar Beach, Dayanand Bandodkar Marg, Panaji, Goa",
        "lat": 15.4805,
        "lon": 73.8115,
        "category": "Beach / Coastal",
        "aliases": ["miramar", "miramar beach", "gaspar dias"],
        "source": "curated"
    },
    {
        "id": "dona-paula",
        "name": "Dona Paula Viewpoint",
        "display_name": "Dona Paula Viewpoint & Jetty, Taleigao Plateau, Goa",
        "lat": 15.4528,
        "lon": 73.8032,
        "category": "Viewpoint / Coastal",
        "aliases": ["dona paula", "dona paula jetty", "nio"],
        "source": "curated"
    },
    {
        "id": "goa-university",
        "name": "Goa University Campus, Taleigao",
        "display_name": "Goa University, Taleigao Plateau, Bambolim, Goa 403206",
        "lat": 15.4578,
        "lon": 73.8335,
        "category": "Education / University",
        "aliases": ["gu", "goa university", "taleigao campus"],
        "source": "curated"
    },
    {
        "id": "gmc-bambolim",
        "name": "Goa Medical College (GMC), Bambolim",
        "display_name": "Goa Medical College Hospital, NH-66, Bambolim, Goa",
        "lat": 15.4650,
        "lon": 73.8550,
        "category": "Hospital / Medical",
        "aliases": ["gmc", "goa medical college", "bambolim hospital"],
        "source": "curated"
    },
    {
        "id": "bits-goa",
        "name": "BITS Pilani K.K. Birla Goa Campus",
        "display_name": "BITS Pilani K.K. Birla Goa Campus, NH-17B, Zuarinagar, Sancoale, Goa",
        "lat": 15.3911,
        "lon": 73.8782,
        "category": "Premier University",
        "aliases": ["bits", "bits pilani", "bits goa", "zuarinagar"],
        "source": "curated"
    },
    {
        "id": "gec-farmagudi",
        "name": "Goa College of Engineering (GEC)",
        "display_name": "Goa College of Engineering (GEC), Farmagudi, Ponda, Goa",
        "lat": 15.4230,
        "lon": 74.0076,
        "category": "Engineering College",
        "aliases": ["gec", "gec farmagudi", "gec ponda"],
        "source": "curated"
    },
    {
        "id": "dbce-fatorda",
        "name": "Don Bosco College of Engineering (DBCE)",
        "display_name": "Don Bosco College of Engineering (DBCE), Fatorda, Margao, South Goa",
        "lat": 15.2974,
        "lon": 73.9744,
        "category": "Engineering College",
        "aliases": ["dbce", "don bosco fatorda", "don bosco engineering"],
        "source": "curated"
    },
    {
        "id": "nit-goa",
        "name": "National Institute of Technology Goa (NIT Goa)",
        "display_name": "National Institute of Technology Goa, Cuncolim, South Goa",
        "lat": 15.1872,
        "lon": 74.0044,
        "category": "Institute of National Importance",
        "aliases": ["nit", "nit goa", "nit cuncolim"],
        "source": "curated"
    },
    {
        "id": "old-goa-bom-jesus",
        "name": "Basilica of Bom Jesus, Old Goa",
        "display_name": "Basilica of Bom Jesus, UNESCO World Heritage Site, Old Goa",
        "lat": 15.5009,
        "lon": 73.9118,
        "category": "Heritage / UNESCO",
        "aliases": ["old goa", "bom jesus", "se cathedral"],
        "source": "curated"
    },
    {
        "id": "kadamba-bus-stand-panaji",
        "name": "Kadamba Inter-State Bus Stand, Panaji",
        "display_name": "KTC Bus Stand, Patto Centre, Panaji, Goa",
        "lat": 15.4940,
        "lon": 73.8340,
        "category": "Transit / Bus Station",
        "aliases": ["ktc panaji", "panaji bus stand", "patto"],
        "source": "curated"
    },
    {
        "id": "kala-academy-panaji",
        "name": "Kala Academy, Panaji",
        "display_name": "Kala Academy Goa, DB Marg, Campal, Panaji, Goa",
        "lat": 15.4925,
        "lon": 73.8185,
        "category": "Cultural / Theater",
        "aliases": ["kala academy", "campal"],
        "source": "curated"
    },
    {
        "id": "margao-railway-station",
        "name": "Madgaon Junction Railway Station (MAO)",
        "display_name": "Madgaon Junction Railway Station, Margao, South Goa",
        "lat": 15.2736,
        "lon": 73.9782,
        "category": "Transit / Train",
        "aliases": ["margao station", "madgaon railway", "margao"],
        "source": "curated"
    },
    {
        "id": "vasco-da-gama",
        "name": "Vasco da Gama City Center",
        "display_name": "Vasco da Gama, Mormugao, South Goa",
        "lat": 15.3982,
        "lon": 73.8113,
        "category": "City Center / Port",
        "aliases": ["vasco", "mormugao port"],
        "source": "curated"
    },
    {
        "id": "mapusa-market",
        "name": "Mapusa Municipal Market",
        "display_name": "Mapusa Market, Mapusa, North Goa",
        "lat": 15.5925,
        "lon": 73.8150,
        "category": "Commercial / Market",
        "aliases": ["mapusa", "mapusa market"],
        "source": "curated"
    },
    {
        "id": "calangute-beach",
        "name": "Calangute Beach",
        "display_name": "Calangute Beach, Bardez, North Goa",
        "lat": 15.5442,
        "lon": 73.7554,
        "category": "Beach / Coastal",
        "aliases": ["calangute", "calangute beach"],
        "source": "curated"
    },
    {
        "id": "candolim-beach",
        "name": "Candolim Beach & Fort Aguada Road",
        "display_name": "Candolim Beach, Sinquerim, Bardez, North Goa",
        "lat": 15.5180,
        "lon": 73.7660,
        "category": "Beach / Coastal",
        "aliases": ["candolim", "sinquerim"],
        "source": "curated"
    },
    {
        "id": "fort-aguada",
        "name": "Fort Aguada & Lighthouse",
        "display_name": "Fort Aguada, Sinquerim, Bardez, North Goa",
        "lat": 15.4920,
        "lon": 73.7735,
        "category": "Heritage / Fort",
        "aliases": ["aguada", "fort aguada"],
        "source": "curated"
    },
    {
        "id": "ponda-center",
        "name": "Ponda City Center",
        "display_name": "Ponda, Central Goa",
        "lat": 15.4026,
        "lon": 74.0152,
        "category": "City Center",
        "aliases": ["ponda", "shanta durga"],
        "source": "curated"
    }
]

# In-memory search cache: query -> (timestamp, List[results])
_GEOCODE_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "SmartRouteAI-NavigationEngine/1.0 (academic-demonstration; pair-programming; contact: admin@smartroute.local)"
}

# Goa Bounding Box for viewbox prioritizing: (min_lon, min_lat, max_lon, max_lat)
GOA_VIEWBOX = "73.65,14.85,74.35,15.85"


async def search_locations(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Searches locations using in-memory cache, curated landmark matching,
    and OpenStreetMap Nominatim geocoding.
    """
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []

    cache_key = f"{clean_q.lower()}_{limit}"
    now = time.time()

    # 1. Check in-memory TTL cache
    if cache_key in _GEOCODE_CACHE:
        ts, cached_results = _GEOCODE_CACHE[cache_key]
        if now - ts < CACHE_TTL_SECONDS:
            return cached_results

    results: List[Dict[str, Any]] = []
    seen_coords = set()

    # 2. Match against curated Goa landmark index first (instant response)
    q_lower = clean_q.lower()
    for item in CURATED_GOA_LANDMARKS:
        aliases = [a.lower() for a in item.get("aliases", [])]
        matched = (
            q_lower in item["name"].lower()
            or q_lower in item["display_name"].lower()
            or q_lower in item["category"].lower()
            or any(q_lower == a or q_lower in a or a in q_lower for a in aliases)
        )
        if matched:
            coord_key = (round(item["lat"], 3), round(item["lon"], 3))
            if coord_key not in seen_coords:
                seen_coords.add(coord_key)
                results.append(item)

    # 3. If query has at least 3 characters and we need more results, query Nominatim
    if len(results) < limit:
        try:
            search_query = clean_q if "goa" in q_lower else f"{clean_q}, Goa, India"
            params = {
                "q": search_query,
                "format": "jsonv2",
                "limit": limit,
                "viewbox": GOA_VIEWBOX,
                "bounded": 0,
                "addressdetails": 1
            }

            async with httpx.AsyncClient(timeout=4.0, headers=NOMINATIM_HEADERS) as client:
                resp = await client.get(NOMINATIM_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data:
                        try:
                            lat = float(item["lat"])
                            lon = float(item["lon"])
                            coord_key = (round(lat, 3), round(lon, 3))
                            if coord_key in seen_coords:
                                continue
                            seen_coords.add(coord_key)

                            name = item.get("name") or item.get("display_name", "").split(",")[0]
                            display_name = item.get("display_name", name)
                            category = item.get("type", "location").replace("_", " ").title()

                            results.append({
                                "id": f"osm-{item.get('place_id', item.get('osm_id', id(item)))}",
                                "name": name,
                                "display_name": display_name,
                                "lat": lat,
                                "lon": lon,
                                "category": category,
                                "source": "nominatim"
                            })
                            if len(results) >= limit:
                                break
                        except (ValueError, KeyError):
                            continue
                else:
                    logger.warning(f"Nominatim returned status {resp.status_code}")
        except Exception as exc:
            logger.warning(f"Nominatim lookup failed: {exc}. Using curated matches only.")

    final_results = results[:limit]
    _GEOCODE_CACHE[cache_key] = (now, final_results)
    return final_results
