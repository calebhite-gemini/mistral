// Prediction service is not yet implemented.
// Returns a stub until LLM research pipeline is built out.
export interface PredictionOutput {
  probability: number;
  confidence: "low" | "medium" | "high";
  key_drivers: string[];
  reasoning: string;
}

export async function getPrediction(): Promise<PredictionOutput> {
  return {
    probability: 50,
    confidence: "low",
    key_drivers: [],
    reasoning: "LLM research pipeline not yet implemented.",
  };
}
