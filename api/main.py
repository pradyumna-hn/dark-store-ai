"""Dark Store AI — FastAPI REST API.

Exposes the forecasting pipeline over HTTP so that mobile and web clients
can consume forecasts, expiry risk alerts and reorder alerts as JSON.

Run with:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*cmdstanpy.*")

# ── Resolve project root so src/ imports work ─────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_orders, load_inventory, get_top_skus  # noqa: E402
from src.forecaster import forecast_all_top_skus  # noqa: E402
from src.inventory_alerts import compute_expiry_risk, compute_reorder_alerts  # noqa: E402

# ── Default data paths ────────────────────────────────────────────────────────
ORDERS_PATH = str(ROOT / "data" / "sample_orders.csv")
INVENTORY_PATH = str(ROOT / "data" / "sample_inventory.csv")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Dark Store AI API",
    description="Inventory forecasting, expiry risk and reorder alerts for quick-commerce dark stores.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Response models ───────────────────────────────────────────────────────────

class ForecastItem(BaseModel):
    sku_id: str
    sku_name: str
    total_quantity: int
    days: List[float]
    days_lower: List[float]
    days_upper: List[float]
    model: str


class ExpiryAlert(BaseModel):
    sku_id: str
    sku_name: str
    current_stock: int
    expiry_days: int
    forecasted_demand: int
    sell_through_probability: float
    risk: Literal["HIGH", "MEDIUM", "LOW"]


class ReorderAlert(BaseModel):
    sku_id: str
    sku_name: str
    current_stock: int
    dynamic_rop: float
    static_rop: int
    recommended_order_qty: int
    avg_daily_demand: float


class ReportSummary(BaseModel):
    total_skus: int
    reorder_alerts: int
    high_expiry_risk: int
    med_expiry_risk: int


class ReportResponse(BaseModel):
    store_id: str
    generated_at: str
    forecast_horizon: int
    method: str
    summary: ReportSummary
    forecasts: List[ForecastItem]
    expiry_alerts: List[ExpiryAlert]
    reorder_alerts: List[ReorderAlert]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    """Simple health check."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/stores")
def list_stores():
    """Return all store IDs present in the inventory data."""
    try:
        inv = load_inventory(INVENTORY_PATH)
        stores = sorted(inv["store_id"].unique().tolist())
        return {"stores": stores}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/report", response_model=ReportResponse)
def get_report(
    store: str = Query("STORE_A", description="Store ID"),
    method: Literal["lgbm", "prophet"] = Query("lgbm", description="Forecasting method"),
    horizon: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    top_n: int = Query(20, ge=1, le=50, description="Number of top SKUs to include"),
):
    """Run the full forecasting pipeline and return results as JSON.

    This is the main endpoint consumed by the mobile app.  It runs SKU-level
    demand forecasts, expiry risk scoring and dynamic reorder point computation
    for the requested store.

    LightGBM (`method=lgbm`) is significantly faster than Prophet and requires
    no additional system dependencies — recommended for mobile polling.
    """
    try:
        orders_df = load_orders(ORDERS_PATH)
        inventory_df = load_inventory(INVENTORY_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Validate store ID
    available_stores = inventory_df["store_id"].unique().tolist()
    if store not in available_stores:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown store '{store}'. Available: {available_stores}",
        )

    top_skus = get_top_skus(orders_df, n=top_n)
    forecasts = forecast_all_top_skus(orders_df, top_skus, store, horizon=horizon, method=method)

    store_inventory = inventory_df[inventory_df["store_id"] == store].copy()
    expiry_df = compute_expiry_risk(store_inventory, forecasts)
    reorder_df = compute_reorder_alerts(store_inventory, orders_df)

    # ── Build forecast list ───────────────────────────────────────────────────
    forecast_list: List[ForecastItem] = []
    for _, sku_row in top_skus.iterrows():
        sku_id = sku_row["sku_id"]
        fc = forecasts.get(sku_id)
        if fc is None:
            continue
        forecast_list.append(ForecastItem(
            sku_id=sku_id,
            sku_name=sku_row["sku_name"],
            total_quantity=int(sku_row["total_quantity"]),
            days=[round(float(v), 1) for v in fc["yhat"].tolist()],
            days_lower=[round(float(v), 1) for v in fc["yhat_lower"].tolist()],
            days_upper=[round(float(v), 1) for v in fc["yhat_upper"].tolist()],
            model=str(fc["model"].iloc[0]) if "model" in fc.columns else method,
        ))

    # ── Build expiry alerts ───────────────────────────────────────────────────
    store_expiry = expiry_df[expiry_df["store_id"] == store].copy()
    high_risk = store_expiry[store_expiry["expiry_risk"] == "HIGH"]
    med_risk = store_expiry[store_expiry["expiry_risk"] == "MEDIUM"]

    expiry_alerts: List[ExpiryAlert] = []
    for _, r in pd.concat([high_risk, med_risk]).iterrows():
        expiry_alerts.append(ExpiryAlert(
            sku_id=str(r["sku_id"]),
            sku_name=str(r["sku_name"]),
            current_stock=int(r["current_stock"]),
            expiry_days=int(r["expiry_days"]),
            forecasted_demand=int(r["forecasted_demand_before_expiry"]),
            sell_through_probability=round(float(r["sell_through_probability"]), 3),
            risk=str(r["expiry_risk"]),  # type: ignore[arg-type]
        ))

    # ── Build reorder alerts ──────────────────────────────────────────────────
    store_reorder = (
        reorder_df[reorder_df["store_id"] == store]
        if not reorder_df.empty
        else reorder_df
    )
    reorder_alerts: List[ReorderAlert] = []
    for _, r in store_reorder.iterrows():
        reorder_alerts.append(ReorderAlert(
            sku_id=str(r["sku_id"]),
            sku_name=str(r["sku_name"]),
            current_stock=int(r["current_stock"]),
            dynamic_rop=round(float(r["dynamic_rop"]), 1),
            static_rop=int(r["static_rop"]),
            recommended_order_qty=int(r["recommended_order_qty"]),
            avg_daily_demand=round(float(r["avg_daily_demand"]), 1),
        ))

    return ReportResponse(
        store_id=store,
        generated_at=datetime.now().isoformat(),
        forecast_horizon=horizon,
        method=method,
        summary=ReportSummary(
            total_skus=len(forecast_list),
            reorder_alerts=len(reorder_alerts),
            high_expiry_risk=len(high_risk),
            med_expiry_risk=len(med_risk),
        ),
        forecasts=forecast_list,
        expiry_alerts=expiry_alerts,
        reorder_alerts=reorder_alerts,
    )
