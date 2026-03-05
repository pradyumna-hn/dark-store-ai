"""Data loading and validation utilities for dark store inventory forecasting."""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path


def load_orders(filepath: str) -> pd.DataFrame:
    """Load and validate orders CSV file.

    Args:
        filepath: Path to the orders CSV file.

    Returns:
        Clean DataFrame with parsed dates and validated columns.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Orders file not found: {filepath}")

    df = pd.read_csv(filepath)

    required_cols = {"order_id", "order_date", "sku_id", "sku_name", "quantity", "store_id", "category"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Orders CSV missing required columns: {missing}")

    # Parse dates
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Data quality checks
    if df["order_date"].isna().any():
        n = df["order_date"].isna().sum()
        warnings.warn(f"Found {n} rows with missing order_date — dropping them.")
        df = df.dropna(subset=["order_date"])

    if df["quantity"].isna().any():
        n = df["quantity"].isna().sum()
        warnings.warn(f"Found {n} rows with missing quantity — dropping them.")
        df = df.dropna(subset=["quantity"])

    neg_qty = (df["quantity"] <= 0).sum()
    if neg_qty > 0:
        warnings.warn(f"Found {neg_qty} rows with non-positive quantity — dropping them.")
        df = df[df["quantity"] > 0]

    # Check for date gaps
    date_range = pd.date_range(df["order_date"].min(), df["order_date"].max(), freq="D")
    unique_dates = df["order_date"].dt.normalize().unique()
    gaps = set(date_range.normalize()) - set(pd.DatetimeIndex(unique_dates).normalize())
    if gaps:
        warnings.warn(f"Found {len(gaps)} date gaps in order data (may be normal for low-volume days).")

    df = df.reset_index(drop=True)
    return df


def load_inventory(filepath: str) -> pd.DataFrame:
    """Load and validate inventory CSV file.

    Args:
        filepath: Path to the inventory CSV file.

    Returns:
        Clean DataFrame with validated inventory data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Inventory file not found: {filepath}")

    df = pd.read_csv(filepath)

    required_cols = {
        "sku_id", "sku_name", "store_id", "current_stock",
        "reorder_point", "max_stock", "expiry_days", "unit_cost", "category"
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Inventory CSV missing required columns: {missing}")

    if df["current_stock"].isna().any():
        warnings.warn("Found rows with missing current_stock — filling with 0.")
        df["current_stock"] = df["current_stock"].fillna(0)

    neg_stock = (df["current_stock"] < 0).sum()
    if neg_stock > 0:
        warnings.warn(f"Found {neg_stock} rows with negative current_stock — setting to 0.")
        df["current_stock"] = df["current_stock"].clip(lower=0)

    df = df.reset_index(drop=True)
    return df


def get_top_skus(orders_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Return top N SKUs by total order volume (ABC analysis).

    Args:
        orders_df: Orders DataFrame from load_orders().
        n: Number of top SKUs to return.

    Returns:
        DataFrame with columns [sku_id, sku_name, total_quantity, cumulative_pct]
        sorted by total_quantity descending.
    """
    sku_volume = (
        orders_df.groupby(["sku_id", "sku_name"])["quantity"]
        .sum()
        .reset_index()
        .rename(columns={"quantity": "total_quantity"})
        .sort_values("total_quantity", ascending=False)
    )

    total = sku_volume["total_quantity"].sum()
    sku_volume["cumulative_pct"] = (
        sku_volume["total_quantity"].cumsum() / total * 100
    ).round(2)

    return sku_volume.head(n).reset_index(drop=True)
