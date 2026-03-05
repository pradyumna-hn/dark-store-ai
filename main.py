#!/usr/bin/env python3
"""Dark Store AI — Inventory Forecasting System.

Single entry point to run the full pipeline:
  1. Load data
  2. Identify top SKUs
  3. Build features
  4. Run forecasts
  5. Compute expiry risk and reorder alerts
  6. Generate daily ops report
"""

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*cmdstanpy.*")

# ── Resolve project root ─────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_orders, load_inventory, get_top_skus
from src.forecaster import forecast_all_top_skus
from src.inventory_alerts import compute_expiry_risk, compute_reorder_alerts, summarize_alerts
from src.report import generate_report


def main(
    store_id: str = "STORE_A",
    horizon: int = 7,
    top_n: int = 20,
    method: str = "prophet",
    orders_path: str = None,
    inventory_path: str = None,
    output_dir: str = None,
) -> None:
    """Run the end-to-end forecasting and reporting pipeline.

    Args:
        store_id: Store to generate the report for.
        horizon: Number of days to forecast.
        top_n: Number of top SKUs to include.
        method: Forecasting method ("prophet" or "lgbm").
        orders_path: Path to orders CSV. Defaults to data/sample_orders.csv.
        inventory_path: Path to inventory CSV. Defaults to data/sample_inventory.csv.
        output_dir: Directory to save the report. Defaults to output/.
    """
    if orders_path is None:
        orders_path = str(ROOT / "data" / "sample_orders.csv")
    if inventory_path is None:
        inventory_path = str(ROOT / "data" / "sample_inventory.csv")
    if output_dir is None:
        output_dir = str(ROOT / "output")

    print("=" * 60)
    print(f"  🏪 Dark Store AI — {store_id}")
    print("=" * 60)

    # ── 1. Load data ─────────────────────────────────────────────────────────
    print("\n📂 Loading data...")
    orders_df = load_orders(orders_path)
    inventory_df = load_inventory(inventory_path)
    print(f"  Orders  : {len(orders_df):,} rows ({orders_df['order_date'].min().date()} → {orders_df['order_date'].max().date()})")
    print(f"  Inventory: {len(inventory_df):,} items")

    # ── 2. Identify top SKUs ─────────────────────────────────────────────────
    print(f"\n🔍 Identifying top {top_n} SKUs...")
    top_skus = get_top_skus(orders_df, n=top_n)
    print(f"  Top SKU: {top_skus.iloc[0]['sku_name']} ({top_skus.iloc[0]['total_quantity']:,} units)")

    # ── 3. Run forecasts ─────────────────────────────────────────────────────
    print(f"\n🔮 Running {method.upper()} forecasts ({horizon}-day horizon) for {store_id}...")
    forecasts = forecast_all_top_skus(orders_df, top_skus, store_id, horizon=horizon, method=method)
    print(f"  Forecasts generated: {len(forecasts)}/{len(top_skus)} SKUs")

    # ── 4. Compute alerts ────────────────────────────────────────────────────
    print("\n🚨 Computing inventory alerts...")
    store_inventory = inventory_df[inventory_df["store_id"] == store_id].copy()
    expiry_df = compute_expiry_risk(store_inventory, forecasts)
    reorder_df = compute_reorder_alerts(store_inventory, orders_df)
    summarize_alerts(expiry_df, reorder_df)

    # ── 5. Generate report ───────────────────────────────────────────────────
    print("\n📋 Generating daily ops report...")
    generate_report(
        inventory_df=store_inventory,
        orders_df=orders_df,
        forecasts_dict=forecasts,
        expiry_df=expiry_df,
        reorder_df=reorder_df,
        top_skus=top_skus,
        store_id=store_id,
        output_dir=output_dir,
        horizon=horizon,
    )

    # ── 6. Success summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ Pipeline complete!")
    print(f"  Store          : {store_id}")
    print(f"  SKUs monitored : {len(forecasts)}")
    print(f"  Forecast horizon: {horizon} days")
    print(f"  Report saved to: {output_dir}/daily_report.txt")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dark Store AI — Inventory Forecasting")
    parser.add_argument("--store", default="STORE_A", help="Store ID (default: STORE_A)")
    parser.add_argument("--horizon", type=int, default=7, help="Forecast horizon in days (default: 7)")
    parser.add_argument("--top-n", type=int, default=20, help="Number of top SKUs (default: 20)")
    parser.add_argument(
        "--method",
        choices=["prophet", "lgbm"],
        default="prophet",
        help="Forecasting method (default: prophet)",
    )
    parser.add_argument("--orders", default=None, help="Path to orders CSV")
    parser.add_argument("--inventory", default=None, help="Path to inventory CSV")
    parser.add_argument("--output-dir", default=None, help="Output directory for report")

    args = parser.parse_args()
    main(
        store_id=args.store,
        horizon=args.horizon,
        top_n=args.top_n,
        method=args.method,
        orders_path=args.orders,
        inventory_path=args.inventory,
        output_dir=args.output_dir,
    )
