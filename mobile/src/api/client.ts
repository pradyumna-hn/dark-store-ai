/**
 * API client for the Dark Store AI FastAPI backend.
 *
 * The API_BASE_URL defaults to localhost:8000 (Expo simulator / web).
 * For a real Android/iOS device on the same WiFi network, change this to
 * your machine's local IP, e.g. "http://192.168.1.42:8000".
 */

export const API_BASE_URL = 'http://localhost:8000';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ForecastItem {
  sku_id: string;
  sku_name: string;
  total_quantity: number;
  /** Forecasted demand for days 0..horizon-1 */
  days: number[];
  days_lower: number[];
  days_upper: number[];
  /** Model used: "lgbm" | "prophet" | "rolling_avg" */
  model: string;
}

export interface ExpiryAlert {
  sku_id: string;
  sku_name: string;
  current_stock: number;
  expiry_days: number;
  forecasted_demand: number;
  sell_through_probability: number;
  risk: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ReorderAlert {
  sku_id: string;
  sku_name: string;
  current_stock: number;
  dynamic_rop: number;
  static_rop: number;
  recommended_order_qty: number;
  avg_daily_demand: number;
}

export interface ReportSummary {
  total_skus: number;
  reorder_alerts: number;
  high_expiry_risk: number;
  med_expiry_risk: number;
}

export interface ReportResponse {
  store_id: string;
  generated_at: string;
  forecast_horizon: number;
  method: string;
  summary: ReportSummary;
  forecasts: ForecastItem[];
  expiry_alerts: ExpiryAlert[];
  reorder_alerts: ReorderAlert[];
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function fetchStores(): Promise<string[]> {
  const resp = await fetch(`${API_BASE_URL}/api/stores`);
  if (!resp.ok) throw new Error(`Server error ${resp.status}`);
  const data = await resp.json();
  return data.stores as string[];
}

export async function fetchReport(
  store: string,
  method: 'lgbm' | 'prophet' = 'lgbm',
  horizon = 7,
  topN = 20,
): Promise<ReportResponse> {
  const url =
    `${API_BASE_URL}/api/report` +
    `?store=${encodeURIComponent(store)}` +
    `&method=${method}` +
    `&horizon=${horizon}` +
    `&top_n=${topN}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Server error ${resp.status}: ${body}`);
  }
  return resp.json() as Promise<ReportResponse>;
}
