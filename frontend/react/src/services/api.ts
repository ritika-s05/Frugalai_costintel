const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8002";

export interface AnalyticsSummary {
  total_requests: number;
  total_actual_cost: number;
  total_baseline_cost: number;
  total_savings: number;
  savings_percentage: number;
  cache_hits: number;
  cache_hit_rate: number;
  routed_requests: number;
  routing_rate: number;
  average_provider_latency_ms: number;
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/summary`
  );

  if (!response.ok) {
    throw new Error(
      `Analytics API error: ${response.status}`
    );
  }

  return response.json();
}