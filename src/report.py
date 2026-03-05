"""Human-readable daily operations report generator."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd


def _box(title: str, width: int = 58) -> str:
    """Render a box around a title string."""
    inner = title.center(width - 4)
    top = "╔" + "═" * (width - 2) + "╗"
    mid = "║" + " " + inner + " " * (width - 3 - len(inner)) + "║"
    bot = "╚" + "═" * (width - 2) + "╝"
    return f"{top}\n{mid}\n{bot}"


def generate_report(
    inventory_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    forecasts_dict: Dict[str, pd.DataFrame],
    expiry_df: pd.DataFrame,
    reorder_df: pd.DataFrame,
    top_skus: pd.DataFrame,
    store_id: str,
    output_dir: str = "output",
    horizon: int = 7,
) -> str:
    """Generate a human-readable daily ops report.

    The report is both printed to console and saved to
    ``{output_dir}/daily_report.txt``.

    Args:
        inventory_df: Inventory DataFrame (filtered to store_id).
        orders_df: Full orders DataFrame.
        forecasts_dict: SKU -> forecast DataFrame mapping.
        expiry_df: Output of compute_expiry_risk().
        reorder_df: Output of compute_reorder_alerts().
        top_skus: DataFrame from get_top_skus().
        store_id: Store being reported on.
        output_dir: Directory to save the report file.
        horizon: Number of forecast days to show.

    Returns:
        The full report as a string.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines.append(_box(f"DARK STORE DAILY OPS REPORT — {date_str} | {store_id}"))
    lines.append("")

    # ── Demand Forecast ──────────────────────────────────────────────────────
    lines.append(f"📦 DEMAND FORECAST — NEXT {horizon} DAYS (Top Items)")
    lines.append("─" * 75)

    # Build header row
    col_width = 22
    header = f"{'Item':<{col_width}}"
    for day in range(horizon):
        label = f"D+{day}" if day > 0 else "Today"
        header += f" | {label:>5}"
    lines.append(header)
    lines.append("─" * 75)

    # One row per top SKU (only those with forecasts)
    shown = 0
    for _, sku_row in top_skus.iterrows():
        sku_id = sku_row["sku_id"]
        sku_name = sku_row["sku_name"]
        forecast = forecasts_dict.get(sku_id)
        if forecast is None:
            continue
        row_str = f"{sku_name:<{col_width}}"
        for day in range(horizon):
            if day < len(forecast):
                val = round(forecast["yhat"].iloc[day])
            else:
                val = "-"
            row_str += f" | {val:>5}"
        lines.append(row_str)
        shown += 1
        if shown >= 10:  # Show at most 10 items
            break

    lines.append("")

    # ── Expiry Risk Alerts ───────────────────────────────────────────────────
    lines.append("⚠️  EXPIRY RISK ALERTS")
    lines.append("─" * 75)

    store_expiry = expiry_df[expiry_df["store_id"] == store_id].copy()
    high_risk = store_expiry[store_expiry["expiry_risk"] == "HIGH"]
    med_risk = store_expiry[store_expiry["expiry_risk"] == "MEDIUM"]

    if high_risk.empty and med_risk.empty:
        lines.append("  ✅ No expiry risk alerts — all items look good!")
    else:
        for _, r in high_risk.iterrows():
            est = int(r["forecasted_demand_before_expiry"])
            lines.append(
                f"🔴 HIGH RISK  — {r['sku_name']:<26} | "
                f"Stock: {int(r['current_stock']):>4} units | "
                f"Expires in {int(r['expiry_days']):>2} days | "
                f"Est. sell: {est:>4} units"
            )
        for _, r in med_risk.iterrows():
            est = int(r["forecasted_demand_before_expiry"])
            lines.append(
                f"🟡 MED RISK   — {r['sku_name']:<26} | "
                f"Stock: {int(r['current_stock']):>4} units | "
                f"Expires in {int(r['expiry_days']):>2} days | "
                f"Est. sell: {est:>4} units"
            )

    lines.append("")

    # ── Reorder Alerts ───────────────────────────────────────────────────────
    lines.append("🔁 REORDER ALERTS")
    lines.append("─" * 75)

    store_reorder = reorder_df[reorder_df["store_id"] == store_id] if not reorder_df.empty else reorder_df

    if store_reorder.empty:
        lines.append("  ✅ No reorder alerts — stock levels are healthy!")
    else:
        for _, r in store_reorder.iterrows():
            lines.append(
                f"⚡ REORDER NOW — {r['sku_name']:<24} | "
                f"Current: {int(r['current_stock']):>4} | "
                f"Dynamic ROP: {r['dynamic_rop']:>6.1f} | "
                f"Order: {r['recommended_order_qty']:>4} units"
            )

    lines.append("")

    # ── Summary ──────────────────────────────────────────────────────────────
    lines.append("📊 SUMMARY")
    lines.append("─" * 75)
    lines.append(f"  Total SKUs monitored   : {len(top_skus)}")
    lines.append(f"  Reorder alerts         : {len(store_reorder)}")
    lines.append(f"  High expiry risk items : {len(high_risk)}")
    lines.append(f"  Med expiry risk items  : {len(med_risk)}")
    lines.append(f"  Report generated at    : {time_str}")
    lines.append("")

    report_text = "\n".join(lines)

    # Print to console
    print(report_text)

    # Save to file
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_path = Path(output_dir) / "daily_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\n📄 Report saved to: {report_path}")
    return report_text
