/**
 * goaLandmarks.js
 * 
 * Local Goa Landmarks Database for SmartRoute AI
 * 
 * Maintained database of verified Goa landmarks and educational institutions
 * with accurate WGS-84 geographic coordinates and search aliases.
 */

export const GOA_LANDMARKS = [
  { 
    id: 'pcce-verna', 
    name: 'Padre Conceicao College of Engineering (PCCE)', 
    area: 'Agnel Ashram, Verna, Salcete, Goa', 
    category: 'Engineering College',
    coordinates: [15.3562, 73.9317],
    aliases: ['pcce', 'pcce verna', 'padre conceicao', 'padre conceicao college of engineering', 'agnel verna'],
    description: 'Premier engineering institution at Agnel Technical Education Complex, Verna, affiliated with Goa University.'
  },
  { 
    id: 'panaji', 
    name: 'Panaji', 
    area: 'Central Panaji, North Goa', 
    category: 'City Center',
    coordinates: [15.4989, 73.8278],
    aliases: ['panjim', 'church square', 'panaji church', 'capital'],
    description: 'Capital city center near Church Square, Secretariat, and Mandovi riverfront promenade.'
  },
  { 
    id: 'goa-university', 
    name: 'Goa University', 
    area: 'Taleigao Plateau, Goa', 
    category: 'Education & Research',
    coordinates: [15.4578, 73.8335],
    aliases: ['gu', 'taleigao university', 'goa university campus'],
    description: 'Premier state university campus and administrative center on the Taleigao Plateau.'
  },
  { 
    id: 'miramar-beach', 
    name: 'Miramar Beach', 
    area: 'Panaji Coastal Belt', 
    category: 'Coastal / Tourism',
    coordinates: [15.4805, 73.8115],
    aliases: ['miramar', 'gaspar dias', 'miramar circle'],
    description: 'Urban beach known for the Mandovi River and Arabian Sea confluence at Gaspar Dias.'
  },
  { 
    id: 'dona-paula', 
    name: 'Dona Paula Viewpoint', 
    area: 'Suburban Panaji', 
    category: 'Scenic Viewpoint',
    coordinates: [15.4530, 73.8040],
    aliases: ['dona paula', 'dona paula jetty', 'nio'],
    description: 'Scenic headland overlooking Mormugao harbour and Zuari bay, site of NIO and Raj Bhavan.'
  },
  { 
    id: 'bambolim-gmc', 
    name: 'Bambolim (GMC Complex)', 
    area: 'Tiswadi, North Goa', 
    category: 'Healthcare & Transit',
    coordinates: [15.4580, 73.8610],
    aliases: ['gmc', 'goa medical college', 'bambolim hospital'],
    description: 'Goa Medical College and Hospital administrative healthcare hub on NH-66.'
  },
  { 
    id: 'bits-goa', 
    name: 'BITS Pilani K.K. Birla Goa Campus', 
    area: 'NH-17B, Zuarinagar, Sancoale, Goa', 
    category: 'Premier University',
    coordinates: [15.3911, 73.8782],
    aliases: ['bits', 'bits pilani', 'bits goa', 'zuarinagar'],
    description: 'Deemed university engineering and science campus situated off the NH-17B highway.'
  },
  { 
    id: 'gec-farmagudi', 
    name: 'Goa College of Engineering (GEC)', 
    area: 'Farmagudi, Ponda, Goa', 
    category: 'Engineering College',
    coordinates: [15.4230, 74.0076],
    aliases: ['gec', 'farmagudi engineering', 'gec ponda'],
    description: 'Oldest state engineering college in Goa situated on the Farmagudi plateau.'
  },
  { 
    id: 'dbce-fatorda', 
    name: 'Don Bosco College of Engineering (DBCE)', 
    area: 'Fatorda, Margao, South Goa', 
    category: 'Engineering College',
    coordinates: [15.2974, 73.9744],
    aliases: ['dbce', 'don bosco fatorda', 'don bosco engineering'],
    description: 'Prominent technical engineering college in Fatorda, Margao.'
  },
  { 
    id: 'nit-goa', 
    name: 'National Institute of Technology Goa (NIT Goa)', 
    area: 'Cuncolim, South Goa', 
    category: 'Institute of National Importance',
    coordinates: [15.1872, 74.0044],
    aliases: ['nit', 'nit goa', 'nit cuncolim'],
    description: 'Institute of National Importance established by the Ministry of Education.'
  },
  { 
    id: 'old-goa', 
    name: 'Old Goa (Basilica of Bom Jesus)', 
    area: 'Tiswadi Heritage Zone', 
    category: 'Heritage / UNESCO',
    coordinates: [15.5009, 73.9116],
    aliases: ['old goa', 'bom jesus', 'se cathedral'],
    description: 'Historical former capital known for UNESCO World Heritage churches and Mandovi heritage corridor.'
  },
  { 
    id: 'calangute', 
    name: 'Calangute', 
    area: 'Bardez Coastal Belt', 
    category: 'Coastal / Commercial',
    coordinates: [15.5440, 73.7550],
    aliases: ['calangute beach', 'calangute circle'],
    description: 'Major coastal hub in North Goa with bustling transit corridors and beach market access.'
  },
  { 
    id: 'margao', 
    name: 'Margao', 
    area: 'South Goa Hub', 
    category: 'Commercial & Railway Gateway',
    coordinates: [15.2730, 73.9580],
    aliases: ['madgaon', 'margao railway', 'margao bus stand'],
    description: 'Commercial capital and primary railway gateway of South Goa connecting to Konkan Railway.'
  },
  { 
    id: 'mapusa', 
    name: 'Mapusa', 
    area: 'Bardez, North Goa', 
    category: 'Market & Transit Junction',
    coordinates: [15.5935, 73.8142],
    aliases: ['mapusa market', 'mapusa bus stand'],
    description: 'Central market town and northern bus transit junction connecting coastal Bardez villages.'
  },
  { 
    id: 'vasco-da-gama', 
    name: 'Vasco da Gama', 
    area: 'Mormugao Peninsula', 
    category: 'Port City & Airport Access',
    coordinates: [15.3980, 73.8113],
    aliases: ['vasco', 'dabolim airport', 'mormugao port'],
    description: 'Harbour city housing Mormugao Port, naval aviation hub and access to Dabolim Airport corridor.'
  }
];

// Default map center coordinates for Goa regional view
export const DEFAULT_GOA_CENTER = [15.4200, 73.8700]; // Centered to encompass Panaji down to Verna / PCCE
export const DEFAULT_GOA_ZOOM = 12;
