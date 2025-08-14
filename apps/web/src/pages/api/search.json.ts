import type { APIRoute } from 'astro';

// Stubbed well records for Sprint 3 (no backend yet)
const items = [
  {
    id: 'W-1001',
    name: 'Barton Creek Well',
    county: 'Travis',
    lat: 30.2672,
    lon: -97.7431,
    depth_ft: 420,
  },
  {
    id: 'W-1002',
    name: 'Spring Branch Well',
    county: 'Hays',
    lat: 29.9996,
    lon: -98.1029,
    depth_ft: 350,
  },
  {
    id: 'W-1003',
    name: 'Cedar Park Well',
    county: 'Williamson',
    lat: 30.5060,
    lon: -97.8203,
    depth_ft: 500,
  },
  {
    id: 'W-1004',
    name: 'Buffalo Bayou Well',
    county: 'Harris',
    lat: 29.7604,
    lon: -95.3698,
    depth_ft: 600,
  },
  {
    id: 'W-1005',
    name: 'White Rock Well',
    county: 'Dallas',
    lat: 32.7767,
    lon: -96.7970,
    depth_ft: 470,
  },
  {
    id: 'W-1006',
    name: 'Mission San Jose Well',
    county: 'Bexar',
    lat: 29.4241,
    lon: -98.4936,
    depth_ft: 440,
  },
];

export const GET: APIRoute = () => {
  return new Response(JSON.stringify({ items }), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const prerender = true;


