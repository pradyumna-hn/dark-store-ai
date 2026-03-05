"""Expiry risk scoring and dynamic reorder point engine."""

import warnings
import numpy as np
import pandas as pd
from typing import Dict


def compute_expiry_risk(
    inventory_df: pd.DataFrame,
    forecasts_dict: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Score each inventory item for expiry risk.

    For each SKU, computes the expected sell-through probability before expiry
    using the demand forecast.

    Args:
        inventory_df: Inventory DataFrame from data_loader.load_inventory().
        forecasts_dict: Dictionary mapping sku_id -> forecast DataFrame
                        (from forecaster.forecast_all_top_skus).

    Returns:
        inventory_df with additional columns:
            forecasted_demand_before_expiry, sell_through_probability,
            expiry_risk (HIGH / MEDIUM / LOW).
    """
    df = inventory_df.copy()
    df["forecasted_demand_before_expiry"] = 0.0
    df["sell_through_probability"] = 0.0
    df["expiry_risk"] = "LOW"

    for idx, row in df.iterrows():
        sku_id = row["sku_id"]
        expiry_days = int(row["expiry_days"])
        current_stock = float(row["current_stock"])

        forecast = forecasts_dict.get(sku_id)
        if forecast is None:
            # No forecast available — mark as LOW risk by default
            continue

        # Sum forecasted demand for the next N days (where N = expiry_days)
        n_days = min(expiry_days, len(forecast))
        if n_days == 0:
            # Already expired
            df.at[idx, "expiry_risk"] = "HIGH"
            continue

        forecasted_demand = forecast["yhat"].head(n_days).sum()
        df.at[idx, "forecasted_demand_before_expiry"] = round(forecasted_demand, 1)

        if current_stock > 0:
            sell_through = forecasted_demand / current_stock
        else:
            sell_through = 0.0

        df.at[idx, "sell_through_probability"] = round(sell_through, 3)

        if sell_through < 0.4:
            df.at[idx, "expiry_risk"] = "HIGH"
        elif sell_through < 0.7:
            df.at[idx, "expiry_risk"] = "MEDIUM"
        else:
            df.at[idx, "expiry_risk"] = "LOW"

    return df


def compute_reorder_alerts(
    inventory_df: pd.DataFrame,
    orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute dynamic reorder points and identify items needing reorder.

    Formula:
        avg_daily_demand = rolling 7-day average demand
        lead_time = 1 day (dark store assumption)
        safety_stock = 1.5 × std_dev of daily demand (last 14 days)
        dynamic_rop = (avg_daily_demand × lead_time) + safety_stock

    Args:
        inventory_df: Inventory DataFrame from data_loader.load_inventory().
        orders_df: Orders DataFrame from data_loader.load_orders().

    Returns:
        DataFrame of items that need reorder, with columns:
            sku_id, sku_name, store_id, current_stock, dynamic_rop,
            recommended_order_qty, static_rop.
    """
    reorder_rows = []

    for _, inv_row in inventory_df.iterrows():
        sku_id = inv_row["sku_id"]
        store_id = inv_row["store_id"]

        mask = (orders_df["sku_id"] == sku_id) & (orders_df["store_id"] == store_id)
        sku_orders = orders_df[mask].copy()

        if sku_orders.empty:
            warnings.warn(f"No order history for SKU {sku_id} in {store_id} — skipping reorder point calculation.")
            continue

        # Build daily demand series
        daily = (
            sku_orders.groupby("order_date")["quantity"]
            .sum()
            .sort_index()
        )

        # 7-day rolling avg for demand estimate
        avg_daily = daily.tail(7).mean() if len(daily) >= 7 else daily.mean()

        # 14-day std dev for safety stock
        std_14d = daily.tail(14).std() if len(daily) >= 14 else daily.std()
        if np.isnan(std_14d):
            std_14d = avg_daily * 0.2  # fallback: 20% of mean

        lead_time = 1  # days
        safety_stock = 1.5 * std_14d
        dynamic_rop = (avg_daily * lead_time) + safety_stock

        current_stock = inv_row["current_stock"]
        max_stock = inv_row["max_stock"]

        if current_stock <= dynamic_rop:
            recommended_order_qty = max(0, int(max_stock - current_stock))
            reorder_rows.append({
                "sku_id": sku_id,
                "sku_name": inv_row["sku_name"],
                "store_id": store_id,
                "current_stock": int(current_stock),
                "dynamic_rop": round(dynamic_rop, 1),
                "static_rop": inv_row["reorder_point"],
                "recommended_order_qty": recommended_order_qty,
                "avg_daily_demand": round(avg_daily, 1),
                "safety_stock": round(safety_stock, 1),
            })

    if not reorder_rows:
        return pd.DataFrame(columns=[
            "sku_id", "sku_name", "store_id", "current_stock",
            "dynamic_rop", "static_rop", "recommended_order_qty",
            "avg_daily_demand", "safety_stock",
        ])

    return pd.DataFrame(reorder_rows).sort_values("current_stock").reset_index(drop=True)


def summarize_alerts(
    expiry_df: pd.DataFrame,
    reorder_df: pd.DataFrame,
) -> None:
    """Print a clean summary of all alerts to the console.

    Args:
        expiry_df: Output of compute_expiry_risk().
        reorder_df: Output of compute_reorder_alerts().
    """
    high_risk = expiry_df[expiry_df["expiry_risk"] == "HIGH"]
    med_risk = expiry_df[expiry_df["expiry_risk"] == "MEDIUM"]

    print("\n⚠️  ALERT SUMMARY")
    print("─" * 50)
    print(f"High expiry risk items : {len(high_risk)}")
    print(f"Medium expiry risk items: {len(med_risk)}")
    print(f"Reorder alerts         : {len(reorder_df)}")

    if not high_risk.empty:
        print("\n🔴 HIGH EXPIRY RISK:")
        for _, r in high_risk.iterrows():
            print(
                f"   {r['sku_name']:<30} | Stock: {int(r['current_stock'])} | "
                f"Expires in {int(r['expiry_days'])} days | "
                f"Sell-through: {r['sell_through_probability']:.0%}"
            )

    if not reorder_df.empty:
        print("\n⚡ REORDER ALERTS:")
        for _, r in reorder_df.iterrows():
            print(
                f"   {r['sku_name']:<30} | Current: {r['current_stock']} | "
                f"Dynamic ROP: {r['dynamic_rop']} | Order: {r['recommended_order_qty']} units"
            )
