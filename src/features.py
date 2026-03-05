"""Feature engineering for dark store demand forecasting."""

import pandas as pd
import numpy as np
import warnings
from typing import Optional


def build_forecast_features(
    orders_df: pd.DataFrame,
    sku_id: str,
    store_id: str,
) -> Optional[pd.DataFrame]:
    """Build a daily time series with demand features for a given SKU and store.

    Args:
        orders_df: Orders DataFrame from data_loader.load_orders().
        sku_id: SKU identifier to filter on.
        store_id: Store identifier to filter on.

    Returns:
        DataFrame indexed by date with demand features, or None if insufficient data.
        Columns: daily_demand, rolling_7d_avg, rolling_14d_avg, day_of_week,
                 is_weekend, is_month_start, is_month_end, lag_1, lag_7, week_of_year
    """
    # Filter for this SKU + store
    mask = (orders_df["sku_id"] == sku_id) & (orders_df["store_id"] == store_id)
    subset = orders_df[mask].copy()

    if subset.empty:
        warnings.warn(f"No data found for SKU {sku_id} in store {store_id}.")
        return None

    # Aggregate to daily demand
    daily = (
        subset.groupby("order_date")["quantity"]
        .sum()
        .reset_index()
        .rename(columns={"order_date": "ds", "quantity": "daily_demand"})
        .sort_values("ds")
    )

    # Fill missing dates with 0 demand
    full_range = pd.date_range(daily["ds"].min(), daily["ds"].max(), freq="D")
    daily = daily.set_index("ds").reindex(full_range, fill_value=0).reset_index()
    daily.rename(columns={"index": "ds"}, inplace=True)

    if len(daily) < 30:
        warnings.warn(
            f"SKU {sku_id} / {store_id} has only {len(daily)} days of data "
            "(< 30). Forecasts may be unreliable."
        )

    # Rolling averages
    daily["rolling_7d_avg"] = (
        daily["daily_demand"].rolling(7, min_periods=1).mean().round(2)
    )
    daily["rolling_14d_avg"] = (
        daily["daily_demand"].rolling(14, min_periods=1).mean().round(2)
    )

    # Date-based features
    daily["day_of_week"] = daily["ds"].dt.dayofweek
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)
    daily["is_month_start"] = daily["ds"].dt.is_month_start.astype(int)
    daily["is_month_end"] = daily["ds"].dt.is_month_end.astype(int)
    daily["week_of_year"] = daily["ds"].dt.isocalendar().week.astype(int)

    # Lag features
    daily["lag_1"] = daily["daily_demand"].shift(1).fillna(0)
    daily["lag_7"] = daily["daily_demand"].shift(7).fillna(0)

    return daily
