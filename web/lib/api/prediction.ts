import { predictionFetch, researchFetch } from "./clients";

export interface SourceRef {
  title: string;
  url: string;
  source_type: string;
}

export interface ResearchBrief {
  market_id: string;
  key_factors: string[];
  injury_flags: string[];
  rest_advantage: string;
  recent_form: string;
  sources: string[];
  source_urls?: SourceRef[];
}

export interface PredictionOutput {
  probability: number;
  confidence: "low" | "medium" | "high";
  key_drivers: string[];
  reasoning: string;
}

export interface ResearchRequest {
  market_id: string;
  question: string;
  sport: string;
  teams: string[];
  game_date: string;
}

export interface PredictRequest {
  market: {
    market_id: string;
    question: string;
    yes_price: number;
    no_price: number;
    closes_at: string;
    sport: string;
    teams: string[];
    game_date: string;
    volume: number;
  };
  research_brief: ResearchBrief;
}

export async function getResearchBrief(req: ResearchRequest): Promise<ResearchBrief> {
  return researchFetch("/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}

export async function getPrediction(req: PredictRequest): Promise<PredictionOutput> {
  return predictionFetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}
