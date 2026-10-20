// types/idea.ts — Shared data contract for the CTH Idea Browser

export type CleanCategory =
  | 'Food & Agriculture'
  | 'Clean Industry'
  | 'Air & Environment'
  | 'Efficiency'
  | 'Water'
  | 'Clean Energy'
  | 'Transportation'
  | 'Energy Storage'
  | 'Not Assigned/ Unknown';

export type ImpactArea = 'Circular Economy' | 'Nature-Based' | 'Mitigation' | 'Adaptation';

export type CTSector =
  | 'af' | 'bu' | 'en' | 'ic' | 'in' | 'tr' | 'wa' | 'ww' | 'xs';

export type IdeaStage =
  | 'Ideation' | 'Sketches' | 'Prototype' | 'Private Beta'
  | 'Public Beta' | 'Pre-orders' | 'Launched' | 'Unknown';

export const STAGE_ORDER: Record<IdeaStage, number> = {
  Ideation: 0, Sketches: 1, Prototype: 2, 'Private Beta': 3,
  'Public Beta': 4, 'Pre-orders': 5, Launched: 6, Unknown: 7,
};

export interface CleantechIdea {
  // Identity
  id: number;
  app_id: string;
  source: string;

  // Who
  founder: string;
  startup_name: string;

  // Where
  country: string;
  city: string;
  flag: string;

  // What
  description: string;
  category: CleanCategory;
  impact_areas: ImpactArea[];

  // Deep fields — fetched on drawer open, empty on card
  problem: string;
  solution: string;
  revenue_model: string;
  target_market: string;
  social_impact: string;
  demand_evidence: string;
  competitors: string;
  expertise: string;
  external_support: string;

  ct_taxonomy?: string;

  // Stage
  stage: IdeaStage;
  stage_order: number;

  // Team & funding
  team_size: string;
  team_roles: string;
  funded: string;
  funding_amt: string;

  // Meta
  website: string;
  bookstack_page_id?: number;
  bookstack_page_url?: string;
  ingested_at?: string;
}

export interface IdeaFilter {
  countries: string[];
  categories: CleanCategory[];
  impactAreas: ImpactArea[];
  stages: IdeaStage[];
  taxonomies: string[];
  query: string;
}

export interface RagQueryResponse {
  answer: string;
  ideas: CleantechIdea[];
  sources: string[];
  highlighted_ids: number[];
}
