export type StubWell = {
  id: string;
  name: string;
  county: string;
  lat: number;
  lon: number;
  depth_ft: number;
  aquifer?: string;
  gcd?: string;
  gwdb_depth_ft?: number;
};

export const wells: StubWell[] = [
  { id: 'S-0001', name: 'Sample Well 1', county: 'Travis', lat: 30.2672, lon: -97.7431, depth_ft: 420, aquifer: 'Edwards', gcd: 'BSEACD', gwdb_depth_ft: 260 },
  { id: 'S-0002', name: 'Sample Well 2', county: 'Hays', lat: 29.9996, lon: -98.1029, depth_ft: 350, aquifer: 'Edwards', gcd: 'BSEACD' },
  { id: 'S-0003', name: 'Sample Well 3', county: 'Williamson', lat: 30.5060, lon: -97.8203, depth_ft: 500, aquifer: 'Trinity' },
  { id: 'S-0004', name: 'Sample Well 4', county: 'Harris', lat: 29.7604, lon: -95.3698, depth_ft: 600, aquifer: 'Chicot', gcd: 'Harris-Galveston' },
  { id: 'S-0005', name: 'Sample Well 5', county: 'Dallas', lat: 32.7767, lon: -96.7970, depth_ft: 470 },
  { id: 'S-0006', name: 'Sample Well 6', county: 'Bexar', lat: 29.4241, lon: -98.4936, depth_ft: 440, aquifer: 'Edwards' },
];


