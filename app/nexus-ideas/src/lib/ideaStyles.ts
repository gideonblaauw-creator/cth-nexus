// lib/ideaStyles.ts — Tailwind class maps for categories and stages

export const CATEGORY_STYLES: Record<string, string> = {
  'Food & Agriculture':    'bg-green-100 text-green-800',
  'Clean Industry':        'bg-blue-100 text-blue-800',
  'Air & Environment':     'bg-sky-100 text-sky-800',
  'Efficiency':            'bg-emerald-50 text-emerald-700',
  'Water':                 'bg-cyan-100 text-cyan-900',
  'Clean Energy':          'bg-yellow-100 text-yellow-800',
  'Transportation':        'bg-purple-100 text-purple-800',
  'Energy Storage':        'bg-red-100 text-red-800',
  'Not Assigned/ Unknown': 'bg-slate-100 text-slate-500',
};

export const STAGE_STYLES: Record<string, string> = {
  'Ideation':     'bg-amber-100 text-amber-800',
  'Sketches':     'bg-blue-100 text-blue-800',
  'Prototype':    'bg-indigo-100 text-indigo-800',
  'Private Beta': 'bg-purple-100 text-purple-800',
  'Public Beta':  'bg-pink-100 text-pink-800',
  'Pre-orders':   'bg-emerald-100 text-emerald-800',
  'Launched':     'bg-green-100 text-green-900 font-bold',
  'Unknown':      'bg-slate-100 text-slate-400',
};

// ── CTH Taxonomy: 9 sectors ──

export const SECTOR_STYLES: Record<string, string> = {
  af: 'bg-green-100 text-green-900 border-green-200',
  bu: 'bg-lime-100 text-lime-900 border-lime-200',
  en: 'bg-yellow-100 text-yellow-900 border-yellow-200',
  ic: 'bg-indigo-100 text-indigo-900 border-indigo-200',
  in: 'bg-blue-100 text-blue-900 border-blue-200',
  tr: 'bg-purple-100 text-purple-900 border-purple-200',
  wa: 'bg-emerald-100 text-emerald-900 border-emerald-200',
  ww: 'bg-cyan-100 text-cyan-900 border-cyan-200',
  xs: 'bg-orange-100 text-orange-900 border-orange-200',
};

export const SECTOR_COLORS: Record<string, string> = {
  af: '#22C55E',
  bu: '#84CC16',
  en: '#EAB308',
  ic: '#6366F1',
  in: '#3B82F6',
  tr: '#A855F7',
  wa: '#10B981',
  ww: '#06B6D4',
  xs: '#F97316',
};

export const SECTOR_LABELS: Record<string, string> = {
  af: 'AFOLU',
  bu: 'Buildings & Infrastructure',
  en: 'Energy Systems',
  ic: 'ICT & Digitalization',
  in: 'Industry',
  tr: 'Transport',
  wa: 'Waste',
  ww: 'Water & Wastewater',
  xs: 'Cross-Sectoral',
};

export const TAXONOMY_NODES: Record<string, string> = {
  'CT-AF-001': 'Sustainable Coffee Production',
  'CT-AF-002': 'Coffee Supply Chain Traceability',
  'CT-AF-003': 'Cacao Agroforestry Systems',
  'CT-AF-004': 'Silvopastoral Systems',
  'CT-AF-005': 'Community Reforestation (REDD+)',
  'CT-AF-006': 'Sustainable Fishing & Blue Economy',
  'CT-AF-007': 'Precision Agriculture & Digital Agri',
  'CT-AF-008': 'Payments for Ecosystem Services (PES)',
  'CT-AF-009': 'Bioeconomy & Non-Timber Forest Products',
  'CT-AF-010': 'Smallholder Climate Adaptation (AFOLU)',
  'CT-AF-011': 'Natural Rubber Agroforestry',
  'CT-AF-012': 'Organic & Regenerative Agriculture',
  'CT-BU-001': 'Green Building Design & Certification',
  'CT-BU-002': 'Building Energy Retrofit',
  'CT-BU-003': 'Affordable Green Housing',
  'CT-BU-004': 'Urban Resilience & Climate Adaptation Infrastructure',
  'CT-BU-005': 'Green Roofs & Urban Greening',
  'CT-EN-001': 'Solar PV (Utility & Distributed)',
  'CT-EN-002': 'Wind Energy',
  'CT-EN-003': 'Small Hydropower',
  'CT-EN-004': 'Energy Storage (Battery & Grid)',
  'CT-EN-005': 'Grid Modernisation',
  'CT-EN-006': 'Distributed Generation & Prosumers',
  'CT-EN-007': 'Clean Cooking',
  'CT-EN-008': 'Energy Efficiency (Industrial)',
  'CT-EN-009': 'Green Hydrogen',
  'CT-EN-010': 'Biomass & Biogas',
  'CT-IC-001': 'Satellite Deforestation Monitoring',
  'CT-IC-002': 'AI-powered MRV & Carbon Measurement',
  'CT-IC-003': 'Supply Chain Traceability (EUDR)',
  'CT-IC-004': 'Climate Data Platforms & APIs',
  'CT-IC-005': 'Precision Agriculture Data',
  'CT-IC-006': 'Smart Grid & IoT for Energy',
  'CT-IN-001': 'Industrial Energy Efficiency',
  'CT-IN-002': 'Green Hydrogen (Industrial Use)',
  'CT-IN-003': 'Cement & Construction Materials Decarbonisation',
  'CT-IN-004': 'Circular Economy & Industrial Symbiosis',
  'CT-IN-005': 'Clean Manufacturing SMEs',
  'CT-TR-001': 'Electric Vehicles (2W/3W/Bus Priority)',
  'CT-TR-002': 'Public Transit Electrification',
  'CT-TR-003': 'Freight Decarbonisation',
  'CT-TR-004': 'Sustainable Aviation Fuels',
  'CT-TR-005': 'Active Mobility Infrastructure',
  'CT-WA-001': 'Waste-to-Energy & Biogas',
  'CT-WA-002': 'Organic Waste & Composting',
  'CT-WA-003': 'Recycling & Materials Recovery',
  'CT-WA-004': 'Extended Producer Responsibility',
  'CT-WW-001': 'Water Treatment & Sanitation',
  'CT-WW-002': 'Irrigation Efficiency & Precision Water',
  'CT-WW-003': 'Watershed Conservation & Payments',
  'CT-WW-004': 'Urban Flood Resilience',
  'CT-XS-001': 'Carbon Markets & Credits',
  'CT-XS-002': 'MRV Platforms',
  'CT-XS-003': 'Climate Finance & Green Bonds',
  'CT-XS-004': 'Climate Risk Assessment & Disclosure',
  'CT-XS-005': 'NDC Implementation Tracking',
  'CT-XS-006': 'Green Insurance & Climate Risk Products',
  'CT-XS-007': 'Blended Finance Structures',
  'CT-XS-008': 'Climate Governance & Policy Enablers',
};

/** Extract sector code from a taxonomy node code, e.g. 'CT-AF-007' → 'af' */
export function sectorFromCode(code: string): string {
  const match = code.match(/^CT-([A-Z]{2})-/);
  return match ? match[1].toLowerCase() : '';
}

export const COUNTRY_FLAGS: Record<string, string> = {
  'Costa Rica':  '\u{1F1E8}\u{1F1F7}',
  'El Salvador': '\u{1F1F8}\u{1F1FB}',
  'Guatemala':   '\u{1F1EC}\u{1F1F9}',
  'Peru':        '\u{1F1F5}\u{1F1EA}',
};
